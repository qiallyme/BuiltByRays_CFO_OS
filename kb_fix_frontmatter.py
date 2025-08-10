#!/usr/bin/env python3
import re, sys, argparse, yaml
from pathlib import Path

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"

FM_TOP_RE = re.compile(r"^\ufeff?\s*---\s*\n(.*?)\n---\s*\n?", flags=re.S)
H1_RE = re.compile(r"(?m)^\s*#\s+(.+?)\s*$")

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, t): p.write_text(t, encoding="utf-8")

def split_frontmatter(txt: str):
    m = FM_TOP_RE.match(txt)
    if not m:
        return {}, txt, 0, 0
    raw = m.group(1)
    try:
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict): data = {}
    except Exception:
        data = {}
    return data, txt[m.end():], m.start(), m.end()

def build_frontmatter(data: dict) -> str:
    # Render tags/aliases inline; simple scalars otherwise
    lines = ["---"]
    for k, v in data.items():
        if isinstance(v, list) and k in ("tags", "aliases", "alias"):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)

def first_h1(body: str) -> str | None:
    m = H1_RE.search(body)
    return m.group(1).strip() if m else None

def extract_alpha_prefix(name: str):
    """
    Detect leading A/B/C style ordering tokens in filenames/folders:
      A-Title, A.Title, A_Title, 'A Title'  -> ('A.', 'Title')
    Returns (prefix like 'A.', remainder) or ('', name) if none.
    """
    m = re.match(r'^\s*([A-Za-z])(?:\s*[\.\-_]\s*|\s+)(.+)$', name)
    if m:
        return m.group(1).upper() + ".", m.group(2).strip()
    return "", name

def humanize_name(name: str) -> str:
    # Replace separators with spaces, collapse, light capitalize
    s = name.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return "Untitled"
    # Preserve existing capitalization mostly; just ensure first char is uppercase
    return s[0].upper() + s[1:]

def derive_title_with_prefix(path_rel: Path) -> str:
    base_name = path_rel.parent.name if path_rel.name.lower()=="index.md" else path_rel.stem
    prefix, core = extract_alpha_prefix(base_name)
    core_human = humanize_name(core)
    return f"{prefix} {core_human}".strip() if prefix else core_human

def ensure_h1_equals(body: str, desired: str) -> str:
    """
    Ensure the first H1 equals `desired` (with prefix if any).
    - If an H1 exists and differs, replace just that first H1 line.
    - If no H1, insert '# desired' at top.
    Also collapse immediate duplicate identical H1s.
    """
    lines = body.splitlines()
    for i, line in enumerate(lines):
        if H1_RE.match(line):
            # Replace the very first H1 with the desired one
            lines[i] = f"# {desired}"
            # Remove an immediate duplicate if present
            if i+1 < len(lines) and re.match(rf"^\s*#\s+{re.escape(desired)}\s*$", lines[i+1]):
                lines.pop(i+1)
            return "\n".join(lines)
    # No H1 at all → insert at top
    return f"# {desired}\n\n{body.lstrip()}"

KV_LINE_RE = re.compile(r"^\s*(title|date|summary|tags|keywords|status|owner|last[_-]?reviewed)\s*:\s*.*$", re.I)

def strip_stray_kv_header(body: str) -> str:
    """Remove accidental key:value lines at the very top of the body (not in FM)."""
    lines = body.splitlines()
    i = 0
    # eat leading KV lines
    while i < min(30, len(lines)) and KV_LINE_RE.match(lines[i]):
        i += 1
    # eat one or two blank lines after
    while i < len(lines) and lines[i].strip() == "":
        i += 1
    return "\n".join(lines[i:]).lstrip("\n")

def main():
    ap = argparse.ArgumentParser()
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
        fm, body, _, _ = split_frontmatter(txt)

        # Clean up stray key:value lines that leaked into content
        body = strip_stray_kv_header(body)

        # What should the title be?
        h1 = first_h1(body)
        if h1:
            # If file/folder name has an alpha prefix (A./B./...), prepend it unless already present
            base_name = p.parent.name if p.name.lower()=="index.md" else p.stem
            prefix, _ = extract_alpha_prefix(base_name)
            if prefix and not re.match(rf"^\s*{re.escape(prefix)}\s+", h1, flags=re.I):
                desired_title = f"{prefix} {h1}"
            else:
                desired_title = h1
        else:
            desired_title = derive_title_with_prefix(p.relative_to(base))

        # Never let title be "index"
        if desired_title.strip().lower() == "index":
            desired_title = derive_title_with_prefix(p.relative_to(base))

        fm["title"] = desired_title

        # Rebuild FM and sync H1 to exactly match the title
        new_fm = build_frontmatter(fm)
        new_body = ensure_h1_equals(body, desired_title)

        rebuilt = new_fm + new_body.lstrip("\n")
        if rebuilt != txt and args.apply:
            write(p, rebuilt)
            changed += 1

    print(f"[OK] Fixed {changed} files." if args.apply else "[DRY] Done. Use --apply to write.")

if __name__ == "__main__":
    try:
        import yaml
    except Exception:
        print("[ERR] Missing dependency 'pyyaml'. Run: pip install pyyaml")
        sys.exit(1)
    main()
