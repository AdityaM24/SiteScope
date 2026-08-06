# SCORING_ENGINE.md

## Executive Summary  
The scoring engine quantifies “AI Citation Readiness” by aggregating objective signals from the website’s pages. Each metric (e.g. presence of schemas, crawlability, content quality, entity consistency, and citation readiness heuristics) is scored deterministically and weighted to produce an overall 0–100 score. This rigorous, transparent scoring ensures reproducibility and guards against hallucination: **all numeric scores come from fixed rules** (no neural generation), and LLMs contribute *only* explanatory text or confidence flags. Structured data and clear content greatly boost AI citation likelihood, so schema-related checks and content formatting carry substantial weight. Likewise, technical accessibility (robots.txt, sitemaps, llms.txt) and freshness directly affect AI crawl/index rates. The engine enforces explicit penalties for missing elements and returns detailed evidence for each issue. Scores are fully explained (no hidden points), and any AI-derived “confidence” only modulates *priority* of fixes, not the scores themselves. 

## Goals & Principles  
- **Explainability:** Each category score is break-down of check scores. The total is a weighted sum with normalization. All deductions (missing schema, outdated content, etc.) are listed with evidence, so site owners see *exactly* why points were lost.  
- **Deterministic-first:** All numeric scores and penalties arise from fixed algorithms (parsing HTML, JSON‑LD, etc.). We *never* let LLM output dictate a score. (This aligns with industry best practice: static, rule-based audits like Lighthouse use fixed criteria.)  
- **LLM-Insulated Scoring:** LLMs (e.g. ChatGPT, Claude) only provide *contextual explanations* or confidence levels for findings. They **cannot alter any numeric score**. For example, an LLM may suggest a business-friendly phrasing or highlight the importance of an issue, but the “Content Quality” or “Structured Data” score is computed purely from HTML analysis.  
- **Reproducibility:** Running the audit twice on the same input always yields the same score breakdown. No randomness or dynamic content should affect the outcome.  
- **Minimal Hallucination:** The engine avoids speculation. If a piece of information can’t be determined (e.g. an image alt-text might require vision OCR, which we skip), we mark it “unknown” or neutral. All checks either pass/fail or deduct fixed points, with no free-form LLM reasoning injected into scoring.  

## Scoring Categories & Weights  

| Category              | Weight (Max Points) | Key Checks                                    |
|-----------------------|---------------------|-----------------------------------------------|
| **Content Quality**   | 25                  | Headings, Metadata (title/desc/canonical/OG), Paragraph structure, Freshness |
| **Structured Data**   | 20                  | Schema.org types (Organization, FAQ, Article, BreadcrumbList) |
| **Crawl Accessibility** | 20                | `robots.txt`, `llms.txt`, `sitemap.xml`       |
| **Entity Trust Signals**| 20                | Organization schema & Name consistency, NAP (Name/Address/Phone) consistency, `sameAs` links |
| **Citation Readiness** | 15                 | Factual density, Q&A format, external references  |

This breakdown reflects industry research on AI visibility. For example, **structured data and freshness** dramatically increase citation likelihood: pages with up-to-date content and JSON-LD schemas were ~76–82% more likely to be cited. Proper title tags alone can more than double AI citation rate, so metadata and headings fall under Content Quality. Entity signals (consistent branding, NAP, social links) are crucial for knowledge-graph authority. Citation readiness heuristics capture factors like factual density and clear Q&A, which directly boost AI extraction. 

Each category score is the sum of its check scores, up to the category’s weight. Points are **only deducted** (no extra credit). For example, if “Content Quality” is 20/25, then 5 points of potential content score are lost for issues (detailed below). The final overall score is  
```  
score_total = round(Content + Structured + Crawl + Entity + Citation)  
```  
on a 0–100 scale. (Rounding is to nearest whole point.) The JSON report will include each category’s numeric score and list of issues.

## Check-by-Check Scoring Rules

For each check, we describe the detection logic, inputs, outputs, evidence format, max points, failure modes, and an example output JSON. (All pseudocode is illustrative.)

