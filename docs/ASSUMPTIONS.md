ASSUMPTIONS.md

1. Product Assumptions

2. User Assumptions

3. Website Assumptions

4. Crawling Assumptions

5. GEO Assumptions

6. LLM Assumptions

7. Scoring Assumptions

8. Report Assumptions

9. Technical Assumptions

10. Constraints

11. Risks

12. Future Validation
1 Product Assumptions

Example

## Product Scope

This product is an AI Citation Readiness Auditor.

It evaluates how well a website can be understood,
retrieved and cited by AI assistants.

It is NOT

- SEO optimizer
- Keyword research tool
- Backlink checker
- Search Console replacement
- Rank tracker
2 User Assumptions
The primary user is

- Small business owner

or

- Marketing manager

The user

- does not know GEO

- does not understand schema

- needs actionable fixes

The report should require no SEO knowledge.
3 Website Assumptions

Huge one.

Assume

- Public websites

- English language

- HTML pages

- Desktop rendering

- Robots accessible

- Maximum 20 pages

- Crawl depth 2

- Static HTML available

Ignore

- Login

- Private portals

- PDFs

- Videos

- Mobile apps

- APIs

Now Claude won't try crawling PDFs.

4 Crawling Assumptions
Crawler only visits

Homepage

About

Contact

Products

Services

Blog

Pricing

FAQ

Resources

Sitemap

Never crawl

/admin

/login

/cart

/checkout

/search

/account

Maximum

20 pages

Maximum HTML

5 MB

Timeout

30 seconds
5 GEO Assumptions

This section is extremely valuable.

Example

This project assumes that AI visibility can be approximated using observable signals.

Examples

- Structured Data

- Entity consistency

- Crawlability

- Citation-ready content

- Content freshness

These are proxies.

The auditor does NOT claim to measure
actual AI ranking.

Excellent interview discussion point.

6 LLM Assumptions
LLMs

DO

Explain

Summarize

Rewrite

Generate recommendations

Generate JSON-LD

Generate HTML

LLMs

DO NOT

Calculate score

Modify evidence

Invent metadata

Invent schema

Guess missing pages

Guess robots.txt

Guess sitemap

Guess company information
7 Scoring Assumptions
Scores represent

AI Citation Readiness

NOT

Google Ranking

NOT

SEO Score

NOT

Domain Authority

NOT

Traffic

Unknown

Missing evidence

↓

Unknown

↓

No score awarded

↓

Never assume pass
8 Report Assumptions
Every issue

must include

Evidence

Impact

Effort

Recommendation

Estimated score gain

Confidence

Every recommendation

must

be copy-pasteable
mention page
mention evidence
mention why
mention expected impact

---

# 9 Technical Assumptions

This prevents architecture drift.

Example

```md
Backend

FastAPI

Frontend

React

No Database

No Auth

REST API

JSON Contracts

Stateless

No Queue

Single audit execution

No cache
10 Constraints

Example

Time available

1 day

Goal

Working MVP

Supported websites

English only

Supported content

HTML only

Deployment

Optional

Tests

Minimal

Mobile

Ignored
11 Known Risks

Very important.

Shows product thinking.

AI search ranking algorithms are proprietary.

No public API exposes citation probability.

Some GEO signals are inferred from current research.

LLMs may evolve.

llms.txt is not yet universally adopted.

Not all AI assistants parse Schema identically.

Dynamic JS-heavy websites may reduce crawl quality.

Some recommendations are heuristic.
12 Future Validation

This is what senior PMs do.

Future versions should validate assumptions by

Comparing reports

↓

Actual ChatGPT citations

↓

Perplexity citations

↓

Gemini citations

↓

Google AI Overviews

↓

Manual expert review

↓

Customer feedback

-------------------

Non-Assumptions


The system does NOT assume

- AI engines read JSON-LD directly
- llms.txt guarantees citations
- More schema always improves visibility
- More pages are always better
- Freshness alone improves AI visibility
- Missing one signal means a website cannot be cited