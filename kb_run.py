#!/usr/bin/env python3
# kb_run.py
# One-stop: clean Markdown frontmatter/titles/tags, clean build Quartz, optional serve + push

import argparse, os, re, shutil, subprocess, sys, time, webbrowser
from pathlib import Path

# ---------- Config ----------
DEFAULT_BASE = Path("content")
MAX_TAGS = 5  # cap visible tags
PORT = 8080   # starting port for preview
# ----------------------------

# Try to load PyYAML nicely
try:
    import yaml
except Exception:
    print("[ERR] Missing dependency 'PyYAML'. Install with: pip install pyyaml")
    sys.exit(1)

# --------- Utilities --------
def read_text(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="ignore")

def write_text(p: Path, text: str, backup=True):
    if backup:
        bak = p.with_suffix(p.suffix + ".bak")
        if not bak.exists():
            try:
                shutil.copy2(p, bak)
            except Exception:
                pass
    p.write_text(text, encoding="utf-8")

def split_frontmatter(txt: str):
    """Return (fm_dict, body, fm_raw) – fm_dict is None if no FM."""
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        if end != -1:
            raw = txt[3:end]  # exclude the opening ---
            body = txt[end+4:]  # skip '\n---'
            try:
                data = yaml.safe_load(raw) or {}
                if not isinstance(data, dict):  # weird FM
                    data = {}
                return (data, body, raw)
            except Exception:
                # Broken YAML: treat as no FM, keep original
                return (None, txt, "")
    return (None, txt, "")

def slug_to_title_preserve_prefix(name: str) -> str:
    """
    Convert folder/file names to human title while preserving A-/B-/C- style prefixes as 'A. '.
    Examples:
      'A-Your-Details' -> 'A. Your Details'
      '01-scope'       -> '01 Scope'
      'foo_bar-baz'    -> 'Foo bar baz'
    """
    m = re.match(r"^([A-Za-z])[-_.]\s*(.+)$", name)
    if m:
        return f"{m.group(1).upper()}. {clean_words(m.group(2))}"

    m = re.match(r"^(\d{1,3})[-_.]\s*(.+)$", name)
    if m:
        return f"{m.group(1)} {clean_words(m.group(2))}"

    return clean_words(name)

def clean_words(s: str) -> str:
    s = s.replace("_", " ").replace("-", " ").strip()
    s = re.sub(r"\s+", " ", s)
    if not s: return s
    return s[0].upper() + s[1:]

def title_from_path(md_path: Path, base: Path) -> str:
    if md_path.name.lower() == "index.md":
        return slug_to_title_preserve_prefix(md_path.parent.name)
    return slug_to_title_preserve_prefix(md_path.stem)

HDR_RE = re.compile(r"(?m)^\s*#\s+(.+?)\s*$")

def first_h1(body: str) -> str | None:
    m = HDR_RE.search(body)
    return m.group(1).strip() if m else None

HEADER_LINE_RE = re.compile(r"^\s*[A-Za-z][\w-]*\s*:\s*.*$")
TAGS_OPEN_RE = re.compile(r"^\s*tags\s*:\s*(\[.*|\s*)$", re.I)

def strip_stray_header_blob(body: str) -> str:
    """
    Some files had a second raw “date:/title:/tags:” block inserted at the top of BODY.
    We remove a header-like blob if it appears before the first H1.
    """
    lines = body.splitlines()
    if not lines:
        return body

    # If a real H1 appears before any blob, bail.
    for i, ln in enumerate(lines[:40]):
        if ln.strip().startswith("# "):
            # check if a header-blob appears before this index
            blob_end = detect_header_blob_end(lines[:i])
            if blob_end is not None and blob_end > 0:
                return "\n".join(lines[blob_end:])
            return body

    # No early H1—still try to strip top blob
    blob_end = detect_header_blob_end(lines[:40])
    if blob_end is not None and blob_end > 0:
        return "\n".join(lines[blob_end:])
    return body

