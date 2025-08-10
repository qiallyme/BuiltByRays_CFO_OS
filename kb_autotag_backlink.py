#!/usr/bin/env python3
import argparse, re, sys, yaml
from pathlib import Path
from collections import defaultdict

DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"
CFG = "kb_tags.yaml"
REL_START = "<!-- RELATED:START -->"
REL_END   = "<!-- RELATED:END -->"

WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

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

def fm_split(txt):
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        if end != -1: return txt[:end+4], txt[end+4:]
    return "", txt

def fm_get(k, fm):
    m = re.search(rf"(?m)^{k}\s*:\s*(.+)$", fm)
    return m.group(1).strip() if m else None

def fm_set(k, v, fm):
    if re.search(rf"(?m)^{k}\s*:", fm):
        return re.sub(rf"(?m)^{k}\s*:.*$", f"{k}: {v}", fm)
    insert_at = len(fm)-4 if fm.startswith("---") and fm.endswith("---") else 0
    return fm[:insert_at] + ("" if insert_at==0 else "\n") + f"{k}: {v}\n" + fm[insert_at:]

def ensure_fm(txt, title):
    fm, body = fm_split(txt)
    if not fm:
        fm = f"---\ntitle: {title}\n---"
    if "title:" not in fm:
        fm = fm_set("title", title, fm)
    return fm, body

def title_from(path_rel):
    # prefer first H1 if present
    txt_path = rel_to_abs(path_rel)
    try:
        txt = read(txt_path)
        _, body = fm_split(txt)
        m = re.search(r"(?m)^\s*#\s+(.+?)\s*$", body)
        if m: return m.group(1).strip()
    except Exception:
        pass
    # fallback to path
    if path_rel.name.lower()=="index.md": return path_rel.parent.name
    return path_rel.stem

def rel_to_abs(path_rel: Path) -> Path:
    # helper is set in main via closure; replaced at runtime
    return path_rel  # placeholder

def to_wikilink(base, p):
    rel = p.relative_to(base)
    if rel.name.lower()=="index.md": return rel.parent.as_posix()
    return rel.with_suffix("").as_posix()

def ordered_uniq(seq):
    seen=set(); out=[]
    for t in seq:
        nt = normalize_tag(t)
        if nt and nt not in seen:
            out.append(nt); seen.add(nt)
    return out

def collect_graph(base: Path):
    pages = []
    links = defaultdict(set)
    by_target = defaultdict(set)
    for md in base.rglob("*.md"):
        if ".obsidian" in md.as_posix(): continue
        pages.append(md)
    target_to_path = {}
    for p in pages:
        target_to_path[to_wikilink(base, p)] = p
    for p in pages:
        txt = read(p)
        for m in WIKILINK_RE.finditer(txt):
            tgt = m.group(1).strip().rstrip("/")
            if tgt in target_to_path:
                dst = target_to_path[tgt]
                links[p].add(dst)
                by_target[dst].add(p)
    return pages, links, by_target, target_to_path

def simple_clean(s: str) -> str:
    s = re.sub(r"^\d{2}[-_]", "", s)
    s = re.sub(r"^[A-Za-z0-9]{1,3}[-_.]\s*", "", s)
    s = s.replace("&","and")
    s = re.sub(r"[^a-zA-Z0-9]+","-", s).strip("-").lower()
    return s

def infer_tags_for(p: Path, base: Path, cfg):
    rel = p.relative_to(base)
    parts = rel.parts
    tags = []
    # from config folders
    if len(parts)>0:
        top = parts[0]
        for key, extra in (cfg.get("folders") or {}).items():
            if key == top:
                tags += extra
    # filename/content keywords
    text = read(p).lower() + " " + " ".join(rel.parts).lower()
    for kw, kws in (cfg.get("keywords") or {}).items():
        kw_str = str(kw).lower()
        if kw_str and kw_str in text:
            tags += [str(x) for x in (kws or [])]
    # path-derived (top-level, second-level)
    if len(parts)>=1: tags.append(simple_clean(parts[0]))
    if len(parts)>=2: tags.append(simple_clean(parts[1]))
    return ordered_uniq(tags)