---

### Organization Schema (10 points)  
**Purpose:** Ensure the site declares its business entity for AI knowledge graphs.  
- **Detection (pseudocode):**  
  ```text
  org_json = findJSONLD(html, type="Organization" or "LocalBusiness")
  if org_json exists:
      score=10, passed=true
      evidence = snippet of JSON-LD with "@type": "Organization"
  else:
      score=0, passed=false
      evidence = "No Organization schema found in HTML"
  ```  
- **Inputs:** Homepage HTML (or About page if homepage lacks it).  
- **Outputs:** `passed: bool`, `score:0–10`, `evidence:string`, `recommendation`.  
- **Evidence Format:** JSON-LD snippet or error string.  
- **Scoring:** *Max 10 points*. (Zero if missing.)  
- **Failure:** Missing or invalid Organization schema. Possible error: multiple conflicting names.  
- **Example Output:**  
  ```json
  {
    "name":"OrganizationSchema",
    "score":0,
    "max_score":10,
    "passed":false,
    "evidence": "No JSON-LD block with '@type': 'Organization' found on https://example.com",
    "recommendation": "Add an Organization JSON-LD with name, logo, sameAs (social profiles) etc."
  }
  ```  
*Rationale:* Organization schema connects pages to your business entity. Without it, AI systems may not associate content with your brand (entity signals).  

---

### FAQ Schema (8 points)  
**Purpose:** Mark up Q&A content to match AI’s answer format.  
- **Detection:**  
  ```text
  faq_json = findJSONLD(html, type="FAQPage")
  if faq_json exists and list of questions ≥ 1:
      score=8
      evidence = list of question texts found
  else:
      score=0
      evidence = "No FAQPage JSON-LD found"
  ```  
- **Inputs:** Any page’s HTML where FAQs are relevant (e.g. support or about pages).  
- **Outputs:** similar structure (`score`, `passed`, etc).  
- **Evidence Format:** List of detected questions or error message.  
- **Scoring:** *Max 8 points.* If the site has an FAQ section visible but no schema, score 0 and issue “Missing FAQ schema”.  
- **Failure:** No `FAQPage` schema.  
- **Example Output:**  
  ```json
  {
    "name":"FAQSchema",
    "score":0,
    "max_score":8,
    "passed":false,
    "evidence": "Found FAQ section but no FAQPage schema on https://example.com/faqs",
    "recommendation": "Add FAQPage JSON-LD for the FAQ content. Include each question and acceptedAnswer as JSON-LD."
  }
  ```  
*Rationale:* Pages with FAQ schema were cited ~3.2× more often by AI assistants. FAQ markup provides a clear Q&A structure that AI loves.

---

### Article Schema (5 points)  
**Purpose:** Identify editorial content (news/blog) for context and freshness.  
- **Detection:**  
  ```text
  art_json = findJSONLD(html, type="Article" or "NewsArticle" or "BlogPosting")
  if art_json exists:
      score=5
      evidence = "Found Article schema with headline: '"+ art_json.headline +"'"
  else:
      score=0
      evidence = "No Article/BlogPosting JSON-LD found"
  ```  
- **Scoring:** *Max 5 points.*  
- **Failure:** No Article schema on a blog or news page.  
- **Example Output:**  
  ```json
  {
    "name":"ArticleSchema",
    "score":5,
    "max_score":5,
    "passed":true,
    "evidence": "Article schema present (headline: 'Our Company History')",
    "recommendation": ""
  }
  ```  
*Rationale:* Article schema signals authorship, date, and topic to AIs. AI models cite content with article schema more often since they can verify date/author.

---

### Breadcrumbs Schema (3 points)  
**Purpose:** Reveal site hierarchy for better indexing.  
- **Detection:**  
  ```text
  bc_json = findJSONLD(html, type="BreadcrumbList")
  if bc_json exists:
      score=3
      evidence = JSON-LD snippet of breadcrumb items
  else:
      score=0
      evidence = "No BreadcrumbList schema found"
  ```  
