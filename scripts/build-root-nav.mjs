import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const CONTENT = path.join(ROOT, "content");

// Order by numeric prefix, then name
function sectionSort(a, b) {
  const na = a.match(/^(\d{2,5})-/)?.[1] ?? "99999";
  const nb = b.match(/^(\d{2,5})-/)?.[1] ?? "99999";
  if (na !== nb) return parseInt(na) - parseInt(nb);
  return a.localeCompare(b);
}

function titleFromFolder(name) {
  return name.replace(/^\d{2,5}-/, "")
             .replace(/-/g, " ")
             .replace(/^\w/, c => c.toUpperCase());
}

async function main() {
  const items = await fs.readdir(CONTENT, { withFileTypes: true });
  const sections = [];

  for (const it of items) {
    if (!it.isDirectory()) continue;
    const folder = it.name;
    // Only include folders that have at least one .md inside (section landing counts)
    const files = await fs.readdir(path.join(CONTENT, folder));
    const hasMd = files.some(f => f.toLowerCase().endsWith(".md"));
    if (!hasMd) continue;

    sections.push(folder);
  }

  sections.sort(sectionSort);

  const lines = sections.map(f => `- [${titleFromFolder(f)}](/${f}/)`);
  const navBlock = `## Navigation\n${lines.join("\n")}\n`;

  const idxPath = path.join(CONTENT, "index.md");
  let idx = await fs.readFile(idxPath, "utf8");

  // Replace existing Navigation section or append if missing
  const navRe = /(^|\n)##\s*Navigation[\s\S]*?(?=\n##\s|\n#\s|$)/i;
  if (navRe.test(idx)) {
    idx = idx.replace(navRe, `\n${navBlock}\n`);
  } else {
    idx = idx.trimEnd() + `\n\n${navBlock}`;
  }

  await fs.writeFile(idxPath, idx, "utf8");
  console.log("✅ Root Navigation rebuilt with current folders:");
  console.log(lines.map(s => "  " + s).join("\n"));
}

await main();