def detect_header_blob_end(head_lines: list[str]) -> int | None:
    """
    Look at the first ~N lines, and if we see 2+ 'key: value' lines,
    or a tags block, consider that a blob until a blank line (inclusive).
    Return the index (line number) right AFTER the blob to keep.
    """
    if not head_lines:
        return None
    saw_kv = 0
    in_tags_block = False
    for i, ln in enumerate(head_lines):
        if in_tags_block:
            # YAML list under tags:
            if ln.strip().startswith("- ") or ln.strip() == "":
                if ln.strip() == "":
                    return i + 1
                continue
            else:
                # tags block ended without blank—consider blob ended here
                return i
        if TAGS_OPEN_RE.match(ln):
            in_tags_block = True
            saw_kv += 1
            continue
        if HEADER_LINE_RE.match(ln):
            saw_kv += 1
            continue
        if ln.strip() == "" and saw_kv >= 2:
            return i + 1
        # If first non-blank is not a header-like line, no blob
        if i == 0 and not HEADER_LINE_RE.match(ln):
            return None
    # End of preview window
    if saw_kv >= 2:
        return len(head_lines)
    return None

def normalize_tags(value) -> list[str]:
    """Return deduped, normalized tags."""
    tags = []
    if value is None:
        return tags
    if isinstance(value, str):
        # handle comma separated or '#tag tag' style
        if value.strip().startswith("[") and value.strip().endswith("]"):
            try:
                parsed = yaml.safe_load(value)
                if isinstance(parsed, list):
                    tags = parsed
                else:
                    tags = [value]
            except Exception:
                tags = [value]
        else:
            # split by commas or spaces
            if "," in value:
                tags = [t.strip() for t in value.split(",")]
            else:
                tags = [t.strip().lstrip("#") for t in value.split()]
    elif isinstance(value, list):
        tags = value
    else:
        tags = [str(value)]

    cleaned = []
    seen = set()
    for t in tags:
        t = (t or "").strip()
        if not t:
            continue
        t = t.replace("_", "-")
        t = re.sub(r"\s+", "-", t)
        t = re.sub(r"[^a-zA-Z0-9\-]+", "", t)
        t = t.strip("-").lower()
        if t and t not in seen:
            cleaned.append(t); seen.add(t)
    return cleaned

def path_tags(md_path: Path, base: Path) -> list[str]:
    """Very conservative: derive at most 2 tags from path if none exist."""
    rel = md_path.relative_to(base)
    parts = list(rel.parts)
    out = []
    if len(parts) >= 1:
        out.append(simplify_tag(parts[0]))
    if len(parts) >= 2:
        out.append(simplify_tag(parts[1]))
    return [t for t in out if t][:2]

def simplify_tag(name: str) -> str:
    n = re.sub(r"^\d{1,3}[-_]", "", name)
    n = re.sub(r"^[A-Za-z]{1}[-_.]\s*", "", n)
    n = n.replace("&", "and")
    n = re.sub(r"[^a-zA-Z0-9]+", "-", n).strip("-").lower()
    return n

def ensure_h1_matches_title(body: str, title: str) -> str:
    """Insert an H1 if missing; otherwise keep the existing H1."""
    if HDR_RE.search(body):
        return body
    return f"# {title}\n\n{body.lstrip()}"

def dump_frontmatter_ordered(data: dict) -> str:
    """Dump FM with friendly ordering."""
    order = [
        "title","summary","description",
        "date","created","modified","last_reviewed",
        "status","owner",
        "tags","aliases",
        "publish","draft","enableToc",
        "permalink","lang","cssclasses","socialDescription","socialImage","image","cover"
    ]
    out = {}
    for k in order:
        if k in data:
            out[k] = data[k]
    for k,v in data.items():
        if k not in out:
            out[k] = v
    # YAML dump without nulls/empties
    cleaned = {k:v for k,v in out.items() if v not in (None, [], "", {})}
    return "---\n" + yaml.safe_dump(cleaned, sort_keys=False, allow_unicode=True).rstrip() + "\n---\n"