- **Scoring:** *Max 3 points.*  
- **Failure:** Missing breadcrumbs schema (particularly if site has breadcrumb navigation).  
- **Example Output:**  
  ```json
  {
    "name":"BreadcrumbSchema",
    "score":0,
    "max_score":3,
    "passed":false,
    "evidence": "No BreadcrumbList schema on https://example.com",
    "recommendation": "Consider adding BreadcrumbList JSON-LD for hierarchical navigation."
  }
  ```  
*Rationale:* While less critical than Organization or FAQ, breadcrumb markup helps AI bots understand page context (schema.org best practice). A proper BreadcrumbList can indirectly boost findability.

---

### robots.txt (3 points)  
**Purpose:** Ensure crawlers (search & AI) can access the site.  
- **Detection:**  
  ```text
  try:
      robots_txt = GET("https://domain/robots.txt")
      if status 200:
          parse lines for Disallow
          score=3
          evidence = list of Disallow rules (or "no rules" if empty)
          if any rule = "Disallow: /":
              note high impact issue
      else:
          score=1 (exists but not accessible), evidence="robots.txt returned status X"
  except network error:
      score=0, evidence="robots.txt not found or unreachable"
  ```  
- **Scoring:** *Max 3 points.* Deduct 3 points if unreachable or disallowing entire site. Even if absent, assume default “allow all” (score 0 or 1).  
- **Failure:** No robots.txt or it blocks the whole site (AI crawlers typically honor `robots.txt`).  
- **Example Output:**  
  ```json
  {
    "name":"RobotsTXT",
    "score":1,
    "max_score":3,
    "passed":false,
    "evidence": "robots.txt retrieved. Disallow: /admin/, /login/",
    "recommendation": "Ensure robots.txt does not block public pages needed by AI (e.g. allow /\nUser-agent: *\nAllow: /)."
  }
  ```  
*Rationale:* A robots.txt tells crawlers what to fetch. AI agents (especially those fetching via Google/Bing) will follow it. An overly restrictive file could prevent AI from accessing content.

---

### llms.txt (5 points)  
**Purpose:** Provide LLM-specific crawl hints (emerging standard).  
- **Detection:**  
  ```text
  try:
      llms = GET("https://domain/llms.txt")
      if status 200:
          score=5
          evidence = "llms.txt found. Summary: " + first100Chars(llms)
      else:
          score=0
          evidence = "llms.txt not found"
  except:
      score=0, evidence="llms.txt inaccessible"
  ```  
- **Scoring:** *Max 5 points.* (No penalty if missing, but bonus if present.)  
- **Failure:** Missing file.  
- **Example Output:**  
  ```json
  {
    "name":"LLMsTXT",
    "score":0,
    "max_score":5,
    "passed":false,
    "evidence": "No llms.txt at root (checked https://example.com/llms.txt)",
    "recommendation": "Add an llms.txt (Markdown format) to guide AI crawlers."
  }
  ```  
*Rationale:* `llms.txt` is a proposed Markdown protocol to help AI bots find key content. While adoption is nascent, including it is a forward-looking best practice. 

---

### sitemap.xml (3 points)  
**Purpose:** List site URLs and lastmod dates for AI discovery.  
- **Detection:**  
  ```text
  try:
      sitemap = GET("https://domain/sitemap.xml")
      if status 200:
          urls = parseXML(sitemap, tag="loc")
          score=3
          evidence = "Found N URLs in sitemap.xml"
      else:
          score=0
          evidence = "No sitemap.xml found"
  except:
      score=0, evidence="sitemap.xml inaccessible"
  ```  
- **Scoring:** *Max 3 points.* Penalize if missing.  
- **Failure:** No sitemap or empty.  
- **Example Output:**  
  ```json
  {
    "name":"SitemapXML",
    "score":3,
    "max_score":3,
    "passed":true,
    "evidence": "sitemap.xml found with 12 entries (<lastmod> present on 8 pages)",
    "recommendation": ""
  }
  ```  
*Rationale:* Sitemaps help AI systems “quickly understand your site’s structure” and prioritize fresh or important pages via `<lastmod>`.

