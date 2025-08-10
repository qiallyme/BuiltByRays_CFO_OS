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
    # swap underscores/spaces to hyphens
    t = t.replace("_", "-").replace(" ", "-")
    # collapse repeats
    t = re.sub(r"-{2,}", "-", t)
    # strip non-alnum except hyphen
    t = re.sub(r"[^a-z0-9-]", "", t)
    # drop pure numeric unless whitelisted
    if t.isdigit() and t not in NUMERIC_WHITELIST:
        return ""
    # drop blocklisted
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
    if path_rel.name.lower()=="index.md": return path_rel.parent.name
    return path_rel.stem

def to_wikilink(base, p):
    rel = p.relative_to(base)
    if rel.name.lower()=="index.md": return rel.parent.as_posix()
    return rel.with_suffix("").as_posix()

def add_tags(existing_tags, new_tags):
    s = set()
    for t in (existing_tags or []):
        nt = normalize_tag(t)
        if nt:
            s.add(nt)
    for t in (new_tags or []):
        nt = normalize_tag(t)
        if nt:
            s.add(nt)
    return sorted(s)



def collect_graph(base: Path):
    pages = []
    links = defaultdict(set)
    by_target = defaultdict(set)
    for md in base.rglob("*.md"):
        if ".obsidian" in md.as_posix(): continue
        pages.append(md)
    # map from wikilink target -> real md path
    target_to_path = {}
    for p in pages:
        target_to_path[to_wikilink(base, p)] = p

    for p in pages:
        txt = read(p)
        for m in WIKILINK_RE.finditer(txt):
            tgt = m.group(1).strip()
            # normalize without trailing slash
            tgt = tgt.rstrip("/")
            if tgt in target_to_path:
                dst = target_to_path[tgt]
                links[p].add(dst)
                by_target[dst].add(p)
    return pages, links, by_target, target_to_path

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

    # from filename and content via keywords
    text = read(p).lower()
    text += " " + " ".join(rel.parts).lower()
    for kw, kws in (cfg.get("keywords") or {}).items():
        kw_str = str(kw).lower()
        if kw_str and kw_str in text:
            tags += [str(x) for x in (kws or [])]



    # path-derived tags (simple)
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
    fm, body = fm_split(txt)
    # find current tags
    tags_line = fm_get("tags", fm)
    tags_now = []
    if tags_line:
        inner = tags_line.strip()
        inner = inner[1:-1] if inner.startswith("[") and inner.endswith("]") else inner
        tags_now = [t.strip().strip(",") for t in inner.split(",") if t.strip()]

    # “related by tag”: siblings sharing ≥1 tag
    related = set()
    # gather backlinks (by_target)
    for src in by_target.get(p, []):
        related.add(src)

    # if we have tags, find other pages with overlap (quick pass)
    if tags_now:
        for q in target_to_path.values():
            if q == p: continue
            qt = read(q)
            qfm,_ = fm_split(qt)
            tl = fm_get("tags", qfm) or "[]"
            qtags = [t.strip() for t in tl.strip("[]").split(",") if t.strip()]
            if set(t.lower() for t in qtags) & set(t.lower() for t in tags_now):
                related.add(q)

    # Build block
    if not related and not by_target.get(p):
        # nothing to inject
        return False

    def linkline(x: Path):
        return f"- [[{to_wikilink(base, x)}]]"

    lines = [REL_START, "", "## Related"]
    # prefer backlinks first
    backs = [x for x in sorted(by_target.get(p, []), key=lambda z: z.as_posix())]
    if backs:
        lines.append("**Backlinks**")
        lines += [linkline(x) for x in backs]
        lines.append("")
    # then similar-by-tag (excluding already listed)
    similars = [x for x in sorted(related, key=lambda z: z.as_posix()) if x not in backs]
    if similars:
        lines.append("**Similar by tag**")
        lines += [linkline(x) for x in similars]
        lines.append("")
    lines.append(REL_END)
    block = "\n".join(lines)

    # Insert/replace
    if REL_START in txt and REL_END in txt:
        new = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), block, txt, flags=re.S)
    else:
        # after first H1 if any, else append
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

    txt = read(p)
    fm, body = fm_split(txt)
    if not fm:
        fm = "---\n---"
    current = fm_get("aliases", fm)
    if current:
        # already has aliases, skip
        return False
    arr = ", ".join(add)
    fm = fm_set("aliases", f"[{arr}]", fm)
    new = fm + body
    if new != txt and apply:
        write(p, new)
    return new != txt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=DEFAULT_BASE)
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    base = Path(args.base).resolve()
    if not base.exists(): print(f"[ERR] base not found: {base}"); sys.exit(1)
    cfgp = Path(CFG)
    cfg = {}
    if cfgp.exists():
        cfg = yaml.safe_load(cfgp.read_text(encoding="utf-8")) or {}
    else:
        print(f"[WARN] {CFG} not found; using built-ins only")

    pages, links, by_target, target_to_path = collect_graph(base)

    changed = 0
    for p in pages:
        # ensure FM exists (title from path if needed)
        txt = read(p)
        title = title_from(p.relative_to(base))
        fm, body = ensure_fm(txt, title)
        if fm + body != txt and args.apply:
            write(p, fm + body); changed += 1

        # infer tags and merge
        fm, body = fm_split(read(p))
        tags_line = fm_get("tags", fm)
        cur = []
        if tags_line:
            inner = tags_line.strip("[]")
            cur = [t.strip() for t in inner.split(",") if t.strip()]
        inferred = infer_tags_for(p, base, cfg)
        merged = add_tags(cur, inferred)
        fm2 = fm_set("tags", "[" + ", ".join(merged) + "]", fm)
        if fm2 != fm and args.apply:
            write(p, fm2 + body); changed += 1

        # optional: add aliases
        if maybe_add_aliases(p, base, cfg, apply=args.apply):
            changed += 1

        # inject Related block
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
