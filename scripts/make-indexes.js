import { promises as fs } from "fs";
import path from "path";

const ROOT = process.cwd();
const CONTENT = path.join(ROOT, "content");
const TODAY = new Date().toISOString().slice(0,10);
const HUB_URL = process.env.CLIENT_HUB || "https://www.builtbyrays.com/Client-Vault/portal";

const sectionCopy = {
  "00-home": ["Welcome to Your BuiltByRays™ Vault","This is your operating manual and source of truth—proposal, scope, SOPs, and live resources in one place."],
  "01-scope": ["Scope of Work & Boundaries","What I’m responsible for, how we work, and what’s out-of-scope to keep us fast and clean."],
  "02-kpis-goals": ["Goals & KPIs","Targets we’re driving toward and how we measure progress—updated as we evolve."],
  "03-investment": ["Investment","Retainer, performance incentives, and payment cadence—simple, transparent, documented."],
  "04-scenarios-usecases": ["Scenarios & Use Cases","Playbooks and examples—pricing, tax, and cash strategies for real decisions."],
  "05-faq": ["FAQ","Quick answers to the things you’ll ask more than once."],
  "06-agreement": ["Proposal & Agreement","Your signed proposal and engagement terms for quick reference."],
  "07-roadmap": ["Roadmap","Milestones, phases, and who-does-what-by-when—updated as reality shifts."],
  "08-engagements": ["Engagements","Active, completed, and proposed work streams—status at a glance."],
  "09-financials": ["Financials","Reports, statements, taxes, and artifacts—organized so audit-week isn’t scary."],
  "10-business-development": ["Business Development","Collateral, references, and external-facing material for growth moments."],
  "11-marketing": ["Marketing","Brand assets, decks, and public touchpoints—kept consistent and easy to grab."],
  "12-operations": ["Operations","SOPs, vendors, and day-to-day machinery—how we keep the wheels greased."],
  "13-human-resources": ["Human Resources","Policies, directories, and anything people-ops—clear and compliant."],
  "14-technology": ["Technology","Stack, keys, and integrations—documented so handoffs are painless."],
  "15-legal-compliance": ["Legal & Compliance","What keeps us clean—licenses, filings, and non-tax legal references."],
  "16-analytics": ["Analytics","Models, reports, and insights—what happened, why, and what’s next."],
  "99-archives": ["Archives","Cold storage—kept for history, audits, or when someone says 'find that thing'."]
};

async function ensureDir(p){ await fs.mkdir(p,{recursive:true}); }
async function exists(p){ try{ await fs.access(p); return true; } catch{ return false; } }

function fm(obj){ return `---\n${Object.entries(obj).map(([k,v])=>`${k}: ${v}`).join("\n")}\n---\n`; }
function hubButton(){ return `\n---\n[← Back to Client Hub](${HUB_URL})\n`; }

function rootIndex(){
  const front = fm({ title:"BuiltByRays™ Client Vault", date:TODAY, summary:"Your one-stop hub for proposal, scope, SOPs, live resources, and updates.", tags:"[overview]", status:"active", owner:"Q", last_reviewed:TODAY });
  return `${front}# Welcome to Your BuiltByRays™ Vault

This is your **operating manual**—the definitive source for what we agreed, how we work, and where everything lives.

## Quick Start
- **Review your Proposal & Agreement** → see the commitments and boundaries.
- **Read the Scope** → what I do, what I don’t, and how we’ll move.
- **Open the Roadmap** → milestones, timelines, and ownership.
- **Use the SOPs** → step-by-step playbooks so nothing stalls.

## Navigation
Use the sidebar or these sections:
- [Scope](/01-scope)
- [Proposal & Agreement](/06-agreement)
- [Roadmap](/07-roadmap)
- [SOPs & Operations](/12-operations)
- [Financials](/09-financials)
- [Analytics](/16-analytics)
- [FAQ](/05-faq)

Everything updates as we work. If something feels off, tag it—we fix fast.${hubButton()}`;
}

function sectionIndex(title, summary){
  const front = fm({ title, date:TODAY, summary, tags:"[overview]", status:"active", owner:"Q", last_reviewed:TODAY });
  return `${front}# ${title}

> ${summary}

## What’s here
- Overview at the top
- Key docs and links in the sidebar
- Living updates as we refine

## Tips
- Use the sidebar to jump into specific docs.
- If you don’t see something you expect, ping me—either it’s in another section or we’ll add it.${hubButton()}`;
}

async function writeRoot(){
  const p = path.join(CONTENT, "index.md");
  await ensureDir(CONTENT);
  await fs.writeFile(p, rootIndex(), "utf8");
  console.log("• Wrote root index.md");
}

async function writeSections(){
  const items = await fs.readdir(CONTENT, { withFileTypes:true });
  for (const it of items) {
    if (!it.isDirectory()) continue;
    const folder = it.name;
    const idx = path.join(CONTENT, folder, "index.md");
    if (await exists(idx)) continue;

    const meta = sectionCopy[folder];
    let title = folder.replace(/^\d{2,5}-/,"").replace(/-/g," ");
    title = title.charAt(0).toUpperCase() + title.slice(1);
    const [t, s] = meta || [title, "Overview for this section."];

    await fs.writeFile(idx, sectionIndex(t, s), "utf8");
    console.log(`• Created ${path.join(folder, "index.md")}`);
  }
}

(async () => {
  await writeRoot();
  await writeSections();
  console.log("✅ Section indexes created (no overwrites).");
})();
