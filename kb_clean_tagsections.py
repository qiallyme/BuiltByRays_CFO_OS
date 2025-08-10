import re, sys
from pathlib import Path

base = Path(".\\content").resolve()
changed = 0

def read(p): return p.read_text(encoding="utf-8", errors="ignore")
def write(p, t):
    bak = p.with_suffix(p.suffix + ".bak2")
    if not bak.exists():
        bak.write_text(read(p), encoding="utf-8")
    p.write_text(t, encoding="utf-8")

for md in base.rglob("*.md"):
    if ".obsidian" in md.as_posix(): 
        continue
    txt = read(md)
    new = re.sub(r"(?ms)^\s*##\s*Tags\s*\n(?:- .*\n?)+", "", txt)
    # Also trim double-blank lines
    new = re.sub(r"\n{3,}", "\n\n", new)
    if new != txt:
        write(md, new)
        changed += 1
        print(f"[FIX] removed visible tag list -> {md}")

print(f"Done. Fixed {changed} files.")
