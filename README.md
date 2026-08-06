# GEO Auditor — AI Citation Readiness Analyzer

A tool that audits websites for AI search visibility. Enter a URL → get a scored report showing what's broken and what to fix, with copy-pasteable recommendations.

## Quick Start (< 5 minutes)

```bash
# 1. Install backend dependencies
pip install -r backend/requirements.txt

# 2. Start the backend
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000

# 3. In another terminal — install & start frontend
cd frontend
npm install
npm run dev

# 4. Open http://localhost:3000
```

Or use the API directly:

```bash
curl -X POST http://localhost:8000/api/v1/audit \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'
```

Swagger docs: http://localhost:8000/docs

---

## What It Does

When you enter a website URL, the GEO Auditor:

1. **Crawls** the homepage + key pages (up to 20 pages, depth 2)
2. **Checks** 12 GEO signals across 5 categories
3. **Scores** the site 0–100 with a transparent breakdown
4. **Reports** specific issues with evidence and copy-pasteable fixes

---

## The 12 Checks (by category)

### Content Quality (25 pts)
| Check | What it checks | Why it matters |
|-------|---------------|----------------|
| Title Tag | `<title>` present, ≤60 chars | Strongest retrieval signal for AI |
| Meta Description | `<meta name="description">` | Context for AI summaries |
| Heading Structure | One H1, logical H2/H3 | Helps AI extract answer sections |
| Content Freshness | Visible last-modified dates | AI prefers recent content |
| **Answer-Block Detectability** *(new)* | First 100-200 words contain a quotable answer | AI engines cite the first answer-like passage; if buried, the page is skipped |

### Structured Data (20 pts)
| Check | What it checks | Why it matters |
|-------|---------------|----------------|
| Organization Schema | JSON-LD `@type: Organization` | AI identifies your brand |
| FAQ Schema | `FAQPage` JSON-LD or visible Q&A | Cited 3.2× more often by AI |
| Article Schema | `Article`/`BlogPosting` JSON-LD | Author + date signals |
| Breadcrumb Schema | `BreadcrumbList` JSON-LD | Site hierarchy context |

### AI Accessibility (20 pts)
| Check | What it checks | Why it matters |
|-------|---------------|----------------|
| robots.txt | AI bots not blocked | GPTBot, ClaudeBot, etc. must access pages |
| llms.txt | `/llms.txt` exists and valid | Emerging standard for AI crawlers |
| sitemap.xml | `/sitemap.xml` with URLs | Helps AI discover pages |

### Entity Trust (20 pts)
| Check | What it checks | Why it matters |
|-------|---------------|----------------|
| NAP Consistency | Name/Address/Phone uniform | Consistent entity = higher trust |

### Citation Readiness (15 pts)
Composite score derived from FAQ + Article schema, meta description, and title presence.

---

## Report Schema

```json
{
  "executiveSummary": "Your site scores 42/100...",
  "overallScore": 42,
  "categoryScores": [
    {"category": "Content Quality", "score": 10, "max_score": 25, "checks": [...]},
    {"category": "Structured Data", "score": 13, "max_score": 20, "checks": [...]},
    {"category": "AI Accessibility", "score": 0, "max_score": 20, "checks": [...]},
    {"category": "Entity Trust", "score": 4, "max_score": 20, "checks": [...]},
    {"category": "Citation Readiness", "score": 15, "max_score": 15, "checks": [...]}
  ],
  "issues": [
    {
      "id": 1,
      "title": "Organization Schema",
      "page": "https://example.com",
      "severity": "High",
      "evidence": "No Organization schema found",
      "recommendation": "Add Organization JSON-LD schema with name, logo, and contact info...",
      "impact": 10,
      "confidence": 1.0,
      "effort": "Low",
      "estimatedScoreGain": 10,
      "priority": 3.0
    }
  ],
  "priority": [...],
  "generatedAt": "2026-08-06T10:50:00Z"
}
```

---

## Architecture

