---
title: Quickstart Guide
date: 2025-08-08
summary: Summary coming soon.
tags: [general]
status: active
owner: Q
last_reviewed: 2025-08-08
---
# Quickstart Guide

---
date: 2025-08-08
title: QuickStart Guide
---
# Built by RAVE CFO OS - Quick Start Guide

## 1. Setup
- Install **Node.js** and **npm** on your machine.
- Unzip this package to a working folder.

## 2. Personalize for Client
1. Go to `vault/00-Home/index.md` and replace `RAISE Construction LLC` with client name.
2. Update KPIs, Payment terms, and Roadmap in `vault/02-KPIs_Goals/` and `vault/03-Payment_Incentives/`.
3. Add client logo to `electron-app/assets/logo.png`.

## 3. Build the App
- In terminal:
```bash
cd electron-app
npm install
npm run build
```
- Output `.exe` (Windows) or `.app` (Mac) will be in `dist/` folder.

## 4. Optional Cloud Sync
- Host vault as static site (GitHub Pages or Obsidian Publish).
- Update `index.html` links if using live vault updates.

## 5. Chatbot Upgrade (Future)
- Train embeddings on vault markdown using Ollama or GPT API.
- Add chatbot UI into Electron front-end for “Ask your CFO” features.

## 6. Delivery
- Send client the `.exe` file and optional PDF snapshot (export markdown to PDF for legal sign-off).

---
**Pro Tip:** Keep this vault as MASTER TEMPLATE. Clone → personalize → build for each premium client.

---
[← Back to Client Hub](https://www.builtbyrays.com/Client-Vault/portal)
