TASKS.md

1. Development Rules

2. Milestones

3. Task Dependency Graph

4. Backend Tasks

5. Frontend Tasks

6. Integration Tasks

7. Testing Tasks

8. Polish Tasks

9. Stretch Goals

10. Definition of MVP
Development Rules

Example

Every task must

- Compile successfully
- Pass linting
- Not break existing APIs
- Update documentation if contracts change
- Follow REPORT_SCHEMA.md
- Follow API_SPEC.md
- Never invent JSON fields

Never start another task until current task passes.
Milestones

Instead of random tasks

Break into milestones.

Milestone 1

Project Foundation

↓

Milestone 2

Crawler

↓

Milestone 3

GEO Checks

↓

Milestone 4

Scoring

↓

Milestone 5

LLM

↓

Milestone 6

Report

↓

Milestone 7

Frontend

↓

Milestone 8

Polish

Claude understands this extremely well.

Task Dependency Graph
Example Task
## TASK-001

Title

Initialize Backend

Priority

Critical

Depends On

None

Description

Create FastAPI backend.

Configure routing.

Environment variables.

Logging.

Folder structure.

Deliverables

backend/

requirements.txt

main.py

config.py

Acceptance Criteria

Server starts.

Swagger loads.

Health endpoint works.

Definition of Done

GET /health returns

200
Another Example
## TASK-005

Title

Organization Schema Checker

Priority

Critical

Depends

Crawler

Extractor

Description

Detect Organization schema.

Read JSON-LD.

Validate.

Generate evidence.

Output CheckResult.

Files

checks/

organization.py

Acceptance

Finds

Organization

LocalBusiness

Corporation

Returns

passed

score

evidence

recommendation

Definition of Done

Runs independently.

Unit tested.

No LLM.
Suggested Tasks
Milestone 1
Foundation
001

Initialize Backend

002

Initialize Frontend

003

Configuration

004

Logging

005

Models

006

API Contracts
Milestone 2

Crawler

010

URL Validation

011

Crawler

012

HTML Download

013

Metadata Extraction

014

JSON-LD Extraction

015

Text Extraction

016

Page Model
Milestone 3

Checks

020

Organization

021

FAQ

022

Article

023

Breadcrumb

024

Metadata

025

Headings

026

robots.txt

027

llms.txt

028

Sitemap

029

Freshness

030

Entity

031

Citation Readiness

Every checker

Independent.

Milestone 4

Scoring

040

Score Engine

041

Category Score

042

Priority Engine

043

Confidence Engine
Milestone 5

LLM

050

Executive Summary

051

Business Explanation

052

Recommendations

053

JSON-LD Generator

054

HTML Generator
Milestone 6

Reports

060

Report JSON

061

Markdown

062

HTML

063

PDF
Milestone 7

API

070

POST /audit

071

GET /health

072

Report Download

073

Error Handling
Milestone 8

Frontend

080

Landing Page

081

Audit Form

082

Loading State

083

Report Page

084

Score Cards

085

Issue Cards

086

Priority Matrix

087

Export Button
Milestone 9

Testing

090

Test Apple.com

091

Test Stripe

092

Test HubSpot

093

Edge Cases
Acceptance Criteria

Every task

Must contain

Build succeeds

Lint succeeds

No TypeScript errors

No Python errors

Follows contracts

No hardcoded data

No mocked production output

Matches API spec
Stretch Goals

Not for MVP.

Competitor Comparison

ChatGPT Prompt Simulation

Perplexity Visibility

AI Overview Checker

Historical Reports

Scheduled Audits

Authentication

Dashboard
Definition of MVP

This is important.

Claude knows exactly when to stop.

The MVP is complete when

✓ User enters URL

✓ Website crawls

✓ GEO checks execute

✓ Score generated

✓ Evidence collected

✓ Business recommendations generated

✓ HTML report rendered

✓ JSON report exported

✓ Three real websites audited

Everything else is out of scope.
The most powerful addition: Agent Execution Mode

Instead of giving Claude the whole project, instruct it to work one task at a time.

Execution Rules

1.

Read all documentation first.

2.

Never implement multiple milestones simultaneously.

3.

Complete exactly one TASK at a time.

4.

Run project after every completed task.

5.

Commit after every completed task.

6.

Do not modify completed modules unless required.

7.

Never invent APIs.

8.

Never invent report fields.

9.

Never change scoring.

10.

Stop after every milestone and summarize progress.