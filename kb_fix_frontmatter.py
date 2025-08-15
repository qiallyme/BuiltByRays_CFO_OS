#!/usr/bin/env python3
import re, sys, argparse, yaml
from pathlib import Path

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"

FM_TOP_RE = re.compile(r"^\ufeff?\s*---\s*\n(.*?)\n---\s*\n?", flags=re.S)
H1_RE = re.compile(r"(?m)^\s*#\s+(.+?)\s*$")

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, t): p.write_text(t, encoding="utf-8")

def split_frontmatter(txt: str):
    """Extract frontmatter and body, handling multiple frontmatter blocks by keeping only the first."""
    m = FM_TOP_RE.match(txt)
    if not m:
        return {}, txt, 0, 0
    
    raw = m.group(1)
    try:
        data = yaml.safe_load(raw) or {}
        if not isinstance(data, dict): 
            data = {}
    except Exception:
        data = {}
    
    # Get the body after the first frontmatter block
    body_start = m.end()
    body = txt[body_start:]
    
    # Remove ALL additional frontmatter blocks that might have been duplicated
    # This is more aggressive - remove any --- blocks at the start of body
    while True:
        body_before = body
        # Remove any frontmatter blocks (--- ... ---)
        body = re.sub(r'^\s*---\s*\n.*?\n---\s*\n?', '', body, flags=re.S)
        # Also remove any single --- lines that might be left
        body = re.sub(r'^\s*---\s*\n', '', body, flags=re.M)
        if body == body_before:
            break
    
    return data, body, m.start(), body_start

def build_frontmatter(data: dict) -> str:
    """Build clean frontmatter with proper YAML formatting."""
    if not data:
        return "---\n---\n"
    
    lines = ["---"]
    for k, v in data.items():
        if isinstance(v, list) and k in ("tags", "aliases", "alias"):
            # Format lists properly
            if v:
                lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
            else:
                lines.append(f"{k}: []")
        elif isinstance(v, str) and v:
            # Escape quotes if needed
            if '"' in v or '\n' in v:
                escaped_v = v.replace('"', '\\"')
                lines.append(f'{k}: "{escaped_v}"')
            else:
                lines.append(f"{k}: {v}")
        elif v is not None:
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

def to_sentence_case(text: str) -> str:
    """Convert text to sentence case while preserving important formatting."""
    if not text:
        return text
    
    # Split by common separators and capitalize each part
    parts = re.split(r'[-\s_]+', text)
    sentence_parts = []
    
    for part in parts:
        if part:
            # Preserve existing capitalization for acronyms and proper nouns
            if part.isupper() or part in ['A.', 'B.', 'C.', 'D.', 'E.', 'F.', 'G.', 'H.', 'I.', 'J.', 'K.', 'L.', 'M.', 'N.', 'O.', 'P.', 'Q.', 'R.', 'S.', 'T.', 'U.', 'V.', 'W.', 'X.', 'Y.', 'Z.']:
                sentence_parts.append(part)
            else:
                # Convert to sentence case
                sentence_parts.append(part[0].upper() + part[1:].lower())
    
    return ' '.join(sentence_parts)

def humanize_name(name: str) -> str:
    """Convert filename to human-readable title while preserving important formatting."""
    # Replace separators with spaces, collapse, light capitalize
    s = name.replace("_", " ").replace("-", " ")
    s = re.sub(r"\s+", " ", s).strip()
    if not s:
        return "Untitled"
    
    # Convert to sentence case
    return to_sentence_case(s)

def derive_title_with_prefix(path_rel: Path) -> str:
    """Derive title from path, preserving any alpha prefixes."""
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
            # Remove any immediate duplicates
            j = i + 1
            while j < len(lines) and re.match(rf"^\s*#\s+{re.escape(desired)}\s*$", lines[j]):
                lines.pop(j)
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

def deduplicate_frontmatter(fm: dict) -> dict:
    """Remove duplicate entries and ensure clean frontmatter."""
    # Remove any None or empty values
    cleaned = {k: v for k, v in fm.items() if v is not None and v != ""}
    
    # Ensure tags are properly formatted
    if "tags" in cleaned and isinstance(cleaned["tags"], list):
        # Remove duplicates and empty tags
        cleaned["tags"] = list(dict.fromkeys([t for t in cleaned["tags"] if t]))
    
    # Ensure aliases are properly formatted
    if "aliases" in cleaned and isinstance(cleaned["aliases"], list):
        cleaned["aliases"] = list(dict.fromkeys([a for a in cleaned["aliases"] if a]))
    
    return cleaned

def determine_proper_title(p: Path, base: Path, h1: str | None) -> str:
    """
    Determine the proper title for a file.
    Priority: H1 content > filename-derived > never "index"
    """
    if h1:
        # If file/folder name has an alpha prefix (A./B./...), prepend it unless already present
        base_name = p.parent.name if p.name.lower()=="index.md" else p.stem
        prefix, _ = extract_alpha_prefix(base_name)
        if prefix and not re.match(rf"^\s*{re.escape(prefix)}\s+", h1, flags=re.I):
            # Convert H1 to sentence case and add prefix
            h1_sentence = to_sentence_case(h1)
            return f"{prefix} {h1_sentence}"
        else:
            # Convert H1 to sentence case
            return to_sentence_case(h1)
    else:
        # No H1 - derive from filename
        derived = derive_title_with_prefix(p.relative_to(base))
        # Never allow "index" as title
        if derived.strip().lower() == "index":
            # Use parent folder name instead
            parent_name = p.parent.name
            prefix, core = extract_alpha_prefix(parent_name)
            core_human = humanize_name(core)
            return f"{prefix} {core_human}".strip() if prefix else core_human
        return derived

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
        desired_title = determine_proper_title(p, base, h1)

        # Update frontmatter
        fm["title"] = desired_title
        
        # Clean up frontmatter to remove duplicates and ensure proper formatting
        fm = deduplicate_frontmatter(fm)

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
