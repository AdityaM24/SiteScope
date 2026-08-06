"""
Check: Article Schema — detect Article/NewsArticle/BlogPosting JSON-LD.
"""
from __future__ import annotations

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import article_schema, derive_site_name

ARTICLE_TYPES = {"Article", "NewsArticle", "BlogPosting", "TechArticle"}


class ArticleSchemaCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="article_schema",
            name="Article Schema",
            category="Structured Data",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check for Article schema on content pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        has_article = False
        evidence: list[EvidenceItem] = []

        for page in pages:
            # Check if page looks like article content (has date, headline)
            is_content_page = bool(page.headings.get(2)) or "blog" in page.url.lower() or "news" in page.url.lower()

            for item in page.json_ld:
                if any(t in ARTICLE_TYPES for t in item.types):
                    has_article = True
                    headline = item.data.get("headline", "")
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="script[type='application/ld+json']",
                        snippet=f"Article schema: {headline[:60]}",
                        source="schema",
                    ))

        # Score based on whether article pages have schema
        content_pages = [p for p in pages if any(kw in p.url.lower() for kw in ["blog", "news", "article", "post"])]

        if not content_pages:
            # No obvious article pages — not applicable
            return self._build_result(
                True, 5,
                [EvidenceItem(page=pages[0].domain, selector="", snippet="No article pages detected", source="html")],
                "No article content found — Article schema not applicable.",
                confidence=0.9,
            )
        elif has_article:
            return self._build_result(
                True, 5, evidence,
                "Article/BlogPosting schema found.",
                confidence=1.0,
            )
        else:
            page_url = content_pages[0].url
            return self._build_result(
                False, 0,
                [EvidenceItem(page=page_url, selector="", snippet="Article pages found but no Article schema", source="schema")],
                "Article pages detected but missing Article/BlogPosting JSON-LD. Add headline, datePublished, and author fields.",
                confidence=0.9,
                effort="Low",
                impact="Medium",
                fix_code=article_schema(derive_site_name(pages), page_url),
            )
