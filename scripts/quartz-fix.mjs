// scripts/quartz-fix.mjs — Node 18+ / 22+
// Fix missing/bad frontmatter dates and guarantee content/index.md exists.

import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const ROOT = process.cwd();
const CONTENT_DIR = process.env.CONTENT_DIR || path.join(ROOT, "content");
const TODAY = new Date().toISOString().slice(0, 10);

const changedFiles = [];
let createdIndex = false;

async function exists(p) {
  try { await fs.access(p); return true; } catch { return false; }
}

function slugToTitle(slug) {
  return (
    slug
      .replace(/\.[^/.]+$/, "")
      .replace(/^[_\-0-9]+/, "")
      .replace(/^[^A-Za-z0-9]+/, "")
      .replace(/[_\-]+/g, " ")
      .replace(/\s+/g, " ")
      .trim() || "Untitled"
  );
}

function ensureFrontmatter(text, fallbackTitle) {
  const fmMatch = text.match(/^---\n([\s\S]*?)\n---\n?/);
  let body = text;
  let fmBlock = "";
  let changed = false;

  if (fmMatch) {
    fmBlock = fmMatch[1];
    body = text.slice(fmMatch[0].length);
  }

  const map = {};
  if (fmBlock) {
    for (const line of fmBlock.split("\n")) {
      const m = line.match(/^([A-Za-z0-9_\-]+)\s*:\s*(.*)$/);
      if (m) map[m[1]] = m[2];
    }
  }

  const needsDate = !map.date || ["0", "'0'", '"0"'].includes(String(map.date).trim());
  if (needsDate) { map.date = TODAY; changed = true; }
  if (!map.title || String(map.title).trim() === "") { map.title = fallbackTitle; changed = true; }

  const rebuilt =
`---
${Object.entries(map).map(([k, v]) => `${k}: ${v}`).join("\n")}
---
${body.replace(/^\n*/, "")}`;

  if (!fmMatch) changed = true;
  return { text: rebuilt, changed };
}

async function walkMarkdown(dir, acc = []) {
  const items = await fs.readdir(dir, { withFileTypes: true });
  for (const it of items) {
    const p = path.join(dir, it.name);
    if (it.isDirectory()) {
      await walkMarkdown(p, acc);
    } else if (it.isFile() && it.name.toLowerCase().endsWith(".md")) {
      acc.push(p);
    }
  }
  return acc;
}

async function fixAllFrontmatter() {
  if (!(await exists(CONTENT_DIR))) return;
  const files = await walkMarkdown(CONTENT_DIR);
  for (const file of files) {
    const raw = await fs.readFile(file, "utf8");
    const title = slugToTitle(path.basename(file));
    const { text, changed } = ensureFrontmatter(raw, title);
    if (changed) {
      await fs.writeFile(file, text, "utf8");
      changedFiles.push(path.relative(ROOT, file));
    }
  }
}

async function buildSectionList() {
  const sections = [];
  const top = await fs.readdir(CONTENT_DIR, { withFileTypes: true });
  for (const it of top) {
    if (!it.isDirectory()) continue;
    const folder = it.name;
    const folderPath = path.join(CONTENT_DIR, folder);
    const entries = await fs.readdir(folderPath, { withFileTypes: true });
    const links = [];
    for (const e of entries) {
      if (e.isFile() && e.name.toLowerCase().endsWith(".md")) {
        const rel = `/${folder}/${e.name.replace(/\.md$/i, "")}`;
        links.push(`- [${slugToTitle(e.name)}](${rel})`);
      }
    }
    if (links.length) {
      sections.push(`## ${slugToTitle(folder)}\n${links.join("\n")}`);
    }
  }
  return sections.join("\n\n");
}

async function ensureIndex() {
  await fs.mkdir(CONTENT_DIR, { recursive: true });
  const indexPath = path.join(CONTENT_DIR, "index.md");
  if (await exists(indexPath)) return;

  const sectionList = await buildSectionList();
  const md =
`---
title: Home
date: ${TODAY}
---
# BuiltByRays™ Client Portal

Welcome. Choose a section below, or use the sidebar.

${sectionList}
`;
  await fs.writeFile(indexPath, md, "utf8");
  createdIndex = true;
}

(async () => {
  await fixAllFrontmatter();
  await ensureIndex();

  console.log("\n✅ Quartz fix complete.");
  if (changedFiles.length) {
    console.log(`• Updated ${changedFiles.length} file(s):`);
    for (const f of changedFiles) console.log("  - " + f);
  } else {
    console.log("• No frontmatter changes needed.");
  }
  console.log(createdIndex ? "• Created content/index.md" : "• content/index.md already present");
  console.log("");
})();
