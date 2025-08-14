---
date: 2025-08-14
title: Backend Design
---
---
date: 2025-08-14
title: Backend Design (Cloudflare Pages + D1)
tags: [analytics, performance, legal, confidentiality, technology]
---
# Backend Design (Cloudflare Pages + D1)

<!-- RELATED:START -->

## Related
**Similar by tag**
- [[01-scope/B-QiSuiteTM-Overview]]
- [[01-scope/C-Scope-of-Services]]
- [[01-scope/E-What-I-DON-T-Do]]
- [[01-scope/F-What-I-Expect-From-You]]
- [[01-scope/G-KPIs-Goals]]
- [[02-investment/A-Investment-Payment-Terms/A-Investment-and-Payment-Terms]]
- [[02-investment/A-Investment-Payment-Terms]]
- [[02-investment/B-ROI-Payment-Projection-Example/B-ROI-and-Payment-Projection-Example]]
- [[02-investment/B-ROI-Payment-Projection-Example]]
- [[.]]

<!-- RELATED:END -->










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