#!/usr/bin/env python3
import argparse, re, sys, yaml
from pathlib import Path
from collections import defaultdict

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"
CFG = "kb_tags.yaml"

REL_START = "<!-- RELATED:START -->"
REL_END   = "<!-- RELATED:END -->"

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FRONTMATTER_TOP_RE = re.compile(r"^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", re.S | re.M)

NUMERIC_WHITELIST = {"1099", "401k", "10k", "10-q"}
BLOCKLIST = {"index", "readme", "md", "markdown", "content"}

def normalize_tag(t):
    t = str(t).strip().lower()
    if not t:
        return ""
    t = t.replace("_", "-").replace(" ", "-")
    t = re.sub(r"-{2,}", "-", t)
    t = re.sub(r"[^a-z0-9-]", "", t)
    if t.isdigit() and t not in NUMERIC_WHITELIST:
        return ""
    if t in BLOCKLIST:
        return ""
    return t

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, t): p.write_text(t, encoding="utf-8")

def to_wikilink(base, p: Path) -> str:
    rel = p.relative_to(base)
    if rel.name.lower() == "index.md":
        return rel.parent.as_posix()
    return rel.with_suffix("").as_posix()

def first_h1(body: str) -> str | None:
    m = re.search(r"(?m)^\s*#\s+(.+?)\s*$", body)
    return m.group(1).strip() if m else None

def strip_body_frontmatter_blocks(body: str) -> str:
    """
    Remove any YAML frontmatter blocks that appear AFTER the first one.
    Only remove if the block actually looks like YAML metadata (contains title:/date:/tags:).
    """
    def repl(m):
        inner = m.group(1)
        if re.search(r"(?m)^(title|date|tags)\s*:", inner):
            return ""  # drop this stray YAML block
        return m.group(0)  # keep if it's not metadata (very rare)
    # Replace all subsequent fm blocks (not at start) safely
    # Find all blocks then rebuild once to avoid nested/overlapping issues.
    parts = []
    last = 0
    for m in re.finditer(r"(?m)^---\s*\r?\n(.*?)\r?\n---\s*\r?\n?", body, re.S):
        parts.append(body[last:m.start()])
        inner = m.group(1)
        if re.search(r"(?m)^(title|date|tags)\s*:", inner):
            parts.append("")  # drop
        else:
            parts.append(m.group(0))  # keep
        last = m.end()
    parts.append(body[last:])
    return "".join(parts)

def strip_leading_kv_lines(body: str) -> str:
    """
    If someone wrote lines like 'title: X' / 'date: Y' / 'tags: [...]' at the very top
    of the body (outside YAML), strip them so Quartz doesn't render them as text.
    """
    lines = body.splitlines()
    i = 0
    while i < len(lines) and re.match(r"\s*(title|date|tags)\s*:", lines[i], re.I):
        i += 1
    return ("\n".join(lines[i:])).lstrip("\n")

def parse_top_frontmatter(txt: str) -> tuple[dict, str]:
    """
    Return (fm_dict, body) ensuring we only consider the TOP block as frontmatter.
    """
    m = FRONTMATTER_TOP_RE.match(txt)
    if m:
        raw = m.group(1)
        try:
            fm = yaml.safe_load(raw) or {}
        except Exception:
            fm = {}
        body = txt[m.end():]
        return (dict(fm), body)
    else:
        return ({}, txt)

def dump_frontmatter(fm: dict) -> str:
    # Keep order, allow unicode, multi-line lists OK
    dumped = yaml.safe_dump(fm, sort_keys=False, allow_unicode=True).strip()
    return f"---\n{dumped}\n---\n"

def title_from_path(rel: Path) -> str:
    return (rel.parent.name if rel.name.lower() == "index.md" else rel.stem).replace("-", " ").strip().title()

def ensure_title_from_h1(fm: dict, body: str, rel: Path) -> tuple[dict, str]:
    """
    If there's an H1, prefer it as the canonical title. If there's no H1, insert one
    using existing fm['title'] (or path) and return updated body.
    """
    h = first_h1(body)
    current = (fm.get("title") or "").strip()
    if h:
        if (not current) or current.lower() in {"index", "readme"} or current.strip() != h.strip():
            fm["title"] = h.strip()
        return fm, body
    # No H1: insert one
    final_title = current if current else title_from_path(rel)
    fm["title"] = final_title
    body = f"# {final_title}\n\n{body.lstrip()}"
    return fm, body

def add_tags(existing_tags, new_tags):
    s = set()
    for t in (existing_tags or []):
        nt = normalize_tag(t)
        if nt: s.add(nt)
    for t in (new_tags or []):
        nt = normalize_tag(t)
        if nt: s.add(nt)
    return sorted(s)

def collect_graph(base: Path):
    pages = []
    links = defaultdict(set)
    by_target = defaultdict(set)

    for md in base.rglob("*.md"):
        if ".obsidian" in md.as_posix(): 
            continue
        pages.append(md)

    target_to_path = {to_wikilink(base, p): p for p in pages}

    for p in pages:
        txt = read(p)
        for m in WIKILINK_RE.finditer(txt):
            tgt = m.group(1).strip().rstrip("/")
            if tgt in target_to_path:
                dst = target_to_path[tgt]
                if dst != p:
                    links[p].add(dst)
                    by_target[dst].add(p)
    return pages, links, by_target, target_to_path