---

### Metadata (Title/Description/Canonical/OG/Twitter) – Combined (10 points)  
**Purpose:** Ensure key HTML metadata for context and branding. In particular, **title** and **description** help retrieval; canonical and social tags aid accuracy.  
- **Detection:**  
  ```text
  title = extractTag(html,"title")
  desc = extractMeta(html,"description")
  canon = extractLink(html,"canonical")
  og = extractMeta(html,"og:title")
  twitter = extractMeta(html,"twitter:title")
  score=0
  if title exists: score+=3
  if desc exists: score+=2
  if canon exists: score+=2
  if og or twitter exists: score+=3 (max total 10)
  evidence = list of found values or missing notices
  ```  
- **Scoring:** *Max 10 points total:* Title (3), Description (2), Canonical (2), OG/Twitter tags (3).  
- **Failure:** Missing title or description is a big penalty. E.g. no title yields −3.  
- **Example Output:**  
  ```json
  {
    "name":"Metadata",
    "score":5,
    "max_score":10,
    "passed":false,
    "evidence": "Title: 'Example Site'; Description missing; Canonical: 'https://example.com'; OG not set; Twitter not set",
    "recommendation": "Add a concise title and meta description. Ensure <link rel=\"canonical\"> is correct. Add OpenGraph/Twitter tags for social context."
  }
  ```  
*Rationale:* Page **titles** are the single strongest retrieval signal for AI (high title–query overlap can >2× AI citations). Descriptions and canonicals ensure content is presented consistently. Social tags help indirect visibility.

---

### Heading Structure (5 points)  
**Purpose:** Validate logical HTML headings to aid AI parsing.  
- **Detection:**  
  ```text
  h1s = countTags(html,"h1")
  h2s = countTags(html,"h2")
  h3s = countTags(html,"h3")
  score=5
  if h1s != 1: deduct 5 (score=0); evidence note = "Found X H1 tags"
  if any skipped levels (e.g. H2 without H1): evidence note
  else: evidence "Headings H1,H2,... ok"
  ```  
- **Scoring:** *Max 5 points.* Deduct full 5 if improper structure (e.g. missing H1 or multiple H1).  
- **Failure:** No H1 or multiple H1s. Also flag any non-sequential jumps (e.g. H3 immediately under H1).  
- **Example Output:**  
  ```json
  {
    "name":"HeadingStructure",
    "score":0,
    "max_score":5,
    "passed":false,
    "evidence": "2 H1 tags found; unclear heading hierarchy",
    "recommendation": "Use exactly one <H1>. Use H2/H3 for subtopics in order."
  }
  ```  
*Rationale:* LLMs rely on clear headings to understand content hierarchy. A page with one H1 and nested H2/H3 is easier to parse than a wall of text.

---

### Entity Consistency (10 points)  
**Purpose:** Check that key entity information (company name, NAP, social profiles) is consistent across pages and schema.  
- **Detection:**  
  ```text
  names = findStrings(html_all_pages, "BusinessName or Organization name")
  address = findStrings(html_all_pages, addressRegex)
  phone = findStrings(html_all_pages, phoneRegex)
  schema_names = findAll(JSONLD, type="Organization", field="name")
  score=10
  if inconsistent name/address across pages or schema mismatch: deduct (e.g. score=5)
  evidence = list of detected values and mismatches
  ```  
- **Scoring:** *Max 10 points.* Deduct for any mismatch. For example, if homepage says “ACME Corp” but Organization schema says “ACME, Inc.”, penalize. Similarly, if address or phone differs across pages.  
- **Failure:** Conflicting entity details.  
- **Example Output:**  
  ```json
  {
    "name":"EntityConsistency",
    "score":5,
    "max_score":10,
    "passed":false,
    "evidence": "Organization name appears as 'Acme Corp' on homepage and 'ACME Corporation' in schema; phone number differs on Contact page",
    "recommendation": "Use a single canonical business name and contact info across all content and schema."
  }
  ```  
