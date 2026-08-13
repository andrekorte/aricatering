# Ari Thai Catering — chat assistant

A small AI assistant on the website that answers catering questions from the
site's own content, and hands anything it should not answer to a human.

`DESIGN.md` explains why it is built this way. This file explains how to run it.

```
chatbot/
  system-rules.md        what the assistant may and may not do  <- edit this
  knowledge-base.md      what it knows                          <- generated
  dev-server.py          run the site + a local chat endpoint
  evals/                 test cases and a runner
  worker/                the Cloudflare Worker that holds the API key
assets/js/chat.js        the widget
assets/css/site.css      its styles (bottom of the file)
tools/build_kb.py        regenerates the knowledge base from the site content
```

## Try it now, without an account

```sh
python3 chatbot/dev-server.py
```

Open <http://127.0.0.1:8000/>. The widget is injected into every page as it is
served. With no API key set you get canned replies — enough to check the
interface, not the assistant.

To talk to the real model, set a key (from
<https://console.anthropic.com/> → API keys) and restart:

```sh
ANTHROPIC_API_KEY=sk-ant-... python3 chatbot/dev-server.py
```

This is the loop for working on the prompt: edit `system-rules.md`, restart,
ask it something awkward.

## Going live

Three steps. Budget half an hour the first time.

### 1. An Anthropic API account

<https://console.anthropic.com/> → sign up → **Billing** → add a payment method
and a small credit balance. Then **Settings → Limits** and set a monthly spend
limit — $20 is plenty and it is the real backstop against a surprise bill.
Create an API key and keep it somewhere safe.

### 2. Deploy the worker

The website is static files on GitHub Pages, which cannot keep a secret:
anything it sends the browser is readable by anyone. So the API key lives in a
Cloudflare Worker, and the browser talks to that.

```sh
cd chatbot/worker
npm install
npx wrangler login              # opens a browser, free Cloudflare account is fine
npx wrangler secret put ANTHROPIC_API_KEY    # paste the key when prompted
npx wrangler deploy
```

The last command prints the URL, something like
`https://ari-chat.<your-account>.workers.dev`. Check it:

```sh
curl https://ari-chat.<your-account>.workers.dev/health
```

### 3. Turn the widget on

Put the worker's URL, with `/chat` on the end, into `site.config.json`:

```json
"chat_endpoint": "https://ari-chat.<your-account>.workers.dev/chat",
```

Then rebuild and push:

```sh
python3 tools/build.py
git add -A && git commit -m "Turn on the chat assistant" && git push
```

Setting `chat_endpoint` back to `""` and rebuilding removes the widget
completely — no script tag, no launcher. That is the off switch.

## Running the tests

With the dev server or the worker running:

```sh
python3 chatbot/evals/run.py                                  # local
python3 chatbot/evals/run.py --endpoint https://.../chat      # deployed
python3 chatbot/evals/run.py --only allergy --verbose
```

Every case names the rule it defends, so a failure tells you which line of
`system-rules.md` to look at. Run this after any change to the rules or the
site's prices — it costs a few cents.

## Changing what it knows

Never edit `chatbot/knowledge-base.md`. It is generated from the website, so
the assistant cannot quote a price the site does not show:

```
tools/build.py content (packages, add-ons, FAQs, menu)
              │
              ▼
      tools/build_kb.py ──► chatbot/knowledge-base.md
                       └──► chatbot/worker/src/knowledge-base.ts
```

- **A price, a package, an FAQ** → edit `tools/build.py`, then run
  `python3 tools/build.py && python3 tools/build_kb.py`.
- **A fact that is not on any page** (opening hours, what we don't cater) →
  `OPERATIONAL_FACTS` in `tools/build_kb.py`.
- **Behaviour** → `chatbot/system-rules.md`, then `python3 tools/build_kb.py`.

Any of those needs a redeploy of the worker (`npx wrangler deploy`) to take
effect on the live site.

## What it costs

Running on Claude Haiku 4.5, with the fixed part of the prompt cached:

| | |
|---|---|
| First message of a conversation | ~$0.004 |
| Each message after that | ~$0.001 |
| A typical five-message conversation | about one cent |
| 500 conversations in a month | around $5 |

Cloudflare Workers' free tier (100,000 requests a day) covers this many times
over. The spend limit in the Anthropic console is what actually caps the bill.

## If something goes wrong

- **Widget not showing** — `chat_endpoint` is empty in `site.config.json`, or
  the site was not rebuilt after setting it. View source: no `chat.js`, no
  endpoint.
- **"Sorry, I could not reach the kitchen"** — the worker returned an error.
  `npx wrangler tail` streams its live logs.
- **403 from the worker** — the site's origin is not in `ALLOWED_ORIGINS` in
  `wrangler.toml`. Redeploy after changing it.
- **Answers are wrong or out of date** — regenerate the knowledge base and
  redeploy. The assistant only knows what is in it.
- **Turn it off in a hurry** — `npx wrangler delete` kills the endpoint, and the
  widget then shows its fallback message with the email address.
