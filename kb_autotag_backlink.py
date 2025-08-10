#!/usr/bin/env python3
import argparse, re, sys, yaml
from pathlib import Path
from collections import defaultdict

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"
CFG = "kb_tags.yaml"
REL_START = "<!-- RELATED:START -->"
REL_END   = "<!-- RELATED:END -->"

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
FM_TOP_RE   = re.compile(r"^\ufeff?\s*---\s*\n(.*?)\n---\s*\n?", flags=re.S)  # allow BOM/whitespace

NUMERIC_WHITELIST = {"1099", "401k", "10k", "10-q"}
BLOCKLIST = {"index", "readme", "md", "markdown", "content"}

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, t): p.write_text(t, encoding="utf-8")

def split_frontmatter(txt: str):
    """Return (fm_dict, body, span_start, span_end). If none, fm_dict={}, span=(0,0)."""
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
    # nice inline list for tags/aliases; other lists fine as block
    lines = ["---"]
    for k, v in data.items():
        if isinstance(v, list) and k in ("tags", "aliases", "alias"):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---\n")
    return "\n".join(lines)

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

def add_tags(cur, new, cap=None):
    s = []
    seen = set()
    for t in (cur or []):
        nt = normalize_tag(t)
        if nt and nt not in seen:
            seen.add(nt); s.append(nt)
    for t in (new or []):
        nt = normalize_tag(t)
        if nt and nt not in seen:
            seen.add(nt); s.append(nt)
    if cap is not None and cap > 0:
        s = s[:cap]
    return s

def title_from(path_rel: Path) -> str:
    name = path_rel.parent.name if path_rel.name.lower()=="index.md" else path_rel.stem
    name = re.sub(r"^\d{2}[-_]\s*", "", name)
    name = re.sub(r"^[A-Za-z0-9]{1,3}[-_.]\s*", "", name)
    name = name.replace("-", " ").replace("_", " ").strip()
    return " ".join(name.split()) or "Untitled"

def to_wikilink(base: Path, p: Path) -> str:
    rel = p.relative_to(base)
    return rel.parent.as_posix() if rel.name.lower()=="index.md" else rel.with_suffix("").as_posix()

def fm_get_tags(fm: dict):
    v = fm.get("tags") or fm.get("tag")
    if v is None: return []
    if isinstance(v, list): return [str(x) for x in v]
    inner = str(v).strip().strip("[]")
    return [t.strip() for t in inner.split(",") if t.strip()]

def list_children(folder: Path):
    subs, files = [], []
    for p in sorted(folder.iterdir(), key=lambda x: (x.is_file(), x.name.lower())):
        if p.name.startswith("."): continue
        if p.is_dir() and (p / "index.md").exists():
            subs.append(p / "index.md")
        elif p.is_file() and p.suffix.lower()==".md":
            files.append(p)
    return subs, files

def collect_graph(base: Path):
    pages = [p for p in base.rglob("*.md") if ".obsidian" not in p.as_posix()]
    target_to_path = {to_wikilink(base, p): p for p in pages}
    links = defaultdict(set)
    by_target = defaultdict(set)
    for p in pages:
        txt = read(p)
        for m in WIKILINK_RE.finditer(txt):
            tgt = m.group(1).strip().rstrip("/")
            if tgt in target_to_path:
                dst = target_to_path[tgt]
                links[p].add(dst)
                by_target[dst].add(p)
    return pages, links, by_target, target_to_path

def infer_tags_for(p: Path, base: Path, cfg):
    rel = p.relative_to(base)
    parts = rel.parts
    tags = []

    # config-based tags from top folder
    if len(parts) > 0:
        top = parts[0]
        for key, extra in (cfg.get("folders") or {}).items():
            if key == top:
                tags += extra

    # filename + content keywords
    text = (read(p) + " " + " ".join(rel.parts)).lower()
    for kw, kws in (cfg.get("keywords") or {}).items():
        kw_str = str(kw).lower()
        if kw_str and kw_str in text:
            tags += [str(x) for x in (kws or [])]

    # path-derived tags
    def clean(s):
        s = re.sub(r"^\d{2}[-_]", "", s)
        s = re.sub(r"^[A-Za-z0-9]{1,3}[-_.]\s*", "", s)
        s = s.replace("&","and")
        s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
        return s
    if len(parts)>=1: tags.append(clean(parts[0]))
    if len(parts)>=2: tags.append(clean(parts[1]))

    # dedupe
    out=[]; seen=set()
    for t in tags:
        if t and t not in seen:
            out.append(t); seen.add(t)
    return out

