# API_SPEC.md

**Project:** GEO Auditor – AI Citation Readiness Analyzer

**Version:** 1.0

**Status:** Final (MVP)

**Audience:** Claude Code, Cursor, Copilot, Human Developers

---

# Purpose

This document defines the public and internal API contracts for the GEO Auditor.

It is the **single source of truth** for communication between:

- Frontend
- Backend
- Crawl Engine
- GEO Check Engine
- Scoring Engine
- Report Generator
- LLM Service

Every module MUST follow these contracts.

No module may invent additional fields or change response structures.

---

# API Principles

The API follows several design principles.

## 1. Deterministic

Every request should generate identical results given identical website content.

The LLM never changes scores.

---

## 2. Stateless

Each audit is independent.

No persistent storage required.

No authentication.

No sessions.

---

## 3. Explainable

Every score must have evidence.

Every issue must contain:

- Evidence
- Recommendation
- Impact
- Effort

---

## 4. Modular

Crawler

↓

Extractor

↓

Checks

↓

Scoring

↓

LLM Explanation

↓

Report

Each stage produces structured JSON.

---

# Base URL

Development

```
http://localhost:8000
```

Production

```
https://geo-auditor.vercel.app/api
```

---

# Authentication

None.

No login.

No API Keys.

No JWT.

---

# Content Type

All requests

```
Content-Type: application/json
```

Responses

```
application/json
```

---

# API Version

```
/api/v1
```

Future versions

```
/api/v2
```

---

# Endpoints

---

# 1. Health Check

## GET

```
/health
```

Purpose

Verify backend availability.

---

Response

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "uptime": 10234
}
```

---

Status Codes

```
200 OK
```

---

# 2. Website Audit

## POST

```
/api/v1/audit
```

Purpose

Run complete GEO audit.

---

Request

```json
{
  "url":"https://company.com"
}
```

---

Validation

Required

- valid HTTP/HTTPS URL
- public domain

Reject

- localhost
- private IP
- FTP
- empty string

---

Success

```
202 Accepted
```

(or)

```
200 OK
```

depending on synchronous implementation.

---

Response

```json
{
    "audit_id":"uuid",

    "status":"completed",

    "report":{
        ...
    }
}
```

---

Errors

400

```json
{
    "error":"Invalid URL"
}
```

---

422

```json
{
    "error":"Unsupported website"
}
```

---

500

```json
{
    "error":"Crawler failed"
}
```

---

504

```json
{
    "error":"Website timeout"
}
```

---

# 3. Audit Status

Only useful if async.

GET

```
/api/v1/audit/{audit_id}
```

---

Response

```json
{
    "status":"running",

    "progress":72,

    "current_step":"Running Structured Data Checks"
}
```

---

Completed

```json
{
    "status":"completed",

    "report":{...}
}
```

---

# 4. Download Report

GET

```
/api/v1/report/{audit_id}
```

Query

```
format=json
```

or

```
format=html
```

or

```
format=pdf
```

---

Response

```
application/json
```

or

```
application/pdf
```

---

# Internal APIs

These are NOT exposed publicly.

They define module contracts.

---

# Crawler API

Input

```typescript
interface CrawlRequest{

    url:string;

}
```

---

Output

```typescript
interface CrawlResult{

    domain:string;

    homepage:string;

    pages:Page[];

}
```

---

Page

```typescript
interface Page{

    url:string;

    html:string;

    markdown:string;

    text:string;

    headers:Record<string,string>;

    metadata:Metadata;

    schemas:SchemaObject[];

}
```

---

Rules

Crawler NEVER

- calculates score

- runs LLM

- generates report

---

# Extractor API

Purpose

Extract structured information.

---

Input

```
Page
```

---

Output

```typescript
interface ExtractedPage{

    metadata;

    headings;

    images;

    links;

    schemas;

    entities;

}
```

---

# GEO Check API

Every check MUST follow the same interface.

---

Input

```
ExtractedPage
```

---

Output

```typescript
interface CheckResult{

    id:string;

    name:string;

    category:string;

    passed:boolean;

    score:number;

    maxScore:number;

    confidence:number;

    evidence:Evidence[];

    recommendation:Recommendation;

}
```

---

Evidence

```typescript
interface Evidence{

    page:string;

    selector:string;

    snippet:string;

    source:"html"|"schema"|"http";

}
```

---

Recommendation

```typescript
interface Recommendation{

    title:string;

    explanation:string;

    fix:string;

    effort:"Low"|"Medium"|"High";

    impact:"Low"|"Medium"|"High";

}
```

---

# Available Checks

Every checker implements

```python
run(page)->CheckResult
```

---

Current Check Library

```
Organization Schema

FAQ Schema

Article Schema

Breadcrumb Schema

Metadata

Robots.txt

LLMS.txt