def infer_tags_for(p: Path, base: Path, cfg):
    rel = p.relative_to(base)
    parts = rel.parts
    tags = []

    # config-based
    if len(parts) > 0:
        top = parts[0]
        for key, extra in (cfg.get("folders") or {}).items():
            if key == top:
                tags += list(extra or [])

    # filename/content
    text = (read(p).lower() + " " + " ".join(rel.parts).lower())
    for kw, kws in (cfg.get("keywords") or {}).items():
        kw_str = str(kw).lower()
        if kw_str and kw_str in text:
            tags += [str(x) for x in (kws or [])]

    # path-derived
    def clean(s):
        s = re.sub(r"^\d{2}[-_]", "", s)
        s = re.sub(r"^[A-Za-z0-9]{1,3}[-_.]\s*", "", s)
        s = s.replace("&","and")
        s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
        return s
    if len(parts) >= 1: tags.append(clean(parts[0]))
    if len(parts) >= 2: tags.append(clean(parts[1]))

    out, seen = [], set()
    for t in tags:
        if t and t not in seen:
            out.append(t); seen.add(t)
    return out

def inject_related(p: Path, base: Path, cfg, links, by_target, target_to_path, apply=False):
    txt = read(p)
    fm, body = parse_top_frontmatter(txt)

    # use frontmatter tags for similarity
    tags_now = fm.get("tags") or []

    related = set()
    # backlinks
    for src in by_target.get(p, []):
        related.add(src)

    # similar by tags (cheap scan)
    if tags_now:
        tags_now_l = {str(t).lower() for t in tags_now}
        for q in target_to_path.values():
            if q == p: continue
            qtxt = read(q)
            qfm, _ = parse_top_frontmatter(qtxt)
            qtags = {str(t).lower() for t in (qfm.get("tags") or [])}
            if qtags & tags_now_l:
                related.add(q)

    if not related and not by_target.get(p):
        return False

    def linkline(x: Path): return f"- [[{to_wikilink(base, x)}]]"

    lines = [REL_START, "", "## Related"]
    backs = sorted(by_target.get(p, []), key=lambda z: z.as_posix())
    # remove self just in case
    backs = [x for x in backs if x != p]
    if backs:
        lines.append("**Backlinks**")
        lines += [linkline(x) for x in backs]
        lines.append("")

    similars = sorted((related - set(backs) - {p}), key=lambda z: z.as_posix())
    if similars:
        lines.append("**Similar by tag**")
        lines += [linkline(x) for x in similars[:10]]  # cap to 10
        lines.append("")
    lines.append(REL_END)
    block = "\n".join(lines)

    # insert/replace block AFTER first H1 if present; else append
    m = re.search(r"(?m)^#\s+.+?$", body)
    if REL_START in body and REL_END in body:
        new_body = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), block, body, flags=re.S)
    elif m:
        new_body = body[:m.end()] + "\n\n" + block + "\n" + body[m.end():]
    else:
        new_body = body.rstrip() + "\n\n" + block + "\n"

    if new_body != body:
        new = dump_frontmatter(fm) + new_body
        if apply:
            write(p, new)
        return True
    return False

def maybe_add_aliases(p: Path, base: Path, cfg, apply=False):
    rel = p.relative_to(base)
    stem = rel.parent.name if p.name.lower()=="index.md" else p.stem
    al_cfg = cfg.get("aliases") or {}
    add = None
    for key, arr in al_cfg.items():
        if key.lower() in stem.lower():
            add = arr; break
    if not add: return False

    txt = read(p)
    fm, body = parse_top_frontmatter(txt)
    if "aliases" in fm and fm["aliases"]:
        return False
    fm["aliases"] = list(add)
    new = dump_frontmatter(fm) + body
    if apply:
        write(p, new)
    return True

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"[ERR] base not found: {base}")
        sys.exit(1)

    cfg = {}
    cfgp = Path(CFG)
    if cfgp.exists():
        cfg = yaml.safe_load(cfgp.read_text(encoding="utf-8")) or {}
    else:
        print(f"[WARN] {CFG} not found; using built-ins only")

    pages, links, by_target, target_to_path = collect_graph(base)

    changed = 0
    for p in pages:
        txt = read(p)

        # 1) parse top FM, scrub body duplicates / stray key: value lines
        fm, body = parse_top_frontmatter(txt)
        body = strip_body_frontmatter_blocks(body)
        body = strip_leading_kv_lines(body)

        # 2) title from H1 if present (else insert H1/title)
        rel = p.relative_to(base)
        fm, body = ensure_title_from_h1(fm, body, rel)

        # 3) tags: merge inferred + existing
        cur_tags = fm.get("tags") or []
        inferred = infer_tags_for(p, base, cfg)
        fm["tags"] = add_tags(cur_tags, inferred)

        # 4) write normalized file (FM at top only)
        normalized = dump_frontmatter(fm) + body
        if normalized != txt and args.apply:
            write(p, normalized)
            changed += 1

        # 5) aliases (optional)
        if maybe_add_aliases(p, base, cfg, apply=args.apply):
            changed += 1

        # 6) related/backlinks block
        if inject_related(p, base, cfg, links, by_target, target_to_path, apply=args.apply):
            changed += 1

    if args.apply:
        print(f"[OK] Updated {changed} files.")
    else:
        print("[DRY] Completed analysis. Use --apply to write changes.")

if __name__ == "__main__":
    try:
        import yaml  # pyyaml
    except Exception:
        print("[ERR] Missing dependency 'pyyaml'. Run: pip install pyyaml")
        sys.exit(1)
    main()