def inject_related(p: Path, base: Path, cfg, links, by_target, target_to_path, apply=False):
    txt = read(p)
    fm, body, s, e = split_frontmatter(txt)
    tags_now = [t.strip() for t in fm_get_tags(fm)]

    related = set()
    # backlinks first
    for src in by_target.get(p, []):
        related.add(src)

    if tags_now:
        for q in target_to_path.values():
            if q == p: continue
            qtxt = read(q)
            qfm, _, _, _ = split_frontmatter(qtxt)
            qtags = [t.strip() for t in fm_get_tags(qfm)]
            if set(t.lower() for t in qtags) & set(t.lower() for t in tags_now):
                related.add(q)

    if not related and not by_target.get(p):
        return False

    def linkline(x: Path):
        return f"- [[{to_wikilink(base, x)}]]"

    lines = [REL_START, "", "## Related"]
    backs = [x for x in sorted(by_target.get(p, []), key=lambda z: z.as_posix())]
    if backs:
        lines.append("**Backlinks**")
        lines += [linkline(x) for x in backs]
        lines.append("")
    similars = [x for x in sorted(related, key=lambda z: z.as_posix()) if x not in backs]
    if similars:
        lines.append("**Similar by tag**")
        lines += [linkline(x) for x in similars]
        lines.append("")
    lines.append(REL_END)
    block = "\n".join(lines)

    new_body = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), block, body, flags=re.S) \
               if (REL_START in body and REL_END in body) else \
               (insert_after_h1(body, block))

    if new_body != body and apply:
        write(p, build_frontmatter(fm) + new_body.lstrip("\n"))
    return new_body != body

def insert_after_h1(body: str, block: str) -> str:
    m = re.search(r"(?m)^\s*#\s+.+$", body)
    if m:
        return body[:m.end()] + "\n\n" + block + "\n" + body[m.end():]
    return body.rstrip()+"\n\n"+block+"\n"

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
    fm, body, s, e = split_frontmatter(txt)
    if fm.get("aliases") or fm.get("alias"):
        return False
    fm["aliases"] = [str(x) for x in add]
    new = build_frontmatter(fm) + body
    if new != txt and apply:
        write(p, new)
    return new != txt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max-tags", type=int, default=5)
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists(): print(f"[ERR] base not found: {base}"); sys.exit(1)

    cfgp = Path(CFG)
    cfg = yaml.safe_load(cfgp.read_text(encoding="utf-8")) if cfgp.exists() else {}
    if cfg is None: cfg = {}

    pages, links, by_target, target_to_path = collect_graph(base)

    changed = 0
    for p in pages:
        txt = read(p)

        # 1) ensure one FM block
        fm, body, s, e = split_frontmatter(txt)
        if not fm:
            fm = {"title": title_from(p.relative_to(base))}
            txt = build_frontmatter(fm) + body
            body = body  # unchanged
            changed += 1

        # 2) merge tags and cap
        cur = fm_get_tags(fm)
        inferred = infer_tags_for(p, base, cfg)
        new_tags = add_tags(cur, inferred, cap=args.max_tags)
        if new_tags:
            fm["tags"] = new_tags
        else:
            fm.pop("tags", None)
            fm.pop("tag", None)

        # 3) write FM back if changed
        rebuilt = build_frontmatter(fm) + body.lstrip("\n")
        if rebuilt != txt and args.apply:
            write(p, rebuilt)
            changed += 1

        # 4) aliases (optional)
        if maybe_add_aliases(p, base, cfg, apply=args.apply):
            changed += 1

        # 5) related block
        if inject_related(p, base, cfg, links, by_target, target_to_path, apply=args.apply):
            changed += 1

    print(f"[OK] Updated {changed} files." if args.apply else "[DRY] Done. Use --apply to write.")

if __name__ == "__main__":
    try:
        import yaml  # ensure pyyaml
    except Exception:
        print("[ERR] Missing dependency 'pyyaml'. Run: pip install pyyaml")
        sys.exit(1)
    main()