Sitemap

Headings

Freshness

Entity Consistency

Citation Readiness
```

---

# Check Aggregator

Input

```
CheckResult[]
```

---

Output

```
AuditResult
```

---

Responsibilities

- merge results

- compute category totals

- remove duplicates

---

Never

- call LLM

---

# Scoring Engine

Input

```
CheckResult[]
```

---

Output

```typescript
interface ScoreResult{

overall:number;

categories:CategoryScore[];

}
```

---

Category

```typescript
interface CategoryScore{

name:string;

score:number;

maxScore:number;

checks:string[];

}
```

---

Rules

Only deterministic logic.

No AI.

---

# Priority Engine

Input

```
Issue[]
```

---

Output

```typescript
PriorityIssue[]
```

---

Formula

```
Priority

=

Impact

×

Confidence

÷

Effort
```

---

PriorityIssue

```typescript
interface PriorityIssue{

issueId:string;

priority:number;

estimatedScoreGain:number;

estimatedTime:number;

}
```

---

# LLM Service

Purpose

Convert technical findings

↓

Business explanations

---

Input

```typescript
interface LLMInput{

issues:Issue[];

scores:ScoreResult;

}
```

---

Output

```typescript
interface LLMOutput{

executiveSummary:string;

issueExplanations:string[];

businessSummary:string;

}
```

---

Rules

LLM

CAN

- summarize

- explain

- rewrite

- generate JSON-LD examples

---

LLM

CANNOT

- modify score

- invent evidence

- remove issues

---

# Report Generator

Input

```
AuditResult

+

LLMOutput
```

---

Output

```
FinalReport
```

---

Must support

```
JSON

HTML

PDF
```

---

# Request Lifecycle

```
POST /audit

↓

Validate URL

↓

Crawler

↓

Extractor

↓

Checks

↓

Scoring

↓

Priority

↓

LLM

↓

Report

↓

Response
```

---

# Error Handling

Crawler Timeout

↓

Partial Crawl

Continue

---

404 Page

↓

Skip

Continue

---

Schema Parsing Error

↓

Log

Continue

---

Missing robots.txt

↓

Warning

Continue

---

Missing sitemap

↓

Warning

Continue

---

LLM Failure

↓

Fallback Template

Continue

---

Frontend never receives

```
500 Internal Stacktrace
```

Always

```json
{
    "error":"Human readable message"
}
```

---

# Validation Rules

URL

```
Required
```

---

Domain

```
Public
```

---

Maximum Pages

```
20
```

---

Maximum Crawl Depth

```
2
```

---

Maximum HTML

```
5 MB
```

---

Maximum Crawl Time

```
30 sec
```

---

Maximum LLM Tokens

```
8000
```

---

# Rate Limits

MVP

None

Future

```
10 audits/hour/IP
```

---

# Standard Response Wrapper

Every endpoint returns

```typescript
interface APIResponse<T>{

success:boolean;

message:string;

timestamp:string;

data:T;

}
```

---

Example

```json
{
  "success": true,
  "message": "Audit completed successfully",
  "timestamp": "2026-08-06T12:10:00Z",
  "data": {
    "audit_id": "a123",
    "status": "completed"
  }
}
```

---

# OpenAPI Compatibility

The API should be fully compatible with OpenAPI 3.1.

Every endpoint must include

- Summary
- Description
- Tags
- Request Schema
- Response Schema
- Examples
- Error Responses

FastAPI should auto-generate

```
/docs
```

Swagger UI

and

```
/redoc
```

---

# Future APIs (Not in MVP)

```
POST /batch-audit

POST /compare

POST /competitors

POST /history

GET /analytics

POST /export

POST /share

GET /audit/{id}/timeline

POST /prompt-simulation

POST /chatgpt-visibility
```

---

# Implementation Constraints

Claude Code MUST follow these rules.

## MUST

✓ Follow API contracts exactly

✓ Never invent response fields

✓ Use typed models

✓ Return structured errors

✓ Keep modules independent

✓ Keep APIs stateless

✓ Validate all input

✓ Produce deterministic outputs

---

## MUST NOT

✗ Change API schemas

✗ Modify score in LLM

✗ Skip evidence

✗ Hardcode website-specific logic

✗ Couple frontend with crawler

✗ Mix crawling with scoring

✗ Return raw HTML in reports

✗ Expose internal implementation details

---

# Definition of Done

The API is complete when:

- Every endpoint validates inputs correctly.
- Every endpoint returns typed JSON matching this specification.
- The crawler, checks, scoring engine, LLM service, and report generator communicate only through documented contracts.
- All errors are handled gracefully without leaking stack traces.
- Swagger/OpenAPI documentation is automatically generated and accurately reflects the implementation.
- The frontend can consume the API without requiring undocumented fields or transformations.