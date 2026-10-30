"""Relative-link checker for Markdown/HTML files.

Usage: python3 scripts/check_links.py [ROOT]

Scans *.md and *.html under ROOT (skipping .git, node_modules, venvs and
templates/), ignores fenced code blocks, inline code and absolute/external URLs, and prints
one line per problem:
  BROKEN  <file> <line> <target>   target does not exist
  OUTSIDE <file> <line> <target>   target resolves outside ROOT
Exits 1 if anything was printed, else 0. Standard library only.
"""
import os
import re
import sys
import urllib.parse

PAT = re.compile(
    r'\]\(<?((?:[^()\s<>]|\([^()\s]*\))+)>?(?:\s+"[^"]*")?\)|(?:src|href)=["\']([^"\'\s]+)["\']'
)
OK_HTML = re.compile(r'^[\w./%~-][\w./%()~-]*(\.\w{1,5}|/)$')
SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "templates"}
EXTERNAL = ("http", "mailto:", "#", "tel:", "data:", "//", "{", "$", "javascript:")


def check(root: str) -> int:
    root = os.path.abspath(root)
    problems = 0
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            low = f.lower()
            if not low.endswith((".md", ".html")):
                continue
            p = os.path.join(dp, f)
            lines = open(p, encoding="utf-8", errors="replace").read().split("\n")
            fence = None
            for i, line in enumerate(lines, 1):
                st = line.lstrip()
                if low.endswith(".md") and (st.startswith("```") or st.startswith("~~~")):
                    tok = st[:3]
                    if fence is None:
                        fence = tok
                    elif tok == fence and st.strip() == tok:
                        fence = None
                    continue
                if fence:
                    continue
                if low.endswith(".md"):
                    line = re.sub(r"`[^`]*`", "", line)  # inline code is not a link
                for m in PAT.finditer(line):
                    u = m.group(1) or m.group(2)
                    if m.group(2) and not OK_HTML.match(u):
                        continue
                    if m.group(1) and low.endswith(".html"):
                        continue
                    if u.startswith(EXTERNAL):
                        continue
                    t = urllib.parse.unquote(u.split("#")[0].split("?")[0])
                    if not t:
                        continue
                    tp = os.path.normpath(
                        os.path.join(root, t.lstrip("/")) if t.startswith("/") else os.path.join(dp, t)
                    )
                    rel = os.path.relpath(p, root)
                    if not (tp == root or tp.startswith(root + os.sep)):
                        print("OUTSIDE", rel, i, u)
                        problems += 1
                    elif not os.path.exists(tp):
                        print("BROKEN", rel, i, u)
                        problems += 1
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(check(sys.argv[1] if len(sys.argv) > 1 else "."))
