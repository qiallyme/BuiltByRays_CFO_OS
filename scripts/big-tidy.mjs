// scripts/big-tidy.mjs
// Big Energy content cleanup for Quartz.
// - kebab-case filenames/folders (no emojis/spaces)
// - remove desktop.ini/Thumbs.db
// - normalize frontmatter (title/date/summary/tags/status/owner/last_reviewed/weight)
// - inject "Back to Client Hub" link if CLIENT_HUB is set
// - create section index.md if missing

import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const CONTENT = path.join(ROOT, "content");
const TODAY = new Date().toISOString().slice(0,10);
const HUB_URL = process.env.CLIENT_HUB || ""; // set ENV to add backlink

const TRASH = new Set(["desktop.ini", "thumbs.db", "Thumbs.db"]);
const emojiRE = /([\p{Emoji_Presentation}\p{Emoji}\uFE0F])/gu;
const unsafeRE = /[^a-z0-9\-./]/g;

function titleCase(s) {
  return s.replace(/[-_]+/g," ").replace(/\s+/g," ").trim()
          .replace(/\b([a-z])/g,(m,c)=>c.toUpperCase());
}
function kebabify(name) {
  const ext = path.extname(name);
  let base = path.basename(name, ext);
  const m = base.match(/^(\d{2,5})[_-]?(.*)$/);
  let num = "", rest = base;
  if (m) { num = m[1]; rest = m[2]; }
  rest = rest.replace(emojiRE,"").normalize("NFKD")
             .replace(/[’'"]/g,"").replace(/[()]/g,"")
             .replace(/[&]/g," and ").replace(/[._\s]+/g,"-")
             .toLowerCase().replace(/-+/g,"-").replace(/^-|-$/g,"");
  let kebab = (num ? `${num}-${rest}` : rest);
  kebab = kebab.replace(unsafeRE,"-").replace(/-+/g,"-").replace(/^-|-$/g,"");
  return (kebab || "untitled") + ext.toLowerCase();
}
async function walk(dir, acc=[]) {
  for (const it of await fs.readdir(dir,{withFileTypes:true})) {
    const p = path.join(dir, it.name);
    if (it.isDirectory()) { acc.push({type:"dir",path:p}); await walk(p, acc); }
    else acc.push({type:"file",path:p});
  }
  return acc;
}
async function renameIfNeeded(p) {
  const dir = path.dirname(p), base = path.basename(p);
  if (TRASH.has(base)) { await fs.unlink(p).catch(()=>{}); return null; }
  const nb = kebabify(base);
  if (nb !== base) { const np = path.join(dir, nb); await fs.rename(p, np); return np; }
  return p;
}
function parseFM(text) {
  const m = text.match(/^---\n([\s\S]*?)\n---\n?/);
  if (!m) return { fm:{}, body:text };
  const fm = {}; m[1].split("\n").forEach(l=>{ const i=l.indexOf(":"); if(i>-1){ fm[l.slice(0,i).trim()] = l.slice(i+1).trim(); }});
  return { fm, body: text.slice(m[0].length) };
}
function buildFM(fm) { return `---\n${Object.entries(fm).map(([k,v])=>`${k}: ${v}`).join("\n")}\n---\n`; }
function ensureBackLink(body) {
  if (!HUB_URL) return body;
  if (body.includes(HUB_URL) || /Back to Client Hub/i.test(body)) return body;
  return `${body.trim()}\n\n---\n[← Back to Client Hub](${HUB_URL})\n`;
}
function inferWeight(base) { const m = base.match(/^(\d{2,5})[-_]/); return m ? parseInt(m[1],10) : undefined; }

async function tidyMarkdown(p) {
  const raw = await fs.readFile(p,"utf8");
  const { fm, body } = parseFM(raw);
  const base = path.basename(p).replace(/\.md$/i,"");
  const title = fm.title?.trim() || titleCase(base.replace(/^\d{2,5}-/,""));
  const weight = fm.weight ? parseInt(fm.weight,10) : inferWeight(base);
  const outFM = {
    title,
    date: (fm.date && fm.date !== "0") ? fm.date : TODAY,
    summary: fm.summary || "Summary coming soon.",
    tags: fm.tags || "[general]",
    status: fm.status || "active",
    owner: fm.owner || "Q",
    last_reviewed: fm.last_reviewed || TODAY,
    ...(weight ? { weight } : {})
  };
  let newBody = body.replace(/^\s*#\s+.*\n/, "");
  newBody = `# ${title}\n\n${newBody.trimStart()}\n`;
  newBody = ensureBackLink(newBody);
  await fs.writeFile(p, buildFM(outFM) + newBody, "utf8");
}
async function ensureIndexMd(dir) {
  const files = await fs.readdir(dir);
  const ok = files.some(f => /^_?index\.md$/i.test(f));
  if (ok) return;
  const name = path.basename(dir);
  const title = titleCase(name.replace(/^\d{2,5}-/,""));
  const md = `---\ntitle: ${title} Overview\ndate: ${TODAY}\nsummary: Overview for ${title}.\ntags: [overview]\nstatus: active\nowner: Q\nlast_reviewed: ${TODAY}\n---\n# ${title}\n\nQuick links will appear in the sidebar.\n`;
  await fs.writeFile(path.join(dir, "index.md"), md, "utf8");
}
async function main() {
  // 1) First pass: rename files
  const items = await walk(CONTENT);
  for (const it of items.filter(i=>i.type==="file").sort((a,b)=>b.path.length-a.path.length)) {
    const np = await renameIfNeeded(it.path); it.path = np || it.path;
  }
  // 2) Rename directories (deepest first)
  for (const it of items.filter(i=>i.type==="dir").sort((a,b)=>b.path.length-a.path.length)) {
    const dir = it.path, base = path.basename(dir), nb = kebabify(base);
    if (nb !== base) { const np = path.join(path.dirname(dir), nb); await fs.rename(dir, np).catch(()=>{}); it.path = np; }
  }
  // 3) Second walk & tidy markdown
  const items2 = await walk(CONTENT);
  const dirs = new Set();
  for (const it of items2) {
    if (it.type==="file" && it.path.toLowerCase().endsWith(".md")) {
      await tidyMarkdown(it.path);
      dirs.add(path.dirname(it.path));
    }
  }
  // Top-level section overviews
  for (const d of dirs) if (path.dirname(d) === CONTENT) await ensureIndexMd(d).catch(()=>{});
  console.log("✅ Big tidy complete.");
}
await main();
