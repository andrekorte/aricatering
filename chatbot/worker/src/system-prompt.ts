import { SYSTEM_RULES } from "./system-rules";

/**
 * The system prompt, in two blocks.
 *
 * The split is deliberate. The rules and the knowledge base are identical on
 * every request, so the cache breakpoint goes at the end of the second block:
 * the first turn of a conversation writes the prefix to cache, and every turn
 * after it re-reads roughly 2,000 tokens at cache rates instead of full input
 * rates. Only the conversation itself is billed as fresh input.
 *
 * Both halves are generated from source files (chatbot/system-rules.md and
 * the site's own content) by tools/build_kb.py, so neither can drift from
 * what the website says.
 */
export function buildSystem(knowledgeBase: string) {
  return [
    { type: "text" as const, text: SYSTEM_RULES },
    {
      type: "text" as const,
      text: "# KNOWLEDGE BASE\n\nEverything you are allowed to state as fact:\n\n" + knowledgeBase,
      cache_control: { type: "ephemeral" as const },
    },
  ];
}
