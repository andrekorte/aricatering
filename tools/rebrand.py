#!/usr/bin/env python3
"""Change the business name and/or domain across the whole site in one go.

    python3 tools/rebrand.py --name "Ari Thai Street Food Catering" \
                             --short "Ari" \
                             --domain arithaistreetfoodcatering.com.au

Updates site.config.json, rewrites every generated HTML file, sitemap.xml
and robots.txt, and refreshes CNAME. Any argument may be omitted to leave
that value unchanged. Use --dry-run to see what would change first.
"""

import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CFG_PATH = os.path.join(ROOT, "site.config.json")

# Files that carry the name/domain and are safe to rewrite in place.
TARGET_EXT = (".html", ".xml", ".txt", ".md")
SKIP_DIRS = {".git", "assets", "tools", "node_modules"}


def iter_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            if fn.endswith(TARGET_EXT):
                yield os.path.join(dirpath, fn)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", help='Full business name, e.g. "Ari Thai Street Food Catering"')
    ap.add_argument("--short", help='Short name used in the header/footer logo lockup, e.g. "Ari Thai"')
    ap.add_argument("--domain", help="Bare domain, no scheme, e.g. arithaicatering.com.au")
    ap.add_argument("--email", help="Contact and form-target email address")
    ap.add_argument("--dry-run", action="store_true", help="Report changes without writing anything")
    args = ap.parse_args()

    if not any([args.name, args.short, args.domain, args.email]):
        ap.error("nothing to do - pass at least one of --name, --short, --domain, --email")

    cfg = json.load(open(CFG_PATH, encoding="utf-8"))

    swaps = []
    if args.name and args.name != cfg["business_name"]:
        swaps.append((cfg["business_name"], args.name))
        cfg["business_name"] = args.name
    if args.short and args.short != cfg["short_name"]:
        swaps.append((cfg["short_name"], args.short))
        cfg["short_name"] = args.short
    if args.domain and args.domain != cfg["domain"]:
        swaps.append((cfg["domain"], args.domain))
        cfg["domain"] = args.domain
    if args.email and args.email != cfg["email"]:
        swaps.append((cfg["email"], args.email))
        cfg["email"] = args.email
        cfg["form_endpoint"] = "https://formsubmit.co/" + args.email

    if not swaps:
        print("Nothing changed - the new values match the current config.")
        return

    # Longest first, so "Ari Thai Catering" is replaced before "Ari Thai".
    swaps.sort(key=lambda s: len(s[0]), reverse=True)
    print("Replacing:")
    for old, new in swaps:
        print("  %-40s -> %s" % (old, new))
    print()

    touched = 0
    for path in iter_files():
        original = open(path, encoding="utf-8").read()
        text = original
        for old, new in swaps:
            text = text.replace(old, new)
        if text != original:
            touched += 1
            rel = os.path.relpath(path, ROOT)
            print("  %s" % rel)
            if not args.dry_run:
                open(path, "w", encoding="utf-8").write(text)

    if args.domain:
        cname = os.path.join(ROOT, "CNAME")
        if os.path.exists(cname) or not args.dry_run:
            print("  CNAME")
            if not args.dry_run:
                open(cname, "w", encoding="utf-8").write(cfg["domain"] + "\n")

    if not args.dry_run:
        with open(CFG_PATH, "w", encoding="utf-8") as fh:
            json.dump(cfg, fh, indent=2, ensure_ascii=False)
            fh.write("\n")
        print("\nUpdated %d files plus site.config.json." % touched)
        print("Re-run `python3 tools/build.py` if you also changed page content.")
    else:
        print("\nDry run - %d files would change. Nothing written." % touched)


if __name__ == "__main__":
    sys.exit(main())
