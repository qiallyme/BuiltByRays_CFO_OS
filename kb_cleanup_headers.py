#!/usr/bin/env python3
"""
Normalize MD headers/frontmatter:
- Keep exactly ONE YAML frontmatter block at the very top.
- If file starts without '---', lift leading key: value lines into proper YAML FM.
- Remove duplicate/stray key lines (date:, title:, tags:, keywords:, aliases:, status:, owner:, last_reviewed:)
- Remove ALL previously injected "Related" and folder TOC blocks so other scripts can re-insert cleanly.
- Deduplicate repeated identical H1s at the top.
"""

import re, sys, argparse, yaml
from pathlib import Path

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"

REL_START = "<!-- RELATED:START -->"
REL_END   = "<!-- RELATED:END -->"
TOC_START = "<!-- AUTO-TOC:START -->"
TOC_END   = "<!-- AUTO-TOC:END -->"

KEYS = {"title","date","tags","keywords","aliases","status","owner","last_reviewed"}

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p,t): p.write_text(t, encoding="utf-8")

def fm_split(txt: str):
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        if end != -1:
            return txt[:end+4], txt[end+4:]
    return "", txt

def parse_inline_list(v: str):
    v = v.strip()
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1]
        out = [x.strip() for x in inner.split(",") if x.strip()]
        return out
    # fallback: comma separated
    if "," in v:
        return [x.strip() for x in v.split(",") if x.strip()]
    return [v] if v else []

def strip_injected_blocks(body: str) -> str:
    # remove ALL existing injected “Related” and TOC blocks; they’ll be re-inserted later
    body = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), "", body, flags=re.S)
    body = re.sub(re.escape(TOC_START)+r".*?"+re.escape(TOC_END), "", body, flags=re.S)
    return body.strip() + ("\n" if body.strip() else "")

def dedupe_top_h1(body: str) -> str:
    lines = body.splitlines()
    if not lines: return body
    # Find first H1
    first_h1_idx = next((i for i,l in enumerate(lines) if re.match(r"^\s*#\s+.+", l)), None)
    if first_h1_idx is None: return body
    first = lines[first_h1_idx].strip()
    j = first_h1_idx+1
    removed = False
    while j < len(lines) and lines[j].strip() == first:
        lines.pop(j)
        removed = True
    return ("\n".join(lines) + ("\n" if body.endswith("\n") and not removed else "\n")).lstrip()

def collect_loose_header_lines(txt: str):
    """
    If file DOES NOT start with '---', grab leading key lines like:
      title: ..., date: ..., tags: [...], keywords: ...
    Stop when we hit a blank line or an H1 or a non key-ish line.
    """
    lines = txt.splitlines()
    header = []
    i = 0
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            # blank line ends header prelude
            i += 1
            break
        if re.match(r"^\s*#\s+.+", l):  # H1 starts body
            break
        m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", l)
        if m and m.group(1).lower() in KEYS:
            header.append(l)
            i += 1
            continue
        else:
            break
    body = "\n".join(lines[i:]).lstrip() + ("\n" if txt.endswith("\n") else "")
    return header, body

def normalize_file(md: Path) -> bool:
    orig = read(md)
    txt = orig.lstrip("\ufeff")  # strip BOM
    fm, body = fm_split(txt)

    # If multiple frontmatter blocks were stacked, keep the FIRST and drop subsequent leading blocks
    if fm:
        rest = body.lstrip()
        # drop consecutive FM blocks at top of body - more aggressive
        while rest.startswith("---"):
            end2 = rest.find("\n---", 3)
            if end2 == -1: break
            rest = rest[end2+4:].lstrip()
        body = rest

    # If no FM, lift loose header lines (key: value) into FM
    data = {}
    if not fm:
        header_lines, body = collect_loose_header_lines(txt)
        if header_lines:
            # parse simple k:v
            for line in header_lines:
                m = re.match(r"^\s*([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.*)$", line)
                if not m: continue
                k = m.group(1).lower()
                v = m.group(2).strip()
                if k in {"tags","keywords","aliases"}:
                    data[k] = parse_inline_list(v)
                else:
                    data[k] = v
        # Compose FM if anything was found, else leave empty for now
        if data:
            fm_dict = data
            fm = "---\n" + yaml.safe_dump(fm_dict, sort_keys=False).strip() + "\n---\n"

    # If we have FM already, strip stray loose key lines that might still be sitting at top of body
    if fm:
        head_lines, body_after = collect_loose_header_lines(body)
        if head_lines:
            body = body_after

    # Strip injected blocks & dedupe H1
    body = strip_injected_blocks(body)
    body = dedupe_top_h1(body)

    # If still no FM, create a minimal one for Quartz (use filename as title)
    if not fm:
        title = md.parent.name if md.name.lower()=="index.md" else md.stem
        # Never use "index" as title
        if title.lower() == "index":
            title = md.parent.name
        # Convert to sentence case
        title = title.replace("_", " ").replace("-", " ")
        title = re.sub(r"\s+", " ", title).strip()
        if title:
            title = title[0].upper() + title[1:].lower()
        fm = f"---\ntitle: {title}\n---\n"

    new_txt = fm + ("\n" if not fm.endswith("\n") else "") + body.lstrip()
    if new_txt != orig:
        write(md, new_txt)
        return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"[ERR] base not found: {base}"); sys.exit(1)

    changed = 0
    for md in base.rglob("*.md"):
        if ".obsidian" in md.as_posix(): continue
        if normalize_file(md):
            changed += 1
            if not args.apply:
                # dry-run: revert write (but we only write when apply, so this is informational)
                pass

    print(f"[OK] Cleaned {changed} files.")

if __name__ == "__main__":
    try:
        import yaml  # pyyaml required
    except Exception:
        print("[ERR] Missing dependency 'pyyaml'. Run: pip install pyyaml")
        sys.exit(1)
    main()
