"""
Check: Breadcrumb Schema — detect BreadcrumbList JSON-LD.
"""
from __future__ import annotations

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import breadcrumb_schema

BREADCRUMB_TYPES = {"BreadcrumbList"}


class BreadcrumbSchemaCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="breadcrumb_schema",
            name="Breadcrumb Schema",
            category="Structured Data",
            max_score=3,
        )

    def run(self, pages) -> CheckResult:
        """Check for BreadcrumbList schema."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        has_breadcrumb = False
        evidence: list[EvidenceItem] = []

        for page in pages:
            for item in page.json_ld:
                if any(t in BREADCRUMB_TYPES for t in item.types):
                    has_breadcrumb = True
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="script[type='application/ld+json']",
                        snippet="BreadcrumbList schema found",
                        source="schema",
                    ))
                    break
            if has_breadcrumb:
                break

        if has_breadcrumb:
            return self._build_result(
                True, 3, evidence,
                "BreadcrumbList schema found.",
                confidence=1.0,
            )
        else:
            homepage = f"https://{pages[0].domain}"
            return self._build_result(
                False, 0,
                [EvidenceItem(page=pages[0].domain, selector="", snippet="No BreadcrumbList schema found", source="schema")],
                "Add BreadcrumbList JSON-LD to help AI understand site hierarchy.",
                confidence=1.0,
                effort="Low",
                impact="Low",
                fix_code=breadcrumb_schema(homepage),
            )
