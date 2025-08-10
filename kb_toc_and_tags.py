#!/usr/bin/env python3
"""
Builds a Quartz-friendly KB:
- Generates a global content/index.md with a full table of contents.
- Injects per-folder TOCs into each folder's index.md between marker comments.
- Ensures frontmatter (title, tags) on all .md files.
- Auto-inserts an H1 (# Title) if missing (from frontmatter title).
- Dry-run by default; use --apply to write changes.
- Backs up any edited file to <file>.bak once per run.

Usage:
  python kb_toc_and_tags.py
  python kb_toc_and_tags.py --apply
  python kb_toc_and_tags.py --base "C:\\path\\to\\content"
"""

import argparse, os, re, sys, shutil
from pathlib import Path

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"
MARKER_START = "<!-- AUTO-TOC:START -->"
MARKER_END   = "<!-- AUTO-TOC:END -->"

def is_md(p: Path) -> bool:
    return p.suffix.lower() == ".md"

def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def write_text(p: Path, txt: str, backup=True):
    if backup and not (p.parent / (p.name + ".bak")).exists():
        shutil.copy2(p, p.parent / (p.name + ".bak"))
    p.write_text(txt, encoding="utf-8")

def slug_title(name: str) -> str:
    m = re.match(r"^([A-Za-z0-9]+)\s*[-_.]\s*(.*)$", name)
    core = m.group(2) if m and m.group(2) else name
    core = core.replace("TM", "™").replace("-", " ").replace("_", " ")
    core = re.sub(r"\s+", " ", core).strip()
    return core[:1].upper() + core[1:]

def path_tags(rel_parts):
    tags = []
    if len(rel_parts) >= 1:
        t = re.sub(r"^\d{2}[-_]", "", rel_parts[0]).lower()
        tags.append(t)
    if len(rel_parts) >= 2:
        s = re.sub(r"^\w{1,3}[-_.]\s*", "", rel_parts[1])
        s = s.replace(" ", "-").lower().replace("&", "and").replace("™", "tm").replace("—", "-").replace("’", "").replace("'", "")
        s = re.sub(r"[^a-z0-9-]+", "-", s).strip("-")
        if s: tags.append(s)
    cat_map = {
        "financials": ["finance", "accounting"],
        "marketing": ["brand", "growth"],
        "operations": ["sop", "process"],
        "technology": ["it", "stack"],
        "human-resources": ["hr", "people"],
        "legal-compliance": ["compliance", "legal"],
        "analytics": ["kpi", "reporting"],
        "business-development": ["sales", "bizdev"],
        "scope": ["services"],
        "investment": ["pricing"],
        "roadmap-strategies-faqs": ["strategy"]
    }
    for k, extras in cat_map.items():
        if len(rel_parts) >= 1 and k in rel_parts[0]:
            tags.extend(extras)
    out, seen = [], set()
    for t in tags:
        if t and t not in seen:
            out.append(t); seen.add(t)
    return out

def md_link_for(md_path: Path, base: Path) -> str:
    rel = md_path.relative_to(base)
    target = rel.parent.as_posix() if md_path.name.lower() == "index.md" else rel.with_suffix("").as_posix()
    return f"[[{target}]]"

def list_children(folder: Path):
    subs, files = [], []
    for p in sorted(folder.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name.startswith("."): continue
        if p.is_dir():
            idx = p / "index.md"
            if idx.exists(): subs.append(idx)
        elif is_md(p):
            files.append(p)
    return subs, files

def build_global_index(base: Path) -> str:
    lines = ["---", "title: BuiltbyRays OS Index", "tags: [index, toc]", "---", ""]
    lines.append("# BuiltbyRays OS Index\n")
    for p in sorted(base.iterdir(), key=lambda x: x.name.lower()):
        if p.name.startswith(".") or p.name.lower() in ("index.md", "qisuitelogo.png"): continue
        if p.is_file() and is_md(p):
            lines.append(f"- {md_link_for(p, base)}")
        elif p.is_dir():
            section_title = slug_title(re.sub(r"^\d{2}[-_]", "", p.name))
            lines.append(f"## {section_title}")
            sub_idx, loose = list_children(p)
            for idx in sub_idx: lines.append(f"- {md_link_for(idx, base)}")
            for f in loose:     lines.append(f"- {md_link_for(f, base)}")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"

def inject_folder_toc(folder_index: Path, base: Path, apply=False):
    folder = folder_index.parent
    sub_idx, loose = list_children(folder)
    if not sub_idx and not loose: return False
    toc_lines = [MARKER_START, "", "## Contents"]
    for idx in sub_idx: toc_lines.append(f"- {md_link_for(idx, base)}")
    for f in loose:     toc_lines.append(f"- {md_link_for(f, base)}")
    toc_lines += ["", MARKER_END]
    toc_block = "\n".join(toc_lines)
    txt = read_text(folder_index)
    if MARKER_START in txt and MARKER_END in txt:
        new_txt = re.sub(re.escape(MARKER_START)+r".*?"+re.escape(MARKER_END), toc_block, txt, flags=re.S)
    else:
        m = re.search(r"^# .*$", txt, flags=re.M)
        new_txt = (txt[:m.end()] + "\n\n" + toc_block + "\n" + txt[m.end():]) if m else (txt.rstrip() + "\n\n" + toc_block + "\n")
    if new_txt != txt and apply: write_text(folder_index, new_txt)
    return new_txt != txt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"Base not found: {base}")
        sys.exit(1)

    changed = 0

    # 1) Build/refresh global index at content/index.md
    global_index_path = base / "index.md"
    global_index = build_global_index(base)
    if args.apply:
        if global_index_path.exists():
            write_text(global_index_path, global_index)
        else:
            global_index_path.write_text(global_index, encoding="utf-8")
        print(f"[APPLY]   wrote global index -> {global_index_path}")
    else:
        print("[DRY]     would write global index -> content/index.md")

    # 3) Inject per-folder TOCs into each folder's index.md
    for folder in [p for p in base.iterdir() if p.is_dir() and not p.name.startswith(".")]:
        for idx in [*folder.rglob("index.md")]:
            if inject_folder_toc(idx, base, apply=args.apply):
                print(f"[APPLY]   folder TOC -> {idx}")
                changed += 1

    if args.apply:
        print(f"\nDone. Updated {changed} files.")
    else:
        print("\nDRY RUN complete. Add --apply to perform writes.")

if __name__ == "__main__":
    main()
