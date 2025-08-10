#!/usr/bin/env python3
"""
KB Restructure — folders-first with undo (Windows-safe)

Fixes:
- Avoid double-planning top-level index.md (special-case only).
- Safe apply: skip ops whose src no longer exists (after prior moves).

Usage:
  python kb_restructure.py                          # dry run
  python kb_restructure.py --apply                  # apply
  python kb_restructure.py --apply --wrap-all-md    # stricter wrapping
  python kb_restructure.py --undo ".logs\...\ops.json"
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"
LOG_DIR_NAME = ".logs"

SAFE_MD_NAMES_TO_KEEP = {"readme"}

def slugify_folder(name: str) -> str:
    m = re.match(r"^([A-Za-z0-9]+)\s*[-_.]\s*(.*)$", name.strip())
    if m:
        prefix, tail = m.group(1), m.group(2)
        raw = f"{prefix}-{tail}"
    else:
        raw = name
    raw = raw.replace("™", "TM")
    raw = re.sub(r"[^A-Za-z0-9]+", "-", raw)
    raw = re.sub(r"-{2,}", "-", raw).strip("-")
    return raw[:120]

def want_wrap(dir_path: Path, md_path: Path, aggressive: bool) -> bool:
    items = [p for p in dir_path.iterdir()]
    subdirs = [p for p in items if p.is_dir()]
    files = [p for p in items if p.is_file()]

    # handled via special-case; don't decide here
    if dir_path == BASE_DIR and md_path.name.lower() == "index.md":
        return False

    if aggressive:
        if len(subdirs) == 0 and len([f for f in files if f.suffix.lower() == ".md"]) == 1:
            return False
        return True

    if len(subdirs) > 0:
        return True

    mds_here = [f for f in files if f.suffix.lower() == ".md"]
    if len(mds_here) > 1:
        return True

    base = md_path.stem.lower()
    if len(mds_here) == 1 and base in SAFE_MD_NAMES_TO_KEEP:
        return False

    return False

def plan_moves(base_dir: Path, aggressive: bool):
    ops = []

    # Special case: wrap top-level index.md into /index/index.md
    top_index = base_dir / "index.md"
    if top_index.exists():
        target_dir = base_dir / "index"
        target_file = target_dir / "index.md"
        if not target_file.exists():
            ops.append({
                "op": "wrap_md_into_folder",
                "src": str(top_index),
                "make_dir": str(target_dir),
                "dst": str(target_file),
                "note": "Wrap top-level index.md"
            })

    # Walk and plan everything else
    for dirpath, dirnames, filenames in os.walk(base_dir):
        d = Path(dirpath)

        # Skip hidden/system dirs
        if any(part.startswith(".") for part in d.parts if part != "."):
            continue

        md_files = [Path(dirpath) / f for f in filenames if f.lower().endswith(".md")]
        if not md_files:
            continue

        for md in md_files:
            # Skip top-level index.md (already handled)
            if d == base_dir and md.name.lower() == "index.md":
                continue

            # If already index.md inside a leaf folder, leave it
            if md.name.lower() == "index.md" and d != base_dir:
                continue

            if want_wrap(d, md, aggressive):
                stem = md.stem
                if stem.lower() in ("index", "readme"):
                    folder_name = slugify_folder(d.name)
                else:
                    folder_name = slugify_folder(stem)

                target_dir = d / folder_name
                suffix = 1
                while target_dir.exists() and (target_dir / "index.md").exists():
                    suffix += 1
                    target_dir = d / f"{folder_name}-{suffix}"

                target_file = target_dir / "index.md"
                ops.append({
                    "op": "wrap_md_into_folder",
                    "src": str(md),
                    "make_dir": str(target_dir),
                    "dst": str(target_file),
                    "note": f"Wrap {md.name} into {target_dir.name}/index.md"
                })

    return ops

def do_apply(ops, dry_run=True):
    rollback = []
    for op in ops:
        src = Path(op["src"])
        dst_dir = Path(op["make_dir"])
        dst = Path(op["dst"])

        if not src.exists():
            print(f"[SKIP] Source missing (already moved?): {src}")
            continue

        if dry_run:
            print(f"[DRY] {op['note']}: {src} -> {dst}")
            continue

        created_dir = False
        if not dst_dir.exists():
            dst_dir.mkdir(parents=True, exist_ok=True)
            created_dir = True

        final_dst = dst
        if final_dst.exists():
            base = final_dst.stem
            ext = final_dst.suffix
            n = 1
            while final_dst.exists():
                final_dst = dst_dir / f"{base}-{n}{ext}"
                n += 1

        shutil.move(str(src), str(final_dst))

        rollback.append({
            "undo": "move_back",
            "from": str(final_dst),
            "to": str(src),
            "remove_dir_if_empty": str(dst_dir) if created_dir else None
        })
        print(f"[OK]  {op['note']}: {src} -> {final_dst}")

    return rollback

def save_log(base_dir: Path, ops, rollback):
    log_dir = base_dir / LOG_DIR_NAME
    log_dir.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = log_dir / f"{stamp}_ops.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({"base_dir": str(base_dir), "timestamp": stamp, "ops": ops, "rollback": rollback}, f, indent=2)
    return path

def load_log(log_path: Path):
    with open(log_path, "r", encoding="utf-8") as f:
        return json.load(f)

def do_undo(log_path: Path):
    data = load_log(log_path)
    rb = data.get("rollback", [])
    print(f"Undoing {len(rb)} actions from {Path(log_path).name} ...")
    for step in reversed(rb):
        if step.get("undo") == "move_back":
            src = Path(step["from"])
            dst = Path(step["to"])
            try:
                dst.parent.mkdir(parents=True, exist_ok=True)
                if src.exists():
                    shutil.move(str(src), str(dst))
                    print(f"[UNDO] {src} -> {dst}")
                else:
                    print(f"[SKIP] Missing {src}")
            finally:
                maybe = step.get("remove_dir_if_empty")
                if maybe:
                    p = Path(maybe)
                    try:
                        if p.exists() and p.is_dir() and not any(p.iterdir()):
                            p.rmdir()
                    except Exception:
                        pass
    print("Undo complete.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Restructure KB to folders-first, with undo.")
    ap.add_argument("--base", default=DEFAULT_BASE, help="Base content directory")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default is dry run)")
    ap.add_argument("--wrap-all-md", action="store_true", help="Aggressive: wrap ANY loose .md")
    ap.add_argument("--undo", default=None, help="Undo using a previous log file path")
    args = ap.parse_args()

    global BASE_DIR
    BASE_DIR = Path(args.base).resolve()

    if args.undo:
        logp = Path(args.undo).resolve()
        if not logp.exists():
            print(f"Log not found: {logp}")
            sys.exit(1)
        do_undo(logp)
        sys.exit(0)

    if not BASE_DIR.exists():
        print(f"Base not found: {BASE_DIR}")
        sys.exit(1)

    print(f"Scanning: {BASE_DIR}")
    ops = plan_moves(BASE_DIR, aggressive=args.wrap_all_md)

    if not ops:
        print("Nothing to do. Structure already folders-first. 💅")
        sys.exit(0)

    for op in ops:
        print(f"- {op['note']}: {op['src']} -> {op['dst']}")

    if not args.apply:
        print("\nDRY RUN complete. Add --apply to execute. Or use --wrap-all-md for stricter wrapping.")
        sys.exit(0)

    rollback = do_apply(ops, dry_run=False)
    log_path = save_log(BASE_DIR, ops, rollback)
    print(f"\nAll set. Log saved to: {log_path}")
    print(f'Undo command:\n  python kb_restructure.py --undo "{log_path}"')

