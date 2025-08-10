#!/usr/bin/env python3
import argparse, re, sys, yaml
from pathlib import Path
from collections import defaultdict

# ====== CONFIG ======
DEFAULT_BASE = r"C:\Users\codyr\Documents\Github\EmpowerQNow713\BuiltByRays_CFO_OS\content"
CFG = "kb_tags.yaml"
REL_START = "<!-- RELATED:START -->"
REL_END   = "<!-- RELATED:END -->"

# how many tags to keep visible in frontmatter pills
MAX_TAGS_VISIBLE = 12

# ====================

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

def read(p: Path): 
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p: Path, t: str):
    # single backup per run (.bak)
    bak = p.with_suffix(p.suffix + ".bak")
    if not bak.exists():
        bak.write_text(read(p), encoding="utf-8")
    p.write_text(t, encoding="utf-8")

def fm_split(txt: str):
    if txt.startswith("---"):
        end = txt.find("\n---", 3)
        if end != -1:
            return txt[:end+4], txt[end+4:]
    return "", txt

def fm_get(k: str, fm: str):
    m = re.search(rf"(?m)^{k}\s*:\s*(.+)$", fm)
    return m.group(1).strip() if m else None

def fm_set(k: str, v: str, fm: str) -> str:
    if re.search(rf"(?m)^{k}\s*:", fm):
        return re.sub(rf"(?m)^{k}\s*:.*$", f"{k}: {v}", fm)
    insert_at = len(fm)-4 if fm.startswith("---") and fm.endswith("---") else 0
    prefix = "" if insert_at == 0 else "\n"
    return fm[:insert_at] + prefix + f"{k}: {v}\n" + fm[insert_at:]

def ensure_fm(txt: str, title: str):
    fm, body = fm_split(txt)
    if not fm:
        fm = f"---\ntitle: {title}\n---"
    if "title:" not in fm:
        fm = fm_set("title", title, fm)
    return fm, body

def title_from(path_rel: Path) -> str:
    if path_rel.name.lower() == "index.md":
        return path_rel.parent.name
    return path_rel.stem

def to_wikilink(base: Path, p: Path) -> str:
    rel = p.relative_to(base)
    if rel.name.lower() == "index.md":
        return rel.parent.as_posix()
    return rel.with_suffix("").as_posix()

def parse_tag_list(val: str):
    # supports "tags: [a, b]" or "tags: a, b"
    if not val:
        return []
    s = val.strip()
    if s.startswith("[") and s.endswith("]"):
        s = s[1:-1]
    items = [x.strip() for x in s.split(",") if x.strip()]
    return items

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
        if ".obsidian" in md.as_posix():
            continue
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

def infer_tags_for(p: Path, base: Path, cfg):
    rel = p.relative_to(base)
    parts = rel.parts
    tags = []

    # from config folders
    if len(parts) > 0:
        top = parts[0]
        for key, extra in (cfg.get("folders") or {}).items():
            if key == top:
                tags += [str(x) for x in (extra or [])]

    # from filename/body via keywords
    text = (read(p) + " " + " ".join(rel.parts)).lower()
    for kw, kws in (cfg.get("keywords") or {}).items():
        kw_str = str(kw).lower()
        if kw_str and kw_str in text:
            tags += [str(x) for x in (kws or [])]

    # path-derived tags
    def clean(s):
        s = re.sub(r"^\d{2}[-_]", "", s)
        s = re.sub(r"^[A-Za-z0-9]{1,3}[-_.]\s*", "", s)
        s = s.replace("&", "and")
        s = re.sub(r"[^a-zA-Z0-9]+", "-", s).strip("-").lower()
        return s

    if len(parts) >= 1: tags.append(clean(parts[0]))
    if len(parts) >= 2: tags.append(clean(parts[1]))

    out, seen = [], set()
    for t in tags:
        if t and t not in seen:
            out.append(t); seen.add(t)
    return out

def strip_visible_tag_sections(txt: str) -> str:
    # remove any old "## Tags" bullet sections we may have added before
    txt = re.sub(r"(?ms)^\s*##\s*Tags\s*\n(?:- .*\n?)+", "", txt)
    # squeeze excessive blank lines
    txt = re.sub(r"\n{3,}", "\n\n", txt)
    return txt