*Rationale:* Consistent entity signals (NAP and `sameAs` links) let AI recognize your brand in knowledge graphs. Inconsistency confuses entity resolution and can lose citations.

---

### Content Freshness (7 points)  
**Purpose:** Favor recently updated content (AI prefers fresh info).  
- **Detection:**  
  ```text
  lastmod = extractMeta(html,"dateModified") or extractJSONLD(html,"dateModified")
  now = today’s date
  delta = now - lastmod
  if lastmod found:
      if delta <=30 days: score=7
      else if delta <=180: score=4
      else: score=1
      evidence = "Last updated X days ago"
  else:
      score=0, evidence = "No update date found"
  ```  
- **Scoring:** *Max 7 points.* Linear or tiered decay by age.  
- **Failure:** No update indicator or very old content.  
- **Example Output:**  
  ```json
  {
    "name":"Freshness",
    "score":4,
    "max_score":7,
    "passed":true,
    "evidence": "Page 'About Us' last modified 120 days ago",
    "recommendation": "Update content within the last 30 days to maximize AI visibility."
  }
  ```  
*Rationale:* AI Overviews heavily favor recent information. Pages updated in the last month get ~76–82% higher citation rates compared to stale content.

---

### Citation Readiness (10 points)  
**Purpose:** Measure how well content is structured for direct answering. (This is a heuristic composite.)  
- **Sub-checks (each contributes partial points):**  
  - **Factual Density:** Count numbers/statistics and quoted claims. For example, count `<span class="stat">` or regex for numbers.  
    - *Pseudocode:*  
      ```text
      facts = regexCount(html,"\\d+(\\.\\d+)?")  // number of numeric facts
      quotes = count(html, "<blockquote>")
      if facts+quotes >= N: add points; else deduct.
      ```  
    - Evidence: “X numeric facts; Y blockquotes found.”  
  - **Q&A Format:** Detect if page has a question-oriented heading. E.g. if H2 text ends with “?” or starts with a Wh-word, award points.  
    - *Pseudocode:*  
      ```text
      q_headings = count(html, regex="<h[2-3]>.*\\?</h[2-3]>")
      score += (q_headings > 0 ? +2 : 0)
      evidence = "Found Y headings in question form"
      ```  
  - **References:** Count external links to reputable domains (not counting menu or footer links).  
    - *Pseudocode:*  
      ```text
      ext_links = findLinks(html, external only)
      authoritative = filter(ext_links, domain in known_list)
      score += min(authoritative.count,3)  // up to 3 points
      evidence = "Found X external references"
      ```  
  - **Conciseness:** Check if paragraphs are reasonably short (e.g. <100 words). Deduct points if most paragraphs are very long.  
    - *Pseudocode:*  
      ```text
      para_lengths = map(html, toParagraphLengths)
      if any(length>150 words for majority of paras): deduct 2
      evidence = "Paragraph length average N words"
      ```  
- **Scoring:** *Max 10 points (sum of sub-checks).* For simplicity, you might allocate ~3–4 points per sub-aspect.  
- **Failure:** Pages with dense, unstructured text (low fact count, no questions, no references) get low scores.  
- **Example Output (combined):**  
  ```json
  {
    "name":"CitationReadiness",
    "score":6,
    "max_score":10,
    "passed":true,
    "evidence": "Stats found: 5; blockquotes: 1; Questions in headings: 2; External references: 1",
    "recommendation": "Increase factual statements and explicit Q&A. Add at least 2-3 factual references (e.g. links to studies) to boost citation confidence."
  }
  ```  
*Rationale:* AI systems prioritize clear, answer-like content. High factual density (statistics, quotes) increases selection by ~22–37%. Question-and-answer formatting aligns with AI output structure.

---

## Score Aggregation & Normalization  

Each category’s raw score (sum of its check points) is multiplied by its weight and summed. In practice, since weights sum to 100, we simply add them.  For instance:  

```text
Overall Score = ContentScore + StructuredScore + CrawlScore + EntityScore + CitationScore
```

