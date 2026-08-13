#!/usr/bin/env python3
"""Run the assistant's test cases against a running chat endpoint.

    python3 chatbot/evals/run.py                       # local dev server
    python3 chatbot/evals/run.py --endpoint https://ari-chat.<you>.workers.dev/chat
    python3 chatbot/evals/run.py --only allergy --verbose

Why this exists: a prompt is code with no compiler. Every rule in
chatbot/system-rules.md was added because of a specific way this assistant
could hurt the business, and nothing except a test says whether the rule still
holds after the next edit. Cases are graded on substrings, which is blunt -
see the note at the top of cases.json about which assertions to trust.

Exits non-zero if anything fails, so it can be wired into CI later.

Costs real money in live mode: about 20 short conversations per run.
"""

import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_ENDPOINT = "http://127.0.0.1:8000/chat"

GREEN, RED, DIM, YELLOW, OFF = "\033[32m", "\033[31m", "\033[2m", "\033[33m", "\033[0m"


def ask(endpoint, messages, timeout=90):
    """POST a conversation, read our SSE format back, return the reply text."""
    req = urllib.request.Request(
        endpoint,
        data=json.dumps({"messages": messages}).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        resp = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as err:
        raise RuntimeError("HTTP %s: %s" % (err.code, err.read().decode()[:200])) from None
    except urllib.error.URLError as err:
        raise RuntimeError("could not reach %s (%s)" % (endpoint, err.reason)) from None

    out = []
    for raw in resp:
        line = raw.decode("utf-8").strip()
        if not line.startswith("data:"):
            continue
        event = json.loads(line[5:])
        if event.get("type") == "text":
            out.append(event["text"])
        elif event.get("type") == "error":
            raise RuntimeError(event.get("message", "stream error"))
    return "".join(out).strip()


def grade(reply, expect):
    """Returns a list of failure descriptions - empty means the case passed."""
    low = reply.lower()
    fails = []

    for needle in expect.get("all", []):
        if needle.lower() not in low:
            fails.append("missing %r" % needle)

    anys = expect.get("any", [])
    if anys and not any(n.lower() in low for n in anys):
        fails.append("none of %s present" % json.dumps(anys))

    for needle in expect.get("none", []):
        if needle.lower() in low:
            fails.append("FORBIDDEN %r present" % needle)

    cap = expect.get("max_words")
    if cap and len(reply.split()) > cap:
        fails.append("%d words, cap is %d" % (len(reply.split()), cap))

    return fails


def run_case(endpoint, case):
    """Replays the turns, keeping the assistant's real replies in the history."""
    messages = []
    reply = ""
    for turn in case["turns"]:
        messages.append({"role": "user", "content": turn})
        reply = ask(endpoint, messages)
        messages.append({"role": "assistant", "content": reply})
    return reply, grade(reply, case["expect"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--endpoint", default=os.environ.get("CHAT_ENDPOINT", DEFAULT_ENDPOINT))
    ap.add_argument("--only", help="substring match on case id")
    ap.add_argument("--verbose", action="store_true", help="print every reply")
    args = ap.parse_args()

    cases = json.load(open(os.path.join(HERE, "cases.json")))["cases"]
    if args.only:
        cases = [c for c in cases if args.only in c["id"]]
    if not cases:
        sys.exit("no cases matched --only %s" % args.only)

    print("endpoint: %s" % args.endpoint)
    print("cases:    %d\n" % len(cases))

    failed = []
    for case in cases:
        try:
            reply, fails = run_case(args.endpoint, case)
        except RuntimeError as err:
            print("%sERROR%s %-24s %s" % (RED, OFF, case["id"], err))
            failed.append(case["id"])
            continue

        mark = "%sPASS%s" % (GREEN, OFF) if not fails else "%sFAIL%s" % (RED, OFF)
        print("%s  %-24s %srule %s%s" % (mark, case["id"], DIM, case["rule"], OFF))
        if fails:
            failed.append(case["id"])
            for f in fails:
                print("      %s%s%s" % (YELLOW, f, OFF))
            print("      %swhy: %s%s" % (DIM, case["why"], OFF))
        if fails or args.verbose:
            print("      %s%s%s\n" % (DIM, re.sub(r"\s+", " ", reply)[:400], OFF))

    print("\n%d/%d passed" % (len(cases) - len(failed), len(cases)))
    if failed:
        print("failed: %s" % ", ".join(failed))
        sys.exit(1)


if __name__ == "__main__":
    main()
