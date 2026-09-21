#!/usr/bin/env python3
"""Run the site and the chat endpoint locally.

    python3 chatbot/dev-server.py            # canned replies, no API key needed
    ANTHROPIC_API_KEY=sk-ant-... python3 chatbot/dev-server.py   # the real model

Then open http://127.0.0.1:8000/ - the chat widget is injected into every page
as it is served, so nothing in the committed HTML has to change to try it.

This is a development stand-in for chatbot/worker, not a second
implementation of it: it reads the same system rules and the same knowledge
base, so prompt changes can be tried here in a second instead of through a
deploy. It has none of the worker's protections (no origin check, no rate
limit) and must never be exposed to the internet.
"""

import json
import os
import re
import sys
import urllib.error
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PORT = int(os.environ.get("PORT", "8000"))
API_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
MODEL = os.environ.get("MODEL", "claude-haiku-4-5")
MAX_TOKENS = 700

CFG = json.load(open(os.path.join(ROOT, "site.config.json")))
EMAIL = CFG["email"]

SNIPPET = (
    "<script>window.ARI_CHAT=%s;</script>\n"
    '<script src="/assets/js/chat.js" defer></script>\n'
) % json.dumps({
    "endpoint": "/chat",
    "email": CFG["email"],
    "phone": CFG["phone"],
    "site": "https://%s" % CFG["domain"],
})


def system_blocks():
    rules = open(os.path.join(ROOT, "chatbot", "system-rules.md"), encoding="utf-8").read()
    rules = re.sub(r"^<!--.*?-->\s*", "", rules, flags=re.S).strip()
    kb = open(os.path.join(ROOT, "chatbot", "knowledge-base.md"), encoding="utf-8").read()
    return [
        {"type": "text", "text": rules},
        {
            "type": "text",
            "text": "# KNOWLEDGE BASE\n\nEverything you are allowed to state as fact:\n\n" + kb,
            "cache_control": {"type": "ephemeral"},
        },
    ]


# --------------------------------------------------------------------------
# Stub mode - enough to exercise the widget without spending anything
# --------------------------------------------------------------------------

STUBS = [
    (r"\b(price|cost|how much|\$)\b",
     "Our catering is $19.99 per person for food only, $26.99 with dessert and $32.99 "
     "with dessert and a drink. Those prices are plus GST. Email %s "
     "with your date and numbers and we will confirm the order." % EMAIL),
    (r"\b(allerg|nut|peanut|coeliac|celiac|shellfish)\b",
     "We can give you ingredient information, but our kitchen prepares everything in one "
     "place with shared equipment, so we cannot guarantee any dish is free of traces. "
     "Please confirm any allergies and dietary requirements with our staff when you order."),
    (r"\b(vegan|vegans|vegetarian|gluten)\b",
     "Yes, vegan, vegetarian and gluten-free choices are available. Please confirm any "
     "allergies and dietary requirements with our staff when you order."),
    (r"\b(deliver|delivery|suburb|area|where|pick ?up)\b",
     "Delivery is free within 5 km of the Brisbane CBD for orders of 10 or more, between "
     "9.00am and 6.00pm. Further out, delivery starts from $15. Pick-up from the "
     "restaurant is also available."),
    (r"\b(notice|lead time|when|book|order)\b",
     "Please order at least 48 hours ahead, with a minimum of 10 people. Email %s "
     "and we will confirm and invoice." % EMAIL),
]

STUB_DEFAULT = (
    "This is the local stub, so I only have a few canned answers. Set ANTHROPIC_API_KEY "
    "and restart to talk to the real assistant."
)


def stub_reply(question):
    for pattern, answer in STUBS:
        if re.search(pattern, question, re.I):
            return answer
    return STUB_DEFAULT


# --------------------------------------------------------------------------

class Handler(SimpleHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)

    def log_message(self, fmt, *args):
        if "/chat" in (args[0] if args else ""):
            sys.stderr.write("  chat: %s\n" % (args[0]))

    # -- static, with the widget injected -----------------------------------

    def do_GET(self):
        path = self.translate_path(self.path.split("?")[0])
        if os.path.isdir(path):
            path = os.path.join(path, "index.html")
        if path.endswith(".html") and os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                body = fh.read().replace("</body>", SNIPPET + "</body>").encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()

    # -- the chat endpoint --------------------------------------------------

    def do_POST(self):
        if self.path.split("?")[0] != "/chat":
            self.send_error(404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            payload = json.loads(self.rfile.read(length) or b"{}")
            messages = payload["messages"]
            assert isinstance(messages, list) and messages
        except Exception:
            self.send_error(400, "Bad request")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        try:
            if API_KEY:
                self.live(messages)
            else:
                self.stub(messages)
            self.emit({"type": "done"})
        except Exception as exc:  # noqa: BLE001 - dev server, report anything
            sys.stderr.write("  chat failed: %r\n" % (exc,))
            self.emit({"type": "error", "message": str(exc)[:200]})
        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()

    def emit(self, obj):
        data = ("data: %s\n\n" % json.dumps(obj)).encode("utf-8")
        self.wfile.write(b"%x\r\n" % len(data) + data + b"\r\n")
        self.wfile.flush()

    def stub(self, messages):
        import time
        for word in stub_reply(messages[-1]["content"]).split(" "):
            self.emit({"type": "text", "text": word + " "})
            time.sleep(0.02)

    def live(self, messages):
        body = json.dumps({
            "model": MODEL,
            "max_tokens": MAX_TOKENS,
            "system": system_blocks(),
            "messages": [{"role": m["role"], "content": m["content"]} for m in messages],
            "stream": True,
        }).encode("utf-8")
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/messages",
            data=body,
            headers={
                "content-type": "application/json",
                "x-api-key": API_KEY,
                "anthropic-version": "2023-06-01",
            },
        )
        try:
            resp = urllib.request.urlopen(req, timeout=60)
        except urllib.error.HTTPError as err:
            raise RuntimeError("API %s: %s" % (err.code, err.read().decode()[:300])) from None

        usage = {}
        for raw in resp:
            line = raw.decode("utf-8").strip()
            if not line.startswith("data:"):
                continue
            event = json.loads(line[5:])
            if event.get("type") == "content_block_delta" and event["delta"].get("type") == "text_delta":
                self.emit({"type": "text", "text": event["delta"]["text"]})
            elif event.get("type") == "message_start":
                usage = event["message"].get("usage", {})
            elif event.get("type") == "message_delta":
                usage.update(event.get("usage", {}))
        if usage:
            sys.stderr.write("  usage: %s\n" % json.dumps(usage))


if __name__ == "__main__":
    mode = "live (%s)" % MODEL if API_KEY else "stub (no ANTHROPIC_API_KEY set)"
    print("Ari Thai Catering dev server")
    print("  mode:  %s" % mode)
    print("  site:  http://127.0.0.1:%d/" % PORT)
    print("  chat:  POST http://127.0.0.1:%d/chat\n" % PORT)
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()