Then round to the nearest integer. The report JSON will present the overall score and per-category scores. For example:  
```json
{
  "overall_score":82,
  "categories": {
    "Content Quality":18,
    "Structured Data":15,
    "AI Accessibility":20,
    "Entity Trust":19,
    "Citation Readiness":10
  },
  ...
}
```  

### Partial Crawl & Missing Page Rules  
- If the crawler retrieves <50% of expected pages (e.g. fails most secondary pages), flag the report as **Partial** and note incomplete coverage in the JSON. Content Quality (and related sub-scores) should be scaled by the percentage of pages scanned.  
- Timeouts or 5xx errors on pages: those pages are skipped; the missing content contributes 0 points and a warning “Page X could not be retrieved.”  
- A missing homepage (HTTP error) is a fatal error for the audit.  
- robots.txt or llms.txt fetching errors (other than 404) do not halt the audit but result in 0 score for that check with evidence.  

### LLM Output and Confidence Integration  
LLMs (e.g. ChatGPT) may provide **explanations** or draft recommendations, but **cannot change numeric scores**. Instead, each recommendation from an LLM comes with a confidence or priority factor. We define:  

- **Base Priority Score** = Impact × (ScoreGain) / Effort  (all deterministic values).  
- **Adjusted Priority** = Base Priority × LLMConfidence.  

The `LLMConfidence` (0.0–1.0) comes from the LLM’s tone or explicit output. A lower confidence (e.g.  “probably”, “may”) slightly lowers priority, but **does not subtract from the points**. Thus, confidence only reorders which fixes to tackle first, never affects category scores.  

## Example Test Cases  

- **Case 1: Organization Schema Present**  
  ```html
  <html><head>
    <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"Organization","name":"Acme Corp","url":"https://acme.example"}
    </script>
    <title>Acme Corp - Home</title>
  </head><body>...</body></html>
  ```  
  *Expected:* OrganizationSchema score=10 (passed), evidence snippet includes `"@type":"Organization"`, Content Quality score ≥3 (title present).  

- **Case 2: Missing Title Tag**  
  ```html
  <html><head>
    <script type="application/ld+json">
      {"@context":"https://schema.org","@type":"Article","headline":"News"}
    </script>
  </head><body>Sample content</body></html>
  ```  
  *Expected:* Metadata score lowered (title missing: -3 points), ArticleSchema score=5, evidence notes missing title, Article schema found.  

- **Case 3: Freshness and Facts**  
  ```html
  <html><body>
    <p>Our company was founded in 1990 and now has over 1,000 employees.</p>
    <h2>What services do we offer?</h2>
    <p>We provide X and Y.</p>
  </body></html>
  ```  
  (Assume `lastmod` = 10 days ago)  
  *Expected:* Freshness close to max (recent date). CitationReadiness score high: factual density (two numeric facts), presence of a question heading → at least 5/10.  

## Priority Matrix (Example)  
Below is a sample mermaid diagram of how scores combine into the final rating:

```mermaid
graph LR
  CQ[Content Quality: 25] --> Score[Overall Score (100)]
  SD[Structured Data: 20] --> Score
  CA[Crawl Accessibility: 20] --> Score
  ET[Entity Trust: 20] --> Score
  CR[Citation Readiness: 15] --> Score
```

The JSON output will contain both the numeric breakdown and detailed **issues** with severity, evidence, and fix effort. For instance, an issue entry:

```json
{
  "issue":"Missing FAQ schema",
  "page":"/faqs",
  "severity":"High",
  "evidence":"FAQ section present but no FAQPage JSON-LD",
  "recommendation":"Add FAQPage JSON-LD markup for each question/answer pair.",
  "estimated_score_gain":8,
  "impact":8,
  "effort":2
}
```

Each issue’s **expected_score_gain** is simply the points lost for that check, so the client knows adding the schema +8 points for “Citation Readiness” category.

**Sources:** Scoring criteria are based on AI search and schema best practices. Each rule reflects industry findings on what makes content “citable” by LLM-powered search. The design ensures full transparency and traceability of every point in the score.