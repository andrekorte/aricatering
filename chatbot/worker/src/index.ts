/**
 * Ari Thai Catering - chat endpoint.
 *
 * The website is static HTML on GitHub Pages, which means it cannot keep a
 * secret: anything shipped to the browser is public. This worker exists for
 * exactly one reason - to be the smallest possible piece of server that can
 * hold the Anthropic API key. Everything else it does (origin checks, rate
 * limiting, input caps) follows from the fact that this URL is public and
 * every request to it costs money.
 *
 * POST /chat  {"messages": [{"role": "user", "content": "..."}]}
 *   -> text/event-stream of {"type":"text","text":"..."} then {"type":"done"}
 *
 * Deploy: see chatbot/README.md
 */

import Anthropic from "@anthropic-ai/sdk";
import { buildSystem } from "./system-prompt";
import { KNOWLEDGE_BASE } from "./knowledge-base";

export interface Env {
  /** Set with: npx wrangler secret put ANTHROPIC_API_KEY */
  ANTHROPIC_API_KEY: string;
  /** Comma-separated origins allowed to call this worker. */
  ALLOWED_ORIGINS?: string;
  MODEL?: string;
  /** Optional [[unsafe.bindings]] rate limiter - the worker runs without it. */
  RATE_LIMITER?: { limit(opts: { key: string }): Promise<{ success: boolean }> };
}

/** Caps chosen so one abusive caller cannot run up a bill. */
const LIMITS = {
  /** ~12 exchanges. Longer conversations are re-enquiries, not questions. */
  messages: 24,
  /** Per message. A real catering question is a sentence or two. */
  chars: 1_000,
  /** Whole conversation, so a long history can't be padded to the cap. */
  totalChars: 8_000,
  /** Enough for a package breakdown, not enough for an essay. */
  maxTokens: 700,
};

const DEFAULT_MODEL = "claude-haiku-4-5";

type ChatMessage = { role: "user" | "assistant"; content: string };

// --------------------------------------------------------------------------
// HTTP plumbing
// --------------------------------------------------------------------------

function allowedOrigins(env: Env): string[] {
  return (env.ALLOWED_ORIGINS ?? "")
    .split(",")
    .map((o) => o.trim())
    .filter(Boolean);
}

/**
 * Returns the CORS headers for this request, or null if the origin is not
 * allowed. A same-origin or non-browser request (no Origin header) is allowed
 * through with no CORS headers - curl and the eval runner need to work.
 */
function corsHeaders(request: Request, env: Env): Record<string, string> | null {
  const origin = request.headers.get("Origin");
  if (!origin) return {};
  const list = allowedOrigins(env);
  // An unconfigured worker is open, so misconfiguration fails loudly in the
  // logs rather than silently serving the whole internet.
  if (list.length === 0) {
    console.warn("ALLOWED_ORIGINS is not set - accepting request from " + origin);
    return { "Access-Control-Allow-Origin": origin, Vary: "Origin" };
  }
  if (!list.includes(origin)) return null;
  return { "Access-Control-Allow-Origin": origin, Vary: "Origin" };
}

function json(body: unknown, status: number, headers: Record<string, string> = {}) {
  return new Response(JSON.stringify(body), {
    status,
    headers: { "Content-Type": "application/json", ...headers },
  });
}

// --------------------------------------------------------------------------
// Request validation
// --------------------------------------------------------------------------

/** Returns the messages, or a string describing why the body was rejected. */
function parseMessages(body: unknown): ChatMessage[] | string {
  if (typeof body !== "object" || body === null) return "Body must be a JSON object.";
  const raw = (body as { messages?: unknown }).messages;
  if (!Array.isArray(raw) || raw.length === 0) return "messages must be a non-empty array.";
  if (raw.length > LIMITS.messages) return "Conversation is too long.";

  const out: ChatMessage[] = [];
  let total = 0;
  for (const m of raw) {
    if (typeof m !== "object" || m === null) return "Each message must be an object.";
    const { role, content } = m as { role?: unknown; content?: unknown };
    if (role !== "user" && role !== "assistant") return "role must be user or assistant.";
    if (typeof content !== "string") return "content must be a string.";
    const text = content.trim();
    if (!text) return "content must not be empty.";
    if (text.length > LIMITS.chars) return "That message is too long - please shorten it.";
    total += text.length;
    if (total > LIMITS.totalChars) return "Conversation is too long.";
    out.push({ role, content: text });
  }
  // The API requires the turn order to end with the customer.
  if (out[out.length - 1].role !== "user") return "The last message must be from the user.";
  return out;
}

