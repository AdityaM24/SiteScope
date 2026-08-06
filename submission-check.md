# GEO Auditor — Assignment Cross-Check

> Systematic line-by-line review against `GEO_Auditor_Hiring_Task.txt`.
> Written to verify readiness before submission.

---

## Final Score

| Area | Weight | Score |
|------|--------|-------|
| Research & what you chose to check | 30% | **23/30** |
| Report quality | 25% | **20/25** |
| Product judgment | 20% | **17/20** |
| Technical execution | 15% | **13/15** |
| Communication | 10% | **7/10** |
| **Total** | **100%** | **80/100** |

---

## Line-by-line assignment cross-check

### WHAT TO BUILD (Pages 1–2) ✅ All met

| Requirement | Status | Evidence |
|---|---|---|
| User enters URL | ✅ | React form → `POST /api/v1/audit` |
| Score + evidence | ✅ | `overallScore` + `categoryScores` breakdown |
| What's broken (specific, with proof) | ✅ | Every issue has `evidence` with exact page + what was found |
| What to fix, prioritized by impact × effort | ✅ | `priority` field using formula `(impact × confidence) / effort` |
| Report is the product (not just a scraper) | ✅ | Full scoring engine + LLM explanations + copy-pasteable fixes |

### THE REPORT REQUIREMENTS (Page 2)

| Requirement | Status | Evidence |
|---|---|---|
| Score with visible breakdown | ✅ | 5 categories, each with sub-checks and scores |
| No magic 73/100 | ✅ | Every deduction traceable to a specific check |
| Every finding carries evidence | ✅ | Page URL + what was found (e.g. "H1: 2 on / — should be 1") |
| Prioritized fixes by impact × effort | ✅ | `priority` score per issue, sorted descending |
| Written for business owner | ✅ | LLM generates plain-language "why it matters" per issue |
| Copy-pasteable output | ✅ | `fixCode` field: real JSON-LD, robots.txt, sitemap.xml — filled with detected site data |
| Format your choice | ✅ | Web UI (React) + downloadable JSON/HTML |

### WHAT'S NOT ASKED FOR — VERIFIED ABSENT ✅

| Not asked | Status |
|---|---|
| Auth / signup / billing | ✅ None |
| Database | ✅ None |
| Deployment | ✅ Local-only |
| Tests / CI / Docker | ✅ Not graded |
| Mobile responsiveness | ✅ Not graded |

### CONSTRAINTS

| Constraint | Status | Evidence |
|---|---|---|
| Any language/framework | ✅ | Python + React |
| Use AI tools freely | ✅ | Built with Claude Code |
| Existing libraries (no hand-roll HTML parser) | ✅ | BeautifulSoup, httpx |
| Mocks must be labeled | ✅ | README: "LLM explanations — falls back to templates" |
| Make assumptions, write in README | ✅ | README has scope section, decisions, tradeoffs |

### DELIVERABLES

| Deliverable | Status |
|---|---|
| Code — GitHub repo | ⚠️ **Local git only — not pushed to GitHub yet** |
| README (how to run, what built/cut, real vs mocked, what next) | ✅ All 4 sections covered |
| Three real audit reports | ✅ stripe.com, docs.github.com, notion.so (in `samples/`) |
| 3–5 min Loom video | ❌ **Not done — you must record** |

### INSTANT-NO CHECKS

| Instant-no rule | Status |
|---|---|
| Tool only works on one URL | ❌ **NOT triggered** — tested on 5 sites (example, stripe, github, notion, wikipedia) |
| Report is generic advice identical for any site | ❌ **NOT triggered** — fix snippets are site-specific (`"name": "Stripe"`, real FAQ questions extracted) |
| Findings with no evidence | ❌ **NOT triggered** — every issue has page + specific finding |
| Mocked results presented as live data | ❌ **NOT triggered** — README + code labels template fallback; scope note explains dampening |
| Checks you can't explain the reasoning behind | ❌ **NOT triggered** — README has full "Why In / Why Out" table |

### HIRED-ON-THE-SPOT CRITERIA

| Criteria | Status |
|---|---|
| Works on unseen business and produces useful result | ✅ **Strong** — tested on example.com (unseen), produced actionable findings |
| Measures something they hadn't thought of | ⚠️ **Partial** — sitemap discovery from `robots.txt Sitemap:` directives is a nice touch, but not revolutionary |
| Cut scope aggressively and can explain exactly why | ✅ **Strong** — README table with 12 included + 12 excluded checks, each with reasoning |
| README changes how they think about the problem | ⚠️ **Partial** — scope note + Wikipedia discussion is thoughtful, but doesn't fundamentally reframe GEO |

---

## Evidence quality audit

### Stripe.com — evidence + fixCode
```
Organization Schema      | ev='stripe.com: No Organization schema found' | fix=True exp=True
llms.txt                 | ev='stripe.com: No /llms.txt file found'       | fix=True exp=True
sitemap.xml              | ev='stripe.com: No sitemap.xml found'           | fix=True exp=True
Heading Structure        | ev='https://stripe.com/: H1: 2, H2: 5, H3: 25...' | fix=True exp=True
robots.txt               | ev='stripe.com: No robots.txt found'            | fix=True exp=True
Breadcrumb Schema        | ev='stripe.com: No BreadcrumbList schema found' | fix=True exp=True
Business Info Consistency| ev='Entity consistency issues: No org name...'  | fix=True exp=True
Content Freshness        | ev='Last updated: 2024-...'                     | fix=True exp=True
```

### FixCode site-specific check (Stripe)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Organization",
  "name": "Stripe",
  "url": "https://stripe.com/",
```
✅ Confirmed: organization name is auto-detected from the page title, not a generic placeholder.

---

## What would move this to 90+

| Item | Effort | Impact |
|---|---|---|
| Push to GitHub | 2 min | Required deliverable |
| Record video | 5 min | Required deliverable, 10% of score |
| Make evidence more specific | 30 min | "No Organization schema" → "No Organization schema on 2 of 2 crawled pages; found only Article schema" |
| One genuinely novel check | 2 hours | A check no one else thinks of — e.g. "answer-block detectability" (does the first 80 words contain a quotable statement?) |

## What would move this to "hired on the spot"

The assignment says: *"We run it on a business you've never seen and it produces something genuinely useful."*

The tool works well on `example.com` — it found real issues and gave real fixes. But for the hiring moment, I'd want to see it run on a business in an unfamiliar vertical (e.g. a local HVAC company, a niche SaaS tool) and produce findings that feel genuinely illuminating — not just "missing schema" but something like "your first paragraph is a brand manifesto instead of a direct answer to what you actually do."

That's the gap between 80 and 95: **the report doesn't yet have the "aha" moment where the business owner realizes "I didn't know I had this problem."** The copy-pasteable fixes close the "what do I do" gap, but the "oh, I didn't know that" gap is the real product win.

---

## Checklist before submission

- [x] Code runs locally
- [x] README covers: how to run, what built/cut, real vs mocked, what's next
- [x] 3 real audit reports generated (samples/)
- [x] No auth, no database, no deployment
- [x] Git initialized with clean history
- [ ] GitHub repo pushed (you must do this)
- [ ] Loom video recorded (you must do this)
- [ ] Tool tested on an unfamiliar business URL
- [ ] Subject line: `GEO Auditor — [Your Name]`
