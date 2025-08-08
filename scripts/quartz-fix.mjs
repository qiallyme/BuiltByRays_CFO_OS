// scripts/quartz-fix.mjs
// Node 18+.
// Scans /content for .md files, fixes bad/missing dates, and generates content/index.md if missing.

import { promises as fs } from "fs";
import path from "path";
import { fileURLToPath } from "url";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Config
const CONTENT_DIR = process.env.CONTENT_DIR || path.join(process.cwd(), "content");
const TODAY = new Date().toISOString().slice(0, 10); // YYYY-MM-DD

const changedFiles = [];
let createdIndex = false;

async function exists(p) {
  try { await fs.access(p); return true; } catch { return false; }
}

function slugToTitle(slug) {
  // Turn "⚙️ Full Operational Overhaul.md" -> "Full Operational Overhaul"
  return slug
    .replace(/\.[^/.]+$/, "")
    .replace(/^[_\-0-9]+/, "")
    .replace(/^[^A-Za-z0-9]+/, "")
    .replace(/[_\-]+/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

function ensureFrontmatter(content, fallbackTitle) {
  // Returns { text, changed }
  const fmMatch = content.match(/^---\n([\s\S]*?)\n---\n?/);
  let body = content;
  let fm = "";
  let changed = false;

  if (fmMatch) {
    fm = fmMatch[1];
    body = content.slice(fmMatch[0].length);
  }

  // Parse simple key: value lines (no nested YAML; we keep it basic on purpose)
  const map = {};
  if (fm) {
    fm.split("\n").forEach(line => {
      const m = line.match(/^([A-Za-z0-9_\-]+)\s*:\s*(.*)$/);
      if (m) map[m[1]] = m[2];
    });
  }

  // Fix date
  const needsDateFix = !map.date || map.date === "0" || map.date === "\"0\"" || map.date === "'0'";
  if (needsDateFix) {
    map.date = TODAY;
    changed = true;
  }

  // Ensure title exists (Quartz likes titles)
  if (!map.title || String(map.title).trim() === "") {
    map.title = fallbackTitle || "Untitled";
    changed = true;
  }

  // Rebuild frontmatter
  const rebuilt =
    "---\n" +
    Object.entries(map)
      .map(([k, v]) => `${k}: ${v}`)
      .join("\n") +
    "\n---\n" +
    body.replace(/^\n*/, ""); // tidy leading whitespace

  if (!fmMatch) changed = true;

  return { text: rebuilt, changed };
}

async function walk(dir, out = []) {
  const items = await fs.readdir(dir, { withFileTypes: true });
  for (const it of items) {
    const p = path.join(dir, it.name);
    if (it.isDirectory()) {
      await walk(p, out);
    } else if (it.isFile() && it.name.toLowerCase().endsWith(".md")) {
      out.push(p);
    }
  }
  return out;
}

async function fixMarkdownFrontmatter() {
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

async function generateIndexIfMissing() {
  const indexPath = path.join(CONTENT_DIR, "index.md");
  if (await exists(indexPath)) return;

  // Build a simple section list of top-level folders
  const top = await fs.readdir(CONTENT_DIR, { withFileTypes: true });
  const sections = [];
  for (const it of top) {
    if (it.isDirectory()) {
      const folder = it.name;
      // Gather first-level .md files inside that folder
      const folderPath = path.join(CONTENT_DIR, folder);
      const entries = await fs.readdir(folderPath, { withFileTypes: true });
      const mdLinks = [];
      for (const e of entries) {
        if (e.isFile() && e.name.toLowerCase().endsWith(".md")) {
          const rel = `/${folder}/${e.name.replace(/\.md$/i, "")}`;
          mdLinks.push(`- [${slugToTitle(e.name)}](${rel})`);
        }
      }
      if (mdLinks.length > 0) {
        sections.push(`## ${slugToTitle(folder)}\n${mdLinks.join("\n")}`);
      }
    }
  }

  const indexMd =
`---
title: Home
date: ${TODAY}
---

# BuiltByRays™ Client Portal

Welcome. Choose a section below, or use the sidebar.

${sections.join("\n\n")}
`;

  await fs.writeFile(indexPath, indexMd, "utf8");
  createdIndex = true;
}

(async () => {
  const ok = await exists(CONTENT_DIR);
  if (!ok) {
    console.error(`❌ Content directory not found: ${CONTENT_DIR}`);
    process.exit(1);
  }

  await fixMarkdownFrontmatter();
  await generateIndexIfMissing();

  console.log("\n✅ Quartz fix complete.");
  if (changedFiles.length) {
    console.log(`• Updated frontmatter in ${changedFiles.length} file(s):`);
    changedFiles.forEach(f => console.log("  - " + f));
  } else {
    console.log("• No frontmatter changes needed.");
  }
  if (createdIndex) {
    console.log("• Created content/index.md");
  } else {
    console.log("• content/index.md already present");
  }
  console.log("");
})();