# ---------- Core: file fix ----------
def fix_markdown_file(md: Path, base: Path, max_tags=5, apply=False) -> bool:
    orig = read_text(md)
    fm, body, _ = split_frontmatter(orig)

    if fm is None:
        # no FM or broken FM — start fresh
        fm = {}
        body = orig

    # Strip stray “header-like” blob that may have been duplicated previously
    body = strip_stray_header_blob(body)

    # Title: prefer first H1; else derive from path; preserve A./01- prefixes
    h1 = first_h1(body)
    if h1:
        title = h1.strip()
    else:
        # If FM already has a suitable title (not "index"), keep it; else derive
        cur = str(fm.get("title") or "").strip()
        title = cur if cur and cur.lower() != "index" else title_from_path(md, base)
        body = ensure_h1_matches_title(body, title)

    fm["title"] = title

    # Tags: keep existing first, normalize, cap; if none, derive from path
    existing = []
    if "tags" in fm:
        existing = normalize_tags(fm.get("tags"))
    elif "tag" in fm:
        existing = normalize_tags(fm.get("tag"))

    if not existing:
        existing = path_tags(md, base)

    # Cap and set (prefer existing order)
    fm["tags"] = (existing[:max_tags]) if existing else []

    # Remove deprecated duplicates
    if "tag" in fm: del fm["tag"]
    if "keywords" in fm: del fm["keywords"]  # we’re not using keywords in Quartz

    new_txt = dump_frontmatter_ordered(fm) + body.lstrip("\n")

    if new_txt != orig and apply:
        write_text(md, new_txt)
        return True
    return new_txt != orig

# ---------- Build / Serve / Git ----------
def ensure_tools():
    for exe in ("node", "npx", "git"):
        if shutil.which(exe) is None:
            print(f"[ERR] Required tool not found on PATH: {exe}")
            sys.exit(1)

def clean_quartz_output():
    # Wipe public for a clean build
    if Path("public").exists():
        shutil.rmtree("public", ignore_errors=True)

def quartz_build():
    print("[build] quartz…")
    subprocess.run(["npx", "quartz", "build"], check=True)
    idx = Path("public/index.html")
    if idx.exists():
        shutil.copyfile(idx, Path("public/404.html"))

def serve_public(port=8080):
    print(f"[serve] http://localhost:{port}")
    # Try to find a free port between port..port+10
    chosen = None
    for p in range(port, port+11):
        if port_free(p):
            chosen = p
            break
    if chosen is None:
        chosen = port

    proc = subprocess.Popen(["npx", "serve", "public", "-l", str(chosen)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        webbrowser.open(f"http://localhost:{chosen}")
    except Exception:
        pass
    input("Press ENTER after you finish reviewing the site in your browser…\n")
    try:
        proc.terminate()
    except Exception:
        pass

def port_free(p: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.2)
        return s.connect_ex(("127.0.0.1", p)) != 0

def git_push(interactive=True, default_msg="KB: update content"):
    if not interactive:
        return
    ans = input("[git] Push changes to remote? (y/N): ").strip().lower()
    if ans != "y":
        print("[git] Skipping push.")
        return
    msg = input("[git] Commit message (blank = default): ").strip() or default_msg
    subprocess.run(["git", "add", "-A"], check=False)
    subprocess.run(["git", "commit", "-m", msg], check=False)
    subprocess.run(["git", "push"], check=False)

# ---------- Main ----------
def main():
    ap = argparse.ArgumentParser(description="Clean KB markdown, rebuild Quartz, optionally serve & push.")
    ap.add_argument("--base", default=str(DEFAULT_BASE), help="content root (default: ./content)")
    ap.add_argument("--apply", action="store_true", help="write changes (otherwise dry-run)")
    ap.add_argument("--limit-tags", type=int, default=MAX_TAGS, help="max tags to keep (default 5)")
    ap.add_argument("--no-build", action="store_true", help="skip Quartz build")
    ap.add_argument("--serve", action="store_true", help="start local preview after build")
    ap.add_argument("--no-push", action="store_true", help="do not prompt to push")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"[ERR] base not found: {base}")
        sys.exit(1)

    print("=== KB Runner ===")
    print(f"Base:   {base}")
    print(f"Apply:  {args.apply}")
    print(f"Limit:  {args.limit_tags} tags\n")

    changed = 0
    for md in sorted(base.rglob("*.md")):
        if ".obsidian" in md.as_posix():
            continue
        if fix_markdown_file(md, base, max_tags=args.limit_tags, apply=args.apply):
            changed += 1
            print(f"[fix] {md.relative_to(base)}")

    print(f"\n[done] Cleaned {changed} file(s).")

    if args.no_build:
        return

    ensure_tools()
    clean_quartz_output()
    quartz_build()

    if args.serve:
        serve_public(PORT)

    if not args.no_push:
        git_push(interactive=True)

if __name__ == "__main__":
    main()
