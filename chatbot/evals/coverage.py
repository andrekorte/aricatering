#!/usr/bin/env python3
"""Check that every rule has at least one test, and every test names a real rule.

    python3 chatbot/evals/coverage.py

RISKS.md says "a rule with no test is an aspiration". That is easy to write and
easy to let slide: rules get added in a hurry, and nothing notices that the new
one is defended by nothing. This does notice, and CI runs it.

It costs nothing - no API calls - so it runs before the eval suite and fails
fast.
"""

import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))

RULES_MD = os.path.join(ROOT, "chatbot", "system-rules.md")
RISKS_MD = os.path.join(ROOT, "chatbot", "RISKS.md")

# Rule 0 is not a numbered hard rule; it tags cases that defend the Style
# section (length, plain text, the handover). Allowed, and deliberately named.
STYLE_RULE = 0


def numbered_rules():
    text = open(RULES_MD, encoding="utf-8").read()
    body = text.split("# Style")[0]
    return {int(n) for n in re.findall(r"^(\d+)\.\s+[A-Z]", body, re.M)}


def main():
    rules = numbered_rules()
    if not rules:
        sys.exit("could not find any numbered rules in chatbot/system-rules.md")

    problems = []
    tested = set()
    for name in ("cases.json", "cases-th.json"):
        path = os.path.join(HERE, name)
        if not os.path.exists(path):
            problems.append("%s is missing but CI runs it" % name)
            continue
        for case in json.load(open(path, encoding="utf-8"))["cases"]:
            rule = case["rule"]
            tested.add(rule)
            if rule != STYLE_RULE and rule not in rules:
                problems.append("%s:%s names rule %s, which does not exist"
                                % (name, case["id"], rule))
            if not case.get("why"):
                problems.append("%s:%s has no 'why' - a case that cannot explain "
                                "itself cannot be reviewed" % (name, case["id"]))
            e = case["expect"]
            if not any(k in e for k in ("none", "none_regex", "all", "any", "any_regex", "max_chars")):
                problems.append("%s:%s asserts nothing" % (name, case["id"]))

    for rule in sorted(rules - tested):
        problems.append("rule %d has no eval case - it is an aspiration, not a control" % rule)

    # Every rule should also be reachable from a risk row, or it exists for no
    # stated reason. This is a soft check: it looks for "Rule N" in the register.
    risks = open(RISKS_MD, encoding="utf-8").read()
    for rule in sorted(rules):
        if not re.search(r"\bRule %d\b" % rule, risks):
            problems.append("rule %d is not referenced by any row in RISKS.md - "
                            "why does it exist?" % rule)

    if problems:
        print("Coverage problems:\n")
        for p in problems:
            print("  - %s" % p)
        sys.exit(1)

    print("%d numbered rules, all tested and all traceable to RISKS.md" % len(rules))
    print("cases tag rules: %s" % ", ".join(str(r) for r in sorted(tested)))


if __name__ == "__main__":
    main()