def inject_related_block(p: Path, base: Path, links, by_target, target_to_path, apply=False):
    txt = read(p)
    fm, body = fm_split(txt)

    # compute related: backlinks + similar-by-tag (lightweight — backlinks usually enough)
    related = set()
    backs = set(by_target.get(p, []))

    # Build a compact, collapsible details block
    if not backs:
        # no backlinks? scrub any old related block and return
        if REL_START in txt and REL_END in txt:
            new = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), "", txt, flags=re.S)
            new = new.rstrip() + "\n"
            if apply and new != txt:
                write(p, new)
                return True
        return False

    def linkline(x: Path): return f"- [[{to_wikilink(base, x)}]]"

    rels = "\n".join(linkline(x) for x in sorted(backs, key=lambda z: z.as_posix()))
    block = (
        f"{REL_START}\n\n"
        "<details>\n"
        "<summary><strong>Related & Backlinks</strong></summary>\n\n"
        f"{rels}\n\n"
        "</details>\n\n"
        f"{REL_END}"
    )

    # replace existing or insert after first H1 (else append)
    if REL_START in txt and REL_END in txt:
        new = re.sub(re.escape(REL_START)+r".*?"+re.escape(REL_END), block, txt, flags=re.S)
    else:
        m = re.search(r"(?m)^#\s+.+", txt)
        if m:
            new = txt[:m.end()] + "\n\n" + block + "\n" + txt[m.end():]
        else:
            new = txt.rstrip() + "\n\n" + block + "\n"

    if apply and new != txt:
        write(p, new)
        return True
    return new != txt

def maybe_add_aliases(p: Path, base: Path, cfg, apply=False):
    rel = p.relative_to(base)
    stem = rel.parent.name if p.name.lower() == "index.md" else p.stem
    al_cfg = cfg.get("aliases") or {}
    add = None
    for key, arr in al_cfg.items():
        if key.lower() in stem.lower():
            add = arr; break
    if not add:
        return False

    txt = read(p)
    fm, body = fm_split(txt)
    if not fm:
        fm = "---\n---"
    current = fm_get("aliases", fm)
    if current:
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
    if not base.exists():
        print(f"[ERR] base not found: {base}")
        sys.exit(1)

    cfgp = Path(CFG)
    cfg = {}
    if cfgp.exists():
        cfg = yaml.safe_load(cfgp.read_text(encoding="utf-8")) or {}
    else:
        print(f"[WARN] {CFG} not found; using built-ins only")

    pages, links, by_target, target_to_path = collect_graph(base)

    changed = 0
    for p in pages:
        # 1) ensure FM with title
        txt = read(p)
        title = title_from(p.relative_to(base))
        fm, body = ensure_fm(txt, title)

        # 1.1) strip any visible "## Tags" sections from body
        body2 = strip_visible_tag_sections(body)
        if (fm + body2) != txt and args.apply:
            write(p, fm + body2); changed += 1
            txt = fm + body2
            fm, body = fm_split(txt)

        # 2) merge tags (and trim to MAX_TAGS_VISIBLE)
        tags_line = fm_get("tags", fm)
        cur = parse_tag_list(tags_line) if tags_line else []
        inferred = infer_tags_for(p, base, cfg)
        merged = add_tags(cur, inferred)

        visible = merged[:MAX_TAGS_VISIBLE]
        overflow = merged[MAX_TAGS_VISIBLE:]

        fm2 = fm_set("tags", "[" + ", ".join(visible) + "]", fm)

        # stash overflow into keywords (for search only, Quartz ignores for pills)
        if overflow:
            kw_existing = fm_get("keywords", fm2)
            kw_list = parse_tag_list(kw_existing) if kw_existing else []
            kw_merged = add_tags(kw_list, overflow)
            fm2 = fm_set("keywords", "[" + ", ".join(kw_merged) + "]", fm2)

        if fm2 != fm and args.apply:
            write(p, fm2 + body); changed += 1
            txt = fm2 + body

        # 3) optional aliases
        if maybe_add_aliases(p, base, cfg, apply=args.apply):
            changed += 1

        # 4) inject compact backlinks block (collapsible)
        if inject_related_block(p, base, links, by_target, target_to_path, apply=args.apply):
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
