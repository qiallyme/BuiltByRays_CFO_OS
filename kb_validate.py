#!/usr/bin/env python3
import argparse, sys, re
from pathlib import Path

BLOCKING = 0
WARNINGS = 0

FRONTMATTER_RE = re.compile(r"^---\s*[\s\S]*?\n---\s*", re.M)
TITLE_RE = re.compile(r"^title\s*:\s*.+$", re.M)
TAGS_RE = re.compile(r"^tags\s*:\s*\[.*\]\s*$", re.M)

def err(msg):
    global BLOCKING
    print(f"[ERROR] {msg}")
    BLOCKING += 1

def warn(msg):
    global WARNINGS
    print(f"[WARN]  {msg}")
    WARNINGS += 1

def has_ctrl_chars(text):
    # flag control chars except \t \n \r
    for ch in text:
        if ord(ch) < 32 and ch not in ("\t", "\n", "\r"):
            return True
    return False

def validate_md(md: Path, base: Path):
    rel = md.relative_to(base)
    txt = md.read_text(encoding="utf-8", errors="ignore")

    if len(txt.strip()) == 0:
        warn(f"{rel}: file is empty")

    m = FRONTMATTER_RE.match(txt)
    if not m:
        # our TOC script should have inserted this already
        err(f"{rel}: missing frontmatter block (--- ... ---)")
        return

    fm = m.group(0)

    if not TITLE_RE.search(fm):
        err(f"{rel}: missing 'title:' in frontmatter")

    if not TAGS_RE.search(fm):
        warn(f"{rel}: missing 'tags:' in frontmatter")

    body = txt[m.end():].strip()

    # Optional: ensure a top-level heading exists somewhere after FM
    if not re.search(r"(?m)^#\s+.+", body):
        warn(f"{rel}: no H1 heading found in body")

    if has_ctrl_chars(txt):
        warn(f"{rel}: contains control characters")

    # For index.md, nudge: keep it as the page anchor for its folder
    if md.name.lower() == "index.md":
        # encourage short summary up top
        if len(body) < 10:
            warn(f"{rel}: index.md has very little content; add a short summary")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"[ERROR] Base not found: {base}")
        sys.exit(2)

    for md in base.rglob("*.md"):
        if ".obsidian" in md.as_posix():
            continue
        validate_md(md, base)

    if BLOCKING > 0:
        print(f"\n{BLOCKING} blocking error(s), {WARNINGS} warning(s).")
        sys.exit(2)
    elif WARNINGS > 0:
        print(f"\n0 blocking errors, {WARNINGS} warning(s).")
        sys.exit(1)
    else:
        print("\nAll good. 0 errors, 0 warnings.")
        sys.exit(0)

if __name__ == "__main__":
    main()