```
backend/
├── main.py                    # FastAPI app entry point
├── config.py                  # Environment config
├── models.py                  # Pydantic models (contracts)
├── audit_pipeline.py          # Orchestrates full audit
├── routers/
│   ├── health.py              # GET /health
│   ├── audit.py               # POST /api/v1/audit
│   └── frontend.py            # Serve frontend
├── crawler/
│   ├── url_utils.py           # URL validation
│   ├── fetcher.py             # Async HTTP fetcher
│   ├── extractor.py           # HTML → structured Page model
│   └── service.py             # Crawl orchestration
├── checks/
│   ├── base.py                # Abstract check base class
│   ├── robots_txt.py          # robots.txt check
│   ├── llms_txt.py            # llms.txt check
│   ├── sitemap.py             # sitemap.xml check
│   ├── title.py               # Title tag check
│   ├── meta_description.py    # Meta description check
│   ├── organization_schema.py # Organization JSON-LD check
│   ├── faq_schema.py          # FAQ schema check
│   ├── article_schema.py      # Article schema check
│   ├── breadcrumb_schema.py   # Breadcrumb schema check
│   ├── headings.py            # Heading structure check
│   ├── nap_consistency.py     # NAP consistency check
│   └── freshness.py           # Content freshness check
├── scoring/
│   └── engine.py              # Category + overall scoring
├── llm/
│   └── service.py             # LLM explanations (w/ template fallback)
└── report/
    ├── generator.py           # JSON report assembly
    └── html.py                # HTML report renderer

frontend/
├── package.json               # React + Vite
├── vite.config.js             # Dev server + API proxy
├── index.html                 # Entry point
└── src/
    ├── main.jsx               # React mount
    ├── index.css              # Dark theme styles
    ├── App.jsx                # Main app component
    └── components/
        ├── ScoreCard.jsx      # Big score display
        ├── CategoryGrid.jsx   # Category breakdown cards
        └── IssueList.jsx      # Issue cards with severity
```

---

## What's Real vs Mocked

| Component | Status |
|-----------|--------|
| URL crawling | **Real** — async httpx, respects robots.txt |
| HTML parsing | **Real** — BeautifulSoup4 extracts text, headings, metadata, JSON-LD |
| 12 GEO checks | **Real** — deterministic rules, no guessing |
| Scoring engine | **Real** — fixed weights per SCORING_ENGINE.md |
| LLM explanations | **Templates** — falls back to pre-written explanations when no OpenAI API key is set |
| Report generation | **Real** — JSON + HTML + React UI |

To enable LLM explanations, set `OPENAI_API_KEY` in your environment.

---

## Why Each Check Is Here (and Why Others Were Cut)

The assignment says *"go deep, not wide"* and *"defend every check in the README."* Here's my reasoning.

### Checks that made the cut

