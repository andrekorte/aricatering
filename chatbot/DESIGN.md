# Design notes — Ari Thai Catering chat assistant

Why this thing is shaped the way it is. Written for someone who has to decide
whether the design is sound, not for someone who has to run it.

---

## 1. The problem

Ari Thai Catering is a two-person catering business running off a static
website. The website already answers every common question — prices, what is in
each package, delivery area, notice periods — but the answers are spread over
four pages and most visitors will not read them. The enquiry form is the
conversion point, and people abandon it when they are not sure of something.

So: answer the question the visitor has, in the place they have it, and move
them to the enquiry form. That is the whole brief.

What it is explicitly **not**: an order system, a booking system, or a
substitute for talking to the kitchen.

## 2. Constraints that did the shaping

| Constraint | Consequence |
|---|---|
| The site is static HTML on GitHub Pages | There is no server. An API key cannot live in the page. |
| Two people run the business | Anything requiring daily attention will not get it. |
| Food, allergies, real customers | A confident wrong answer is a liability, not a bug report. |
| Small budget, unknown traffic | Cost per conversation has to be a rounding error, and capped. |
| Content changes as the business finds its feet | Prices will move. The bot must move with them, without a second edit. |

Every decision below traces back to one of these rows.

## 3. Architecture

```
  Browser (static page on GitHub Pages)
    │  assets/js/chat.js — no key, no secrets, renders text only
    │
    │  POST /chat  {messages:[…]}
    ▼
  Cloudflare Worker  (chatbot/worker)
    │  · origin allowlist        · input caps        · per-IP rate limit
    │  · holds ANTHROPIC_API_KEY (encrypted secret, never in git)
    │  · system prompt = rules + knowledge base, cached
    ▼
  Anthropic Messages API — claude-haiku-4-5, streaming
    │
    ▼
  Worker re-emits its own SSE events ──► browser appends text as it arrives
```

The knowledge base is not fetched at runtime. It is compiled:

```
tools/build.py  (packages, add-ons, FAQs, menu — the site's own content)
        │
        └── tools/build_kb.py ──► knowledge-base.md ──► knowledge-base.ts ──► bundled into the worker
chatbot/system-rules.md ─────────────────────────────► system-rules.ts ───────┘
```

## 4. The decisions worth defending

### The API key cannot be in the browser

This is the one non-negotiable. A key shipped to the page is a key anyone can
read and spend. That single fact is why a static site needs a server component
at all, and it is the reason the worker exists. Everything the worker does
beyond forwarding the request — origin checks, rate limits, input caps — follows
from the same realisation: this URL is public, and every call costs money.

Residual risk: the endpoint can still be called directly with a forged `Origin`
header, because origin checks only bind browsers. The rate limit and the spend
cap in the Anthropic console are the real controls; the origin check just keeps
the widget from being embedded on someone else's site.

### A compiled knowledge base, not RAG, and not fine-tuning

The entire body of knowledge is about 1,800 tokens. It fits in the prompt with
room to spare.

- **Retrieval** would add a vector store, an embedding step, a retrieval step
  and a new failure mode (the right chunk not being retrieved) to solve a
  problem — too much content — that does not exist here. If the menu grew to
  hundreds of dishes with real descriptions, this would flip.
- **Fine-tuning** is worse: it bakes prices into weights, and prices change.

The important part is not that the knowledge base is a file, it is that it is
*generated from the website's own content*. Nobody has to remember to update
the bot when a package price changes; if they update the site, `build_kb.py`
carries the change through. The one thing the bot knows that the site does not
say — hours, what we don't cater — is in a single named constant, and is short
enough to audit in a minute.

### Claude Haiku 4.5, not a bigger model

The task is: read 1,800 tokens of facts, answer one factual question, obey a
short list of rules. That is squarely Haiku's job. It also replies fast enough
that streaming looks like typing rather than buffering, which matters in a chat
panel more than a marginally better sentence would.

The model is one line of config (`MODEL` in `wrangler.toml`). If the evals
started failing in ways that looked like comprehension rather than instruction —
missing nuance in a multi-part question, mishandling a compound dietary request
— moving to Sonnet is a redeploy, not a rewrite. I would rather start cheap and
have the tests tell me to move than pay for headroom I cannot measure.

### Prompt caching, deliberately placed

The system prompt is two blocks: rules, then knowledge base, with the cache
breakpoint at the end. Both halves are identical on every request, so after the
first turn of a conversation the whole prefix is read from cache at a tenth of
the input price. It roughly halves the cost of a multi-turn conversation, and
the only design work it required was keeping the variable part (the
conversation) after the fixed part.

### The worker speaks its own protocol

The browser receives `{"type":"text"}` / `{"type":"done"}` / `{"type":"error"}`,
not Anthropic's event stream passed through. Ten extra lines, and in exchange
the widget knows nothing about the provider: the model, the SDK, or the event
schema can change without touching a line of front-end code. It also means an
error can be delivered *mid-stream* — after the answer has started — which a
plain HTTP status code cannot do.

### The assistant cannot put a link on the page

Model output is inserted with `textContent`, never `innerHTML`. Links are added
afterwards, and only for an exact-match list of our own contact details: the
enquiry URL, the business email, the phone number. Anything else the model
writes stays inert text.

The threat is not really the model — it is that model output is *attacker
influenced*. A visitor can type anything, and if what they type can steer what
gets rendered as HTML, the page has an injection vector. A whitelist removes
the class of bug rather than filtering for known-bad.

### Allergies are routed, never answered