// --------------------------------------------------------------------------
// Worker
// --------------------------------------------------------------------------

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const cors = corsHeaders(request, env);
    if (cors === null) return json({ error: "Origin not allowed." }, 403);

    if (request.method === "OPTIONS") {
      return new Response(null, {
        status: 204,
        headers: {
          ...cors,
          "Access-Control-Allow-Methods": "POST, OPTIONS",
          "Access-Control-Allow-Headers": "Content-Type",
          "Access-Control-Max-Age": "86400",
        },
      });
    }

    const url = new URL(request.url);
    if (url.pathname === "/health") return json({ ok: true, model: env.MODEL ?? DEFAULT_MODEL }, 200, cors);
    if (url.pathname !== "/chat") return json({ error: "Not found." }, 404, cors);
    if (request.method !== "POST") return json({ error: "Use POST." }, 405, cors);

    if (env.RATE_LIMITER) {
      // CF-Connecting-IP is set by Cloudflare and cannot be spoofed by the
      // caller; it is the only identity we have for an anonymous widget.
      const key = request.headers.get("CF-Connecting-IP") ?? "unknown";
      const { success } = await env.RATE_LIMITER.limit({ key });
      if (!success) {
        return json(
          { error: "You're sending messages faster than we can answer. Try again in a minute." },
          429,
          cors,
        );
      }
    }

    let body: unknown;
    try {
      body = await request.json();
    } catch {
      return json({ error: "Invalid JSON." }, 400, cors);
    }

    const messages = parseMessages(body);
    if (typeof messages === "string") return json({ error: messages }, 400, cors);

    // Checked after validation so a misconfigured worker still reports a bad
    // request as a bad request: 4xx is about the caller, 5xx is about us.
    if (!env.ANTHROPIC_API_KEY) {
      console.error("ANTHROPIC_API_KEY is not set");
      return json({ error: "The assistant is not configured." }, 500, cors);
    }

    return streamReply(messages, env, cors);
  },
};

/**
 * Relays the model's output to the browser as our own small SSE format rather
 * than passing Anthropic's event stream straight through. The browser then
 * depends on this contract, not on the API's - the model, the provider or the
 * event schema can change without touching the widget.
 */
function streamReply(messages: ChatMessage[], env: Env, cors: Record<string, string>): Response {
  const client = new Anthropic({ apiKey: env.ANTHROPIC_API_KEY });
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      const send = (obj: unknown) => controller.enqueue(encoder.encode(`data: ${JSON.stringify(obj)}\n\n`));
      try {
        const reply = client.messages.stream({
          model: env.MODEL ?? DEFAULT_MODEL,
          max_tokens: LIMITS.maxTokens,
          system: buildSystem(KNOWLEDGE_BASE),
          messages,
        });

        for await (const event of reply) {
          if (event.type === "content_block_delta" && event.delta.type === "text_delta") {
            send({ type: "text", text: event.delta.text });
          }
        }

        const final = await reply.finalMessage();
        // Logged, not returned: usage is our business, not the caller's.
        console.log(
          JSON.stringify({
            model: final.model,
            input: final.usage.input_tokens,
            cache_read: final.usage.cache_read_input_tokens ?? 0,
            cache_write: final.usage.cache_creation_input_tokens ?? 0,
            output: final.usage.output_tokens,
            stop: final.stop_reason,
            turns: messages.length,
          }),
        );
        send({ type: "done" });
      } catch (err) {
        // The failure may land mid-sentence, so it goes down the stream as an
        // event; the widget shows the fallback contact details.
        console.error("chat failed", err);
        send({ type: "error", message: "Sorry - something went wrong at our end." });
      } finally {
        controller.close();
      }
    },
  });

  return new Response(stream, {
    headers: {
      ...cors,
      "Content-Type": "text/event-stream; charset=utf-8",
      "Cache-Control": "no-store",
      Connection: "keep-alive",
    },
  });
}