def inject_related(p: Path, base: Path, cfg, links, by_target, target_to_path, apply=False):
    txt = read(p)
    fm, body = fm_split(txt)
    tags_line = fm_get("tags", fm)
    tags_now = []
    if tags_line:
        inner = tags_line.strip()
        inner = inner[1:-1] if inner.startswith("[") and inner.endswith("]") else inner
        tags_now = [t.strip().strip(",") for t in inner.split(",") if t.strip()]

    related = set()
    for src in by_target.get(p, []):
        related.add(src)
    if tags_now:
        for q in target_to_path.values():
            if q == p: continue
            qt = read(q); qfm,_ = fm_split(qt)
            tl = fm_get("tags", qfm) or "[]"
            qtags = [t.strip() for t in tl.strip("[]").split(",") if t.strip()]
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

    if REL_START in txt and REL_END in txt:
        new = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), block, txt, flags=re.S)
    else:
        m = re.search(r"(?m)^#\s+.+", txt)
        if m:
            new = txt[:m.end()] + "\n\n" + block + "\n" + txt[m.end():]
        else:
            new = txt.rstrip()+"\n\n"+block+"\n"

    if new != txt and apply:
        write(p, new)
    return new != txt

def maybe_add_aliases(p: Path, base: Path, cfg, apply=False):
    rel = p.relative_to(base)
    stem = rel.parent.name if p.name.lower()=="index.md" else p.stem
    al_cfg = cfg.get("aliases") or {}
    add = None
    for key, arr in al_cfg.items():
        if key.lower() in stem.lower():
            add = arr; break
    if not add: return False
    txt = read(p); fm, body = fm_split(txt)
    if not fm: fm = "---\n---"
    if fm_get("aliases", fm): return False
    fm = fm_set("aliases", "[" + ", ".join(add) + "]", fm)
    new = fm + body
    if new != txt and apply:
        write(p, new)
    return new != txt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--max-tags", type=int, default=5, help="max tags to keep in frontmatter")
    ap.add_argument("--spill-keywords", action="store_true", help="store overflow tags in 'keywords' field")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists():
        print(f"[ERR] base not found: {base}"); sys.exit(1)

    # wire helper for title_from
    def _rel_to_abs(relp: Path) -> Path:
        return base / relp
    globals()['rel_to_abs'] = _rel_to_abs

    cfgp = Path(CFG)
    cfg = yaml.safe_load(cfgp.read_text(encoding="utf-8")) or {} if cfgp.exists() else {}

    pages, links, by_target, target_to_path = collect_graph(base)

    changed = 0
    for p in pages:
        txt = read(p)
        rel = p.relative_to(base)

        # TITLE: prefer H1, else path
        ttl = title_from(rel)
        fm, body = ensure_fm(txt, ttl)

        # CURRENT TAGS
        tags_line = fm_get("tags", fm) or "[]"
        cur = [t.strip() for t in tags_line.strip("[]").split(",") if t.strip()]

        # INFERRED TAGS
        inferred = infer_tags_for(p, base, cfg)

        # PREFERRED ORDER: top folder, second folder first
        parts = rel.parts
        preferred = []
        if len(parts)>=1: preferred.append(simple_clean(parts[0]))
        if len(parts)>=2: preferred.append(simple_clean(parts[1]))

        ordered = ordered_uniq(preferred + cur + inferred)

        visible = ordered[:max(0, args.max_tags)]
        overflow = ordered[len(visible):]

        # write tags + (optional) keywords
        fm2 = fm_set("tags", "[" + ", ".join(visible) + "]", fm)
        if args.spill_keywords and overflow:
            fm2 = fm_set("keywords", "[" + ", ".join(overflow) + "]", fm2)
        # also capture date if missing (Quartz likes it)
        if fm_get("date", fm2) is None:
            fm2 = fm_set("date", "2025-08-10", fm2)  # or generate today if you prefer

        new_txt = fm2 + body
        if new_txt != txt and args.apply:
            write(p, new_txt); changed += 1

        if maybe_add_aliases(p, base, cfg, apply=args.apply):
            changed += 1
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
