#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sync_quartz_kb.py — Curate a Quartz-ready content tree from a big vault.

- Mirrors the exact folder hierarchy from SOURCE to DEST.
- Copies only approved types (.md, images, pdf by default).
- For non-approved or too-large files, creates a .link.md stub that points
  to the original file (file:/// URL), leaving the original in place.
- Optional normalization of directory and/or file names in DEST only.
"""

import argparse
import os
import re
import shutil
import sys
from pathlib import Path
from urllib.parse import quote

DEFAULT_APPROVED = [
    ".md", ".markdown",
    ".pdf",
    ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp",
]

def human_bytes(n: int) -> str:
    for unit in ("B","KB","MB","GB","TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.0f} {unit}"
        n /= 1024

def normalize_component(name: str, max_len: int = 80, is_file: bool = True) -> str:
    """Slug-ish normalize: spaces->'-', strip forbidden chars, collapse dashes, trim, limit length."""
    # split name/ext only if it's a file
    base, ext = (os.path.splitext(name) if is_file else (name, ""))
    # replace whitespace with dash
    base = re.sub(r"\s+", "-", base)
    # remove forbidden characters
    base = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "", base)
    # collapse multiple dashes
    base = re.sub(r"-{2,}", "-", base).strip("-.")
    # truncate
    if len(base) > max_len:
        base = base[:max_len].rstrip("-.")

    if is_file:
        return f"{base}{ext.lower()}"
    else:
        return base.lower()

def ensure_dir(p: Path, dry_run: bool):
    if not p.exists():
        if dry_run:
            print(f"MKDIR   {p}")
        else:
            p.mkdir(parents=True, exist_ok=True)

def unique_path(p: Path, dry_run: bool) -> Path:
    if dry_run or not p.exists():
        return p
    stem, ext = p.stem, p.suffix
    i = 2
    while True:
        alt = p.with_name(f"{stem}-{i}{ext}")
        if not alt.exists():
            return alt
        i += 1

def file_uri(p: Path) -> str:
    # pathlib.as_uri() handles Windows drive letters correctly
    try:
        return p.resolve().as_uri()
    except Exception:
        # fallback: manual file:/// with URL-encoded path
        path_str = str(p.resolve()).replace("\\", "/")
        if not path_str.startswith("/"):
            path_str = "/" + path_str  # file:///C:/...
        return "file://" + quote(path_str)

def map_dest_dir(rel_dir: Path, dest_root: Path, normalize_dirs: bool) -> Path:
    parts = [normalize_component(part, is_file=False) if normalize_dirs else part
             for part in rel_dir.parts if part not in (".", "")]
    out = dest_root
    for part in parts:
        out = out / part
    return out

def map_dest_file(rel_file: Path, dest_root: Path, normalize_dirs: bool, normalize_files: bool) -> Path:
    rel_dir = rel_file.parent
    rel_name = rel_file.name
    dest_dir = map_dest_dir(rel_dir, dest_root, normalize_dirs)
    dest_name = normalize_component(rel_name, is_file=True) if normalize_files else rel_name
    return dest_dir / dest_name

def write_link_stub(dest_dir: Path, src_file: Path, keep_base_name_for_stub: bool,
                    normalize_files: bool, is_large: bool, dry_run: bool):
    base = src_file.stem
    if normalize_files:
        base = normalize_component(base, is_file=False)
    if not keep_base_name_for_stub:
        base = normalize_component(base, is_file=False)
    stub = dest_dir / f"{base}.link.md"
    stub = unique_path(stub, dry_run)

    uri = file_uri(src_file)
    size_note = " (large file stub)" if is_large else ""
    content = f"""---
title: "{src_file.name}{size_note}"
source_path: "{src_file}"
size_bytes: {src_file.stat().st_size}
ext: "{src_file.suffix.lower()}"
tags: [external, stub]
---

**Link stub.** Original stays in your local vault.

- **Open locally:** [{uri}]({uri})
- **Folder:** {src_file.parent}
- **Size:** {src_file.stat().st_size:,} bytes
"""

    if dry_run:
        print(f"STUB    {stub}  ->  {src_file}")
    else:
        ensure_dir(dest_dir, dry_run=False)
        stub.write_text(content, encoding="utf-8")

def curate(source_root: Path,
           dest_root: Path,
           approved_exts: list[str],
           large_file_bytes: int,
           normalize_dirs: bool,
           normalize_files: bool,
           keep_empty_dirs: bool,
           keep_base_name_for_stub: bool,
           dry_run: bool):
    if not source_root.exists():
        print(f"ERROR: Source does not exist: {source_root}", file=sys.stderr)
        sys.exit(1)

    print(f"Source: {source_root}")
    print(f"Dest:   {dest_root}")
    ensure_dir(dest_root, dry_run)

    # Pre-create full directory tree
    all_dirs = [source_root] + [Path(dp) for dp, dn, fn in os.walk(source_root) for _ in [None]]
    # The above comprehension yields each directory many times; dedupe:
    uniq_dirs: set[Path] = set()
    for dp, _, _ in os.walk(source_root):
        uniq_dirs.add(Path(dp))
    for d in sorted(uniq_dirs):
        rel = d.relative_to(source_root)
        dest_dir = dest_root if str(rel) == "." else map_dest_dir(rel, dest_root, normalize_dirs)
        if keep_empty_dirs:
            ensure_dir(dest_dir, dry_run)

    approved = {e.lower() for e in approved_exts}

    copied = 0
    stubbed = 0
    processed = 0

    for dirpath, _, filenames in os.walk(source_root):
        rel_dir = Path(dirpath).relative_to(source_root)
        dest_dir = map_dest_dir(rel_dir, dest_root, normalize_dirs)
        for name in filenames:
            processed += 1
            src = Path(dirpath) / name
            ext = src.suffix.lower()
            is_approved = ext in approved
            is_large = src.stat().st_size > large_file_bytes

            dest = map_dest_file(rel_dir / name, dest_root, normalize_dirs, normalize_files)
            dest = unique_path(dest, dry_run)

            if is_approved and not is_large:
                if dry_run:
                    print(f"COPY    {src.relative_to(source_root)}")
                else:
                    ensure_dir(dest_dir, dry_run=False)
                    shutil.copy2(src, dest)
                copied += 1
            else:
                write_link_stub(dest_dir, src, keep_base_name_for_stub, normalize_files, is_large, dry_run)
                stubbed += 1

            # keep the console alive on huge trees
            if processed % 1000 == 0:
                print(f"...processed {processed} files (copied {copied}, stubbed {stubbed})")

    print(f"Done. Copied: {copied}, Stubbed: {stubbed}, Total: {processed}")
    if not dry_run:
        print("Preview with Quartz: npx quartz build --serve (from your repo root)")

def parse_args():
    p = argparse.ArgumentParser(description="Curate a Quartz-ready content tree from a large vault.")
    p.add_argument("--source", default=r"Q:\GoogleDriveStream\QiVault\quartz\content",
                   help="Source vault content root")
    p.add_argument("--dest", default=r"C:\Users\codyr\Documents\Github\EmpowerQNow713\QiVaultInternal\quartz\content",
                   help="Destination Quartz repo content root")
    p.add_argument("--approved", nargs="*", default=DEFAULT_APPROVED,
                   help=f"Approved extensions (default: {', '.join(DEFAULT_APPROVED)})")
    p.add_argument("--large-bytes", type=int, default=25 * 1024 * 1024,
                   help="Files larger than this will be stubbed even if approved (default 25MB)")
    p.add_argument("--normalize-dirs", action="store_true",
                   help="Normalize directory names in DEST")
    p.add_argument("--no-normalize-files", action="store_true",
                   help="Do NOT normalize file names (default is to normalize files)")
    p.add_argument("--keep-empty-dirs", action="store_true",
                   help="Create empty directories in DEST to mirror SOURCE")
    p.add_argument("--no-keep-empty-dirs", dest="keep_empty_dirs", action="store_false")
    p.set_defaults(keep_empty_dirs=True)
    p.add_argument("--keep-base-stub-name", action="store_true",
                   help="Keep original base name for stub files (adds .link.md)")
    p.add_argument("--dry-run", action="store_true", help="Plan only; make no changes")
    return p.parse_args()

def main():
    args = parse_args()
    source = Path(args.source)
    dest = Path(args.dest)

    curate(
        source_root=source,
        dest_root=dest,
        approved_exts=args.approved,
        large_file_bytes=args.large_bytes,
        normalize_dirs=args.normalize_dirs,
        normalize_files=not args.no_normalize_files,
        keep_empty_dirs=args.keep_empty_dirs,
        keep_base_name_for_stub=args.keep_base_stub_name,
        dry_run=args.dry_run,
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        sys.exit(130)
