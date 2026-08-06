"""
Pydantic data models — the single source of truth for all contracts.
"""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

from pydantic import BaseModel, Field, HttpUrl, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class Severity(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class Effort(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class Impact(str, Enum):
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class CheckCategory(str, Enum):
    CONTENT_QUALITY = "Content Quality"
    STRUCTURED_DATA = "Structured Data"
    AI_ACCESSIBILITY = "AI Accessibility"
    ENTITY_TRUST = "Entity Trust"
    CITATION_READINESS = "Citation Readiness"


# ---------------------------------------------------------------------------
# Auxiliary data passed to checks (robots.txt, llms.txt, sitemap.xml)
# ---------------------------------------------------------------------------

class AuxData(BaseModel):
    """Extra crawl results attached to checks at runtime (not per-page data)."""
    robots_content: Optional[str] = None
    llms_content: Optional[str] = None
    sitemap_content: Optional[str] = None


# ---------------------------------------------------------------------------
# Crawler / Extractor models
# ---------------------------------------------------------------------------

class JSONLDItem(BaseModel):
    """A single parsed JSON-LD block."""
    raw: str
    data: dict[str, Any]
    types: list[str] = Field(default_factory=list)


class Page(BaseModel):
    """Raw and extracted data for one crawled page."""
    url: str
    status_code: int = 200
    html: str = ""
    text: str = ""
    title: str = ""
    meta_description: str = ""
    canonical: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    twitter_title: Optional[str] = None
    twitter_description: Optional[str] = None
    twitter_image: Optional[str] = None
    headings: dict[int, list[str]] = Field(default_factory=dict)  # {1:[...], 2:[...]}
    links: list[str] = Field(default_factory=list)
    json_ld: list[JSONLDItem] = Field(default_factory=list)
    last_modified: Optional[str] = None  # ISO 8601 date string or None
    headers: dict[str, str] = Field(default_factory=dict)
    domain: str = ""
    path: str = ""


class CrawlResult(BaseModel):
    domain: str
    homepage: str
    pages: list[Page] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Check models
# ---------------------------------------------------------------------------

class EvidenceItem(BaseModel):
    page: str
    selector: str
    snippet: str
    source: str = "html"  # html | schema | http


class CheckResult(BaseModel):
    id: str
    name: str
    category: str  # CheckCategory name
    passed: bool
    score: int
    max_score: int
    confidence: float = 1.0
    evidence: list[EvidenceItem] = Field(default_factory=list)
    recommendation: str = ""
    fix_code: str = ""  # Copy-pasteable snippet to resolve the finding
    effort: str = "Low"
    impact: str = "Medium"

    @property
    def priority_score(self) -> float:
        effort_map = {"Low": 1, "Medium": 2, "High": 3}
        impact_map = {"Low": 1, "Medium": 2, "High": 3}
        e = effort_map.get(self.effort, 2)
        imp = impact_map.get(self.impact, 2)
        if e == 0:
            e = 1
        return round((imp * self.confidence) / e, 2)

    @property
    def score_gain(self) -> int:
        return self.max_score - self.score


# ---------------------------------------------------------------------------
# Scoring models
# ---------------------------------------------------------------------------

class CategoryScore(BaseModel):
    category: str
    score: int
    max_score: int
    checks: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Report models (matches REPORT_SCHEMA.md)
# ---------------------------------------------------------------------------

class Issue(BaseModel):
    id: int
    title: str
    page: str
    severity: str = "Medium"  # High/Medium/Low
    evidence: str
    recommendation: str
    fixCode: str = ""  # Copy-pasteable snippet (Markdown code fence content)
    explanation: str = ""  # Business-friendly "why it matters" text (LLM or template)
    impact: int = 1
    confidence: float = 1.0
    effort: str = "Low"
    estimatedScoreGain: int = 0
    priority: float = 0.0


class PriorityItem(BaseModel):
    issueId: int
    impact: float
    confidence: float
    effort: float
    priority: float


class AuditReport(BaseModel):
    executiveSummary: str
    overallScore: int
    categoryScores: list[CategoryScore]
    issues: list[Issue]
    priority: list[PriorityItem]
    generatedAt: str


# ---------------------------------------------------------------------------
# API request / response models
# ---------------------------------------------------------------------------

class AuditRequest(BaseModel):
    url: str

    @field_validator("url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("URL is required")
        return v


T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    """Generic wrapper used by all endpoints."""
    success: bool
    message: str
    timestamp: str
    data: T


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    version: str
    uptime: int
