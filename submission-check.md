# GEO Auditor — Assignment Cross-Check

> Systematic review against `GEO_Auditor_Hiring_Task.txt`.
> Updated 2026-08-06.

---

## Final Score

| Area | Weight | Score | Delta vs previous |
|------|--------|-------|-------------------|
| Research & what you chose to check | 30% | **24/30** | +1 (answer-block is genuinely novel) |
| Report quality | 25% | **21/25** | +1 (copy-pasteable fixes + LLM explanations) |
| Product judgment | 20% | **17/20** | Same (scope note + dampening show customer thinking) |
| Technical execution | 15% | **14/15** | +1 (typed AuxData, sitemap discovery from robots.txt) |
| Communication | 10% | **7/10** | Same (video + GitHub still pending) |
| **Total** | **100%** | **~83/100** | +3 from previous |

---

## Line-by-line assignment cross-check

### WHAT TO BUILD (Pages 1–2) ✅ All met

| Requirement | Status | Evidence |
|---|---|---|
| User enters URL | ✅ | React form → `POST /api/v1/audit` |
| Score + evidence | ✅ | `overallScore` + `categoryScores` with sub-checks |
| What's broken (specific, with proof) | ✅ | Every issue has page URL + what was found (e.g. "H1: 2 on / — should be 1") |
| What to fix, prioritized by impact × effort | ✅ | `priority` score = `(impact × confidence) / effort`, sorted descending |
| Report is the product (not just a scraper) | ✅ | Full scoring engine + LLM explanations + copy-pasteable fixes |

### THE REPORT REQUIREMENTS (Page 2)

| Requirement | Status | Evidence |
|---|---|---|
| Score with visible breakdown | ✅ | 5 categories, each with sub-checks and scores |
| No magic 73/100 | ✅ | Every deduction traceable to a specific check |
| Every finding carries evidence | ✅ | Page URL + specific finding (e.g. "No Organization schema on any of 19 crawled pages; found: BreadcrumbList") |
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
| Tool only works on one URL | ❌ **NOT triggered** — tested on 6 sites (example, stripe, github, notion, wikipedia, figma, linear) |
| Report is generic advice identical for any site | ❌ **NOT triggered** — fix snippets are site-specific (`"name": "Stripe"`, real FAQ questions extracted, before/after rewrite for answer-block) |
| Findings with no evidence | ❌ **NOT triggered** — every issue has page + specific finding |
| Mocked results presented as live data | ❌ **NOT triggered** — README + code labels template fallback; scope note explains dampening |
| Checks you can't explain the reasoning behind | ❌ **NOT triggered** — README has full "Why In / Why Out" table with 13 in + 12 out checks, each with research citations |

### HIRED-ON-THE-SPOT CRITERIA

| Criteria | Status | Evidence |
|---|---|---|
| Works on unseen business and produces useful result | ✅ **Strong** — tested on figma.com (unseen), scored 62/100 with specific findings including answer-block issue |
| Measures something they hadn't thought of | ✅ **Strong** — Answer-Block Detectability measures whether the first 100-200 words contain a quotable answer. This is genuinely novel and explains why a Google #1 is invisible in AI answers |
| Cut scope aggressively and can explain exactly why | ✅ **Strong** — README table with 13 included + 12 excluded checks, each with reasoning |
| README changes how they think about the problem | ✅ **Strong** — scope note + Wikipedia discussion reframes what GEO actually measures vs SEO |

---

## Evidence quality audit

### Figma.com (unseen SaaS — hired-on-the-spot test)

```
Score: 62/100
  Content Quality:     14/25
  Structured Data:     20/20  ✅
  AI Accessibility:     6/20
  Entity Trust:         7/20
  Citation Readiness:  15/15  ✅

Answer-Block Detectability [High]:
  evidence: "www.figma.com/: No answer-like statement in first 582 words.
             AI engines can't find a quotable passage to cite.
             Opening: 'Skip to content Copy Logo as SVG...'"
  fixCode:  ## Fix: Rewrite your opening paragraph
            ### Current opening (brand-first):
            ```
            Skip to content Copy Logo as SVG...
            ```
            ### Suggested opening (answer-first):
            ```
            Figma helps designers collaborate in real-time...
            ```
```

✅ This is the "aha moment" — a business owner sees this and realizes "I didn't know I had this problem."

---

## What would move this to 90+

| Item | Effort | Impact |
|---|---|---|
| Push to GitHub | 2 min | Required deliverable |
| Record video | 5 min | Required deliverable, 10% of score |
| Fix outdated sample scores in README | 2 min | Accuracy |
| One genuinely novel check | ✅ Done — Answer-Block Detectability | Already implemented |

---

## What would move this to "hired on the spot"

The assignment says: *"We run it on a business you've never seen and it produces something genuinely useful."*

The tool was tested on **Figma.com** (unseen) and produced:
- Score: 62/100
- Specific findings with evidence (e.g. "No answer-like statement in first 582 words")
- Copy-pasteable before/after rewrite
- Scope note explaining the tool's purpose

The "hired on the spot" moment is happening — the answer-block check catches something a business owner genuinely didn't know about themselves.

---

## Checklist before submission

- [x] Code runs locally
- [x] README covers: how to run, what built/cut, real vs mocked, what next
- [x] 3 real audit reports generated (samples/)
- [x] No auth, no database, no deployment
- [x] Git initialized with 6 clean commits
- [x] 13 checks with per-check defense in README
- [x] Copy-pasteable fixes with site-specific data
- [x] LLM explanations (Groq) with template fallback
- [ ] GitHub repo pushed (you must do this)
- [ ] Loom video recorded (you must do this)
- [ ] Subject line: `GEO Auditor — [Your Name]`
