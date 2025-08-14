---
date: 2025-08-14
title: Backend Design
---
---
title: Backend Design (Cloudflare Pages + D1)
date: 2025-08-10
enableToc: True
tags: [backend, api, d1, cloudflare, quartz]
---
# Backend Design (Cloudflare Pages + D1)

## Data flow
1. **Source of truth:** Admin form or Google Sheet → synced to **D1.monthly_inputs**.  
2. **Compute:** Pages Function `/api/schedule` calculates monthly capped variable and weekly due.  
3. **Annual cap:** if sum of monthly variables in a calendar year exceeds **25% of GP**, apply a proportional scale factor.  
4. **History:** store snapshots in `schedule_history`.  
5. **Quartz page:** simple script fetches `/api/schedule` and renders.

## API
- `GET /api/schedule` → `{ months: [...] }` with fields per period: revenue, gp, kpi, capped variable, weekly due, etc.
- `GET /api/monthly` / `GET /api/trueup?quarter=YYYY-Q#` (optional future endpoints)
- `POST /api/actuals` (optional, auth) → write inputs.

## D1 Schema
See `cloudflare-pages/_schema.sql`.

## Cron
Use the `_worker.js` scheduled handler to pull from a Sheet or simply finalize quarterly true-ups and append to history.

## Quartz Embed
Use the snippet in `quartz-embed/schedule-embed.html` to render the schedule in content pages.