| Check | Why it's in | Research basis |
|-------|------------|---------------|
| **Organization Schema** | The single strongest entity signal for AI. Without it, LLMs can't connect your content to your brand. This is the #1 thing missing on most sites. | Schema.org docs; LLMs use Knowledge Graph data which relies on structured entity info |
| **FAQ Schema** | Pages with FAQPage markup are cited ~3.2× more often by AI assistants. Even if you don't have a dedicated FAQ page, adding one is the highest-leverage fix. | ZipTie 2026 study on FAQ vs AI citations; industry data on answer-extraction patterns |
| **robots.txt AI-bot blocking** | Many businesses inadvertently block GPTBot, ClaudeBot, or PerplexityBot. This makes them completely invisible to AI search — the exact problem we're solving. | Google Search Central robots.txt docs; OpenAI/Claude/Perplexity bot documentation |
| **llms.txt** | An emerging standard (proposed Sep 2024, not yet widely adopted) that signals content structure to AI crawlers. Forward-looking pick — small effort, big future-proofing. | llms.txt spec (Jeremy Howard); industry coverage in Search Engine Land, Webflow |
| **sitemap.xml** | AI crawlers use sitemaps for page discovery. Most businesses have one but it's not AI-aware (missing lastmod, no priority hints). | Sitemaps.org protocol docs; Apify GEO Actor as a reference |
| **NAP consistency** | Confused entity data (different names/addresses across pages) breaks the knowledge graph. AI can't resolve who you are if your pages disagree. | Ahrefs entity-consistency research; Google Knowledge Graph guidelines |
| **Title Tag** | Title is the single strongest retrieval signal — high title-query overlap can >2× AI citation rates. Missing title = invisible to extraction. | AI citation rate studies; Google's own documentation on title importance |
| **Meta Description** | AI models use meta descriptions to verify context and generate summaries. Missing descriptions = AI guesses your content's relevance. | Google Search Central meta description guidance |
| **Heading Structure** | LLMs extract answers from heading sections. An H2 before a paragraph signals "this is an answer block." No H1 = content looks unstructured. | AI extraction pipeline behavior; content hierarchy in RAG systems |
| **Answer-Block Detectability** | Measures whether the opening 100-200 words contain a direct, quotable answer. Most SMB sites open with brand language ("We are a mission-driven company...") instead of a direct answer ("We help X achieve Y by Z"). AI search engines extract the first quotable passage — if it's buried past 300 words, the page is skipped entirely. This is the #1 reason a Google #1 result is invisible in AI answers. | Ahrefs 2025 AI citation study (cited passages average 18 words, must appear early); Google AI Overview design (system extracts first quotable paragraph) |
| **Freshness** | AI assistants prefer citing recent content — cited URLs are 25.7% fresher than organic SERP results. | Ahrefs AI freshness study (2025) |
| **Article Schema** | For blog/news content, Article schema provides datePublished, author, and headline — all signals that increase AI citation confidence. | Schema.org Article type; Google Structured Data docs |
| **Breadcrumb Schema** | Lower-value but very cheap to implement (5 minutes). Signals site hierarchy to crawlers. Included because effort ≈ 0. | Schema.org BreadcrumbList; Google rich results docs |

### Checks I deliberately skipped and why

| Check | Why I cut it | Honest reason |
|-------|-------------|---------------|
| **Alt text audit** | Checking every image's alt text is valuable but requires vision/caption analysis or manual inspection. Not deterministic enough for an automated tool. | Couldn't measure reliably; would produce noisy results |
| **Internal link depth** | Checking if key pages are linked from the homepage is a good crawlability signal, but we already capture link structure in the crawler. Not worth a separate check. | Already covered by crawl data; scoring overlap |
| **Page speed / Core Web Vitals** | Important for SEO, not directly relevant to AI citation readiness. AI models don't execute JavaScript or measure load time. | Out of scope for GEO |
| **Backlink analysis** | Critical for SEO authority, but requires paid APIs (Ahrefs/Moz) and is not related to AI citation readiness. | Too expensive, wrong problem |
| **Social media presence** | Helpful for entity consistency but requires API calls to Twitter/LinkedIn. Not feasible for a free tool. | API access required; out of MVP scope |
| **Content depth / word count** | Longer content can signal authority, but it's a weak proxy. Many short pages get cited frequently by AI. Not reliable as a standalone check. | Research is mixed; low signal-to-noise |
| **OpenGraph / Twitter cards** | Social metadata, not directly related to AI citation. Minor entity signal. Not worth a separate check. | Negligible AI impact |
| **Canonical tag check** | Important for preventing duplicate content in Google, but AI crawlers handle canonicals differently. Not a strong GEO signal. | Weak correlation with AI citations |
| **SSL/HTTPS check** | Standard security practice in 2026; >95% of public sites use HTTPS. The check would pass on almost every site — zero diagnostic value. | Would pass everywhere; wasted score |
| **Accessibility (a11y)** | Critical for users, not related to AI citation readiness. Different discipline entirely. | Wrong problem |
| **Mobile responsiveness** | Out of scope per the assignment ("not graded"). AI crawlers don't render mobile views. | Explicitly excluded |
| **JavaScript rendering** | We only parse static HTML. SPAs (React/Next.js) may need JS to render content, but that's a complex crawl problem out of MVP scope. | Technically hard; out of MVP |

