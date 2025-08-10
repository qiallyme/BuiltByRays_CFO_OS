#!/usr/bin/env python3
# Fix mixed tag syntax + normalize frontmatter across all MDs.
import re, sys
from pathlib import Path

BASE = Path(r".\content").resolve()

NUMERIC_WHITELIST = {"1099","401k","10k","10-q"}
BLOCKLIST = {"index","readme","md","markdown","content"}

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p,t): p.write_text(t, encoding="utf-8")

def slug_title(name: str) -> str:
    name = re.sub(r"^([A-Za-z0-9]+)\s*[-_.]\s*", "", name)  # drop A- / 01-
    name = (name or "").replace("TM","™").replace("_"," ").replace("-"," ")
    name = re.sub(r"\s+"," ", name).strip()
    return name[:1].upper() + name[1:] if name else "Untitled"

def derive_title(md: Path, base: Path) -> str:
    rel = md.relative_to(base)
    return slug_title(rel.parent.name if md.name.lower()=="index.md" else md.stem)

def normalize_tag(t: str) -> str:
    t = str(t or "").strip().lower().replace("_","-").replace(" ", "-")
    t = re.sub(r"-{2,}", "-", t)
    t = re.sub(r"[^a-z0-9-]", "", t)
    if t in BLOCKLIST: return ""
    if t.isdigit() and t not in NUMERIC_WHITELIST: return ""
    return t

def parse_frontmatter(txt: str):
    if not txt.strip().startswith("---"): return None, txt
    end = txt.find("\n---", 3)
    if end == -1: return None, txt
    fm = txt[:end+4]; body = txt[end+4:]
    return fm, body

def collect_multiline_list(lines, start_idx):
    """Collect indented '- item' lines following a key line."""
    items = []
    i = start_idx + 1
    while i < len(lines):
        line = lines[i]
        if re.match(r"^\s*-\s+.+$", line):
            items.append(re.sub(r"^\s*-\s+", "", line).strip())
            i += 1
            continue
        if re.match(r"^\s*[A-Za-z0-9_-]+\s*:", line):  # next key
            break
        if line.strip()=="":
            i += 1
            continue
        break
    return items, i

def fix_file(p: Path, base: Path) -> bool:
    txt = read(p)
    fm, body = parse_frontmatter(txt)
    if fm is None:
        # inject minimal FM
        title = derive_title(p, base)
        fm = f"---\ntitle: {title}\n---"
        new = fm + "\n\n" + txt.lstrip()
        if new != txt:
            write(p, new)
            return True
        return False

    # split lines to edit keys robustly
    lines = fm.strip().splitlines()
    # ensure starts/ends with ---
    if lines and lines[0].strip() == "---": lines = lines[1:]
    if lines and lines[-1].strip() == "---": lines = lines[:-1]

    out = []
    tags_found_inline = []
    tags_found_block = []
    i = 0
    while i < len(lines):
        line = lines[i]

        # title fix
        m_title = re.match(r"^title\s*:\s*(.*)$", line, flags=re.I)
        if m_title:
            title_val = m_title.group(1).strip()
            if title_val.lower() in ("", "index"):  # fix bogus title
                title_val = derive_title(p, base)
            out.append(f"title: {title_val}")
            i += 1
            continue

        # tags inline: tags: [...]
        m_tags_inline = re.match(r"^tags\s*:\s*\[(.*)\]\s*$", line, flags=re.I)
        if m_tags_inline:
            inside = m_tags_inline.group(1)
            candidates = [t.strip().strip(",") for t in inside.split(",")]
            tags_found_inline.extend([t for t in candidates if t])
            i += 1
            # also collect any following block-style items and skip them
            block_items, j = collect_multiline_list(lines, i-1)
            tags_found_block.extend(block_items)
            i = j
            continue

        # tags key (block style to follow)
        m_tags_key = re.match(r"^tags\s*:\s*$", line, flags=re.I)
        if m_tags_key:
            # collect subsequent '- x' lines
            items, j = collect_multiline_list(lines, i)
            tags_found_block.extend(items)
            i = j
            continue

        out.append(line)
        i += 1

    # merge tags
    merged = []
    seen = set()
    for t in (tags_found_inline + tags_found_block):
        nt = normalize_tag(t)
        if nt and nt not in seen:
            merged.append(nt); seen.add(nt)

    # rebuild FM
    # ensure we have title
    if not any(l.lower().startswith("title:") for l in out):
        out.insert(0, f"title: {derive_title(p, base)}")

    if merged:
        out = [l for l in out if not l.lower().startswith("tags:")]
        out.append(f"tags: [{', '.join(merged)}]")

    new_fm = "---\n" + "\n".join(out) + "\n---"
    new_txt = new_fm + txt[txt.find("\n---", 3)+4:]

    if new_txt != txt:
        write(p, new_txt)
        return True
    return False

def main():
    base = BASE
    changed = 0
    for md in base.rglob("*.md"):
        if ".obsidian" in md.as_posix(): continue
        if fix_file(md, base):
            print(f"[FIX] {md}")
            changed += 1
    print(f"Done. Fixed {changed} files.")

if __name__ == "__main__":
    main()