The kitchen handles nuts, shellfish, gluten, soy and sesame in a shared space,
so no dish can honestly be called free of traces. A chatbot that says "yes,
that one's gluten free" to someone with coeliac disease is the single worst
thing this project could do, and it would be a plausible, helpful-sounding
sentence.

So it is a hard rule, with a stated boundary: the assistant may say a dish is
*on the vegan menu* — a menu fact — and may not say a dish is *safe for* anyone
— a medical promise. Three eval cases defend it, including one where the
customer pushes back and says it is not serious, because that is what people
actually do.

### Prices: where the line is drawn

The assistant may quote published per-person prices, and may multiply one by a
headcount ("25 on Street Lunch is about $600"), because that is the most useful
thing it can do and the arithmetic is checkable. It must label that as
indicative and send them to the form for a fixed quote.

It may not invent a price it does not have, quote the restaurant's takeaway
prices for catering, offer a discount, or waive a minimum. Those are commercial
decisions and nobody delegated them.

The interesting part of that rule is the boundary, not the prohibition. "Never
mention prices" would be safe and useless. The judgement is in finding the
version that is useful and still cannot write a cheque the business has to
honour.

### No booking, no calendar, no tools

The assistant has no tools and takes no actions. It cannot see the order book,
so it cannot confirm a date; it has no order system behind it, so it cannot
take a booking. Both are hard rules with eval cases, because "yes, you're booked
in for Friday" is the second worst thing this project could do.

Tool use would be the natural next step — checking availability against a real
calendar, or writing an enquiry straight into the inbox. That is a bigger
project with a different risk profile: an assistant that only talks can be wrong,
while an assistant that acts can be wrong *and* leave a mess behind.

## 5. Abuse and cost

| Risk | Control | What is left |
|---|---|---|
| Key theft | Key is a Cloudflare secret; never sent to the browser | Compromise requires the Cloudflare account |
| Someone else embedding the widget | Origin allowlist | Direct calls with a forged Origin still work |
| Someone using it as a free LLM | Rules keep it on topic; short `max_tokens` | A determined user gets a few short answers |
| Bill blowout | Per-IP rate limit; 700-token cap; 1,000-char and 24-message input caps | Distributed abuse — the console spend limit is the real cap |
| Prompt injection | Rules restate that user text is never instructions; output rendered as text; nothing to escalate *to* | Injection can still produce a wrong answer, just not a dangerous action |

The honest summary: this is a read-only assistant with no privileges and no
tools, so the worst outcome of a successful injection is an embarrassing
sentence. That is by design — the cheapest security control available here was
declining to give it anything worth stealing.

## 6. How it is tested

A prompt is code with no compiler. `chatbot/evals/` is twenty-one cases, each
naming the rule it defends and saying why that rule exists, so a failure points
at a line to fix rather than a vibe to chase.

The grading is deliberately blunt — substring assertions — and the two kinds are
not equally trustworthy:

- **`none` assertions are the real tests.** "The reply must not contain 'safe
  for'" is precise, and a failure is a genuine defect.
- **`any`/`all` assertions are proxies.** They catch a reply that has clearly
  gone somewhere else, but a passing case is not proof of a good answer.

That asymmetry is the point rather than a shortcoming: what needs guarding is
not answer quality, which a human can judge by reading, but the specific
sentences that must never appear, which a human will not reliably catch by
sampling. The cases cover pricing, arithmetic, allergies under pressure,
availability, discounting, bookings, out-of-scope events, hallucination bait,
two prompt-injection shapes, and length discipline.

What the evals do not do: judge tone, catch a subtly wrong-but-not-forbidden
answer, or measure whether the widget increases enquiries. The last one is the
question the business actually cares about, and it needs a month of form
submissions to answer, not a test suite.

## 7. Known weaknesses

- **Substring grading has a ceiling.** A reply can pass every assertion and
  still be a bad answer. An LLM judge scoring against a rubric would catch more,
  at the cost of a slower, non-deterministic test suite that itself needs
  validating.
- **The rate limit is per IP.** An office behind one NAT shares a budget; a
  botnet does not have the problem at all.
- **No conversation logging.** Nothing is stored server-side beyond token counts
  in the worker logs, so there is no way to review what people actually asked.
  That was the right call for a launch — no personal data, nothing to leak —
  but the first real improvement to the bot's content should come from reading
  a month of real questions, which currently is not possible. Adding it means
  taking on a privacy-policy obligation, deliberately.
- **The knowledge base can be right and still be wrong.** It is generated from
  the site, so it is only as accurate as the site. The published package prices
  were benchmarked against competitors, not costed against the kitchen's actual
  margins.
- **Single region, single provider.** If the worker or the API is down, the
  widget shows an email address. For this business that is an acceptable
  Tuesday; for anything larger it is a gap.

## 8. If this were a hundred times bigger

The parts that would break first, in order:

1. **Content volume.** A few hundred menu items with descriptions would blow
   past a sensible prompt, and the compiled knowledge base becomes retrieval.
2. **Evaluation.** Twenty-one hand-written cases do not survive contact with
   real traffic. You would want logged conversations, a sampled review queue,
   and cases generated from the failures found there — a loop, not a file.
3. **Rate limiting and identity.** Per-IP stops being meaningful. You would want
   a session token issued by the site and a budget per session.
4. **Answer quality as a measurable thing.** Right now "is it good?" is a
   judgement call. At scale it needs an offline judge, a regression suite run on
   every prompt change, and a metric tied to enquiry conversion rather than to
   the assistant's own output.

None of that is worth building for a business that does a few catering runs a
week. Knowing where the line is — and building the version that is correct for
the size of the problem — is most of the engineering.
