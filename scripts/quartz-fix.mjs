// scripts/quartz-fix.mjs — Node 18+
// Fixes bad/missing dates in frontmatter and ensures content/index.md exists.

import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const CONTENT_DIR = process.env.CONTENT_DIR || path.join(process.cwd(), "content");
const TODAY = new Date().toISOString().slice(0, 10);

const changedFiles = [];
let createdIndex = false;

async function exists(p) { try { await fs.access(p); return true; } catch { return false; } }

function slugToTitle(slug) {
  return slug
    .replace(/\.[^/.]+$/, "")
    .replace(/^[_\-0-9]+/, "")
    .replace(/^[^A-Za-z0-9]+/, "")
    .replace(/[_\-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim() || "Untitled";
}

function ensureFrontmatter(content, fallbackTitle) {
  const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n?/);
  let body = content;
  let fm = "";
  let changed = false;

  if (fmMatch) {
    fm = fmMatch[1];
    body = content.slice(fmMatch[0].length);
  }

  const map = {};
  if (fm) {
    for (const line of fm.split("\n")) {
      const m = line.match(/^([A-Za-z0-9_\-]+)\s*:\s*(.*)$/);
      if (m) map[m[1]] = m[2];
    }
  }

  const needsDateFix = !map.date || ["0","'0'","\"0\""].includes(String(map.date).trim());
  if (needsDateFix) { map.date = TODAY; changed = true; }
  if (!map.title || String(map.title).trim() === "") { map.title = fallbackTitle; changed = true; }

  const rebuilt = 
    "---\n" +
    Object.entries(map).map(([k,v]) => `${k}: ${v}`).join("\n") +
    "\n---\n" +
    body.replace(/^\n*/, "");

  if (!fmMatch) changed = true;
  return { text: rebuilt, changed };
}

async function walk(dir, out=[]) {
  const items = await fs.readdir(dir, { withFileTypes: true });
  for (const it of items) {
    const p = path.join(dir, it.name);
    if (it.isDirectory()) await walk(p, out);
    else if (it.isFile() && it.name.toLowerCase().endsWith(".md")) out.push(p);
  }
  return out;
}

async function fixMarkdown() {
  const files = await walk(CONTENT_DIR);
  for (const file of files) {
    const raw = await fs.readFile(file, "utf8");
    const title = slugToTitle(path.basename(file));
    const { text, changed } = ensureFrontmatter(raw, title);
    if (changed) {
      await fs.writeFile(file, text, "utf8");
      changedFiles.push(path.relative(process.cwd(), file));
    }
  }
}

async function ensureIndex() {
  const indexPath = path.join(CONTENT_DIR, "index.md");
  if (await exists(indexPath)) return;

  const top = await fs.readdir(CONTENT_DIR, { withFileTypes: true });
  const sections = [];
  for (const it of top) {
    if (!it.isDirectory()) continue;
    const folder = it.name;
    const folderPath = path.join(CONTENT_DIR, folder);
    const entries = await fs.readdir(folderPath, { withFileTypes: true });
    const mdLinks = [];
    for (const e of entries) {
      if (e.isFile() && e.name.toLowerCase().endsWith(".md")) {
        const rel = `/${folder}/${e.name.replace(/\.md$/i, "")}`;
        mdLinks.push(`- [${slugToTitle(e.name)}](${rel})`);
      }
    }
    if (mdLinks.length) sections.push(`## ${slugToTitle(folder)}\n${mdLinks.join("\n")}`);
  }

  const indexMd = `---
title: Home
date: ${TODAY}
---
# BuiltByRays™ Client Portal

Welcome. Choose a section below, or use the sidebar.

${sections.join("\n\n")}
`;
  await fs.mkdir(CONTENT_DIR, { recursive: true });
  await fs.writeFile(indexPath, indexMd, "utf8");
  createdIndex = true;
}

(async () => {
  if (!await exists(CONTENT_DIR)) {
    await fs.mkdir(CONTENT_DIR, { recursive: true });
  }
  await fixMarkdown();
  await ensure