---

## What's Real vs Mocked

| Component | Status |
|-----------|--------|
| URL crawling | **Real** — async httpx, respects robots.txt, discovers sitemaps via robots.txt directives |
| HTML parsing | **Real** — BeautifulSoup4 extracts text, headings, metadata, JSON-LD |
| 12 GEO checks | **Real** — deterministic rules, no guessing. Each produces evidence + a copy-pasteable fix snippet. |
| Scoring engine | **Real** — fixed weights per SCORING_ENGINE.md, fully transparent breakdown |
| LLM explanations | **Real** (when key is set) — Groq llama-3.3-70b generates business-friendly per-issue explanations. Falls back to templates when no key. |
| Copy-pasteable fixes | **Real** — Organization, FAQ, Article, Breadcrumb, NAP, robots.txt, llms.txt, sitemap snippets filled with detected site data |
| Report generation | **Real** — JSON API + downloadable HTML + React UI with export buttons |

---

## Run on 3 Real Websites

### 1. stripe.com — Score: 43/100
- ✅ Title tags present
- ❌ No Organization schema
- ❌ No llms.txt
- ❌ No sitemap.xml

### 2. docs.github.com — Score: 33/100
- ✅ Good heading structure
- ✅ Article pages detected
- ❌ No Organization schema
- ❌ Missing FAQ schema on FAQ content

### 3. notion.so — Score: 32/100
- ✅ Content quality OK
- ❌ No Organization schema
- ❌ No FAQ schema despite FAQ content
- ❌ No llms.txt

---

## Scope & Limitations

**This tool is designed for SMB and brand websites trying to improve their visibility in AI search.**

The score measures **GEO optimization readiness** — how well your site's technical signals (structured data, crawlability, metadata, content structure) are set up for AI discovery. It is **not** a measure of actual AI citation likelihood.

A well-known source like Wikipedia may score 30/100 because it doesn't use schema.org markup, FAQ tags, or llms.txt — but it's still the most cited source in AI answers. Why? Because it has something our checks can't measure: **authority, reputation, and being the default source AI models train on.**

**When the score is low but the site is clearly well-known**, the report includes a scope note explaining this. The tool's value is for the businesses that rank on Google but are invisible in AI answers — the ones who think they're fine because they're page 1 on Google, but ChatGPT has never heard of them.

### Content-strength dampening

When a site shows strong content quality signals (good headings, fresh content, structured metadata), Structured Data and AI Accessibility deductions are automatically reduced. The rationale: an established site with good content but missing schema.org is less invisible than a small site missing everything — AI already finds it through other means.

---

## What I'd Build Next

1. **LLM-powered recommendations** — Real OpenAI/Gemini explanations instead of templates
2. **Multi-page analysis** — Score each page individually, find the weakest pages
3. **Competitor comparison** — Compare your score against competitors
4. **Historical tracking** — Store audit results, show improvement over time
5. **Scheduled audits** — Cron-based re-auditing with email alerts
6. **AI prompt simulation** — Actually ask ChatGPT/Perplexity about the business and check if it's cited
7. **Richer entity checks** — Verify business info across Google Knowledge Graph, Wikipedia, social profiles

---

## Decisions & Tradeoffs

- **12 checks, not 30** — The docs suggested 25-35 checks, but I focused on the 12 highest-signal checks that are deterministic and measurable. Better to nail 12 than half-ship 30.
- **Templates over LLM** — Without a valid API key, the tool still works with pre-written explanations. LLM is additive, not required.
- **Single-page crawl by default** — Crawl depth is configurable (default 2), but most SMBs have <20 pages worth auditing.
- **No auth, no database** — Per the brief. Stateless, single-shot audit.
- **Dark theme UI** — Feels modern, matches developer tools aesthetic.
