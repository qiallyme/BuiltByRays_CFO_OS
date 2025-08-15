#!/usr/bin/env python3
"""
Fix duplicate H1 headings that match frontmatter titles.
This prevents Quartz from showing the title twice on pages.
"""

import re, sys, argparse, yaml
from pathlib import Path

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"

FM_TOP_RE = re.compile(r"^\ufeff?\s*---\s*\n(.*?)\n---\s*\n?", flags=re.S)
H1_RE = re.compile(r"^(?:\s*)#\s+(.+?)\s*$", re.M)

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, t): p.write_text(t, encoding="utf-8")

def split_frontmatter(txt: str):
    """Extract frontmatter and body."""
    m = FM_TOP_RE.match(txt)
    if not m:
        return {}, txt
    
    raw = m.group(1)
    try:
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict): 
            data = {}
    except Exception:
        data = {}
    
    body = txt[m.end():]
    return data, body

def normalize_title(title: str) -> str:
    """Normalize title for comparison (remove quotes, extra spaces, etc)."""
    if not title:
        return ""
    # Remove quotes and normalize whitespace
    title = re.sub(r'^["\']|["\']$', '', title.strip())
    title = re.sub(r'\s+', ' ', title)
    return title.lower()

def remove_duplicate_h1(fm_title: str, body: str) -> str:
    """Remove H1 that matches frontmatter title."""
    if not fm_title:
        return body
    
    normalized_fm_title = normalize_title(fm_title)
    lines = body.splitlines()
    new_lines = []
    removed_first_h1 = False
    
    for line in lines:
        # Check if this is an H1
        h1_match = H1_RE.match(line)
        if h1_match and not removed_first_h1:
            h1_content = h1_match.group(1).strip()
            normalized_h1 = normalize_title(h1_content)
            
            # If H1 matches frontmatter title, skip it
            if normalized_h1 == normalized_fm_title:
                removed_first_h1 = True
                continue
        
        new_lines.append(line)
    
    return "\n".join(new_lines)

def main():
    ap = argparse.ArgumentParser(description="Remove duplicate H1 headings that match frontmatter titles")
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"[ERR] base not found: {base}")
        sys.exit(1)

    changed = 0
    for p in base.rglob("*.md"):
        if ".obsidian" in p.as_posix():
            continue

        txt = read(p)
        fm, body = split_frontmatter(txt)
        
        # Get frontmatter title
        fm_title = fm.get("title", "")
        if not fm_title:
            continue
        
        # Remove duplicate H1
        new_body = remove_duplicate_h1(fm_title, body)
        
        if new_body != body:
            new_txt = txt[:txt.find("---", 3) + 4] + new_body
            if args.apply:
                write(p, new_txt)
                changed += 1
                print(f"Fixed: {p.relative_to(base)}")
            else:
                print(f"Would fix: {p.relative_to(base)}")

    print(f"[OK] Fixed {changed} files." if args.apply else f"[DRY] Would fix {changed} files. Use --apply to write.")

if __name__ == "__main__":
    try:
        import yaml
    except Exception:
        print("[ERR] Missing dependency 'pyyaml'. Run: pip install pyyaml")
        sys.exit(1)
    main()
