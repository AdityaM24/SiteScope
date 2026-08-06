"""
Check: Title Tag — validate page title presence and quality.
"""
from __future__ import annotations

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import title_tag_example


class TitleCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="title",
            name="Title Tag",
            category="Content Quality",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check title tags across crawled pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        evidence: list[EvidenceItem] = []
        issues: list[str] = []
        total_pages = len(pages)
        pages_with_title = 0

        for page in pages:
            title = page.title.strip() if page.title else ""
            if title:
                pages_with_title += 1
                if len(title) > 60:
                    issues.append(f"{page.url}: title too long ({len(title)} chars)")
                evidence.append(EvidenceItem(
                    page=page.url,
                    selector="title",
                    snippet=title[:80],
                    source="html",
                ))
            else:
                issues.append(f"{page.url}: missing title tag")

        if pages_with_title == total_pages:
            score = 5
            passed = True
            rec = "All pages have title tags."
        elif pages_with_title > total_pages * 0.5:
            score = 3
            passed = False
            rec = f"{total_pages - pages_with_title} page(s) missing title tags. Add <title> to each page."
        else:
            score = 0
            passed = False
            rec = "Most pages are missing title tags. This severely impacts AI visibility."

        if issues:
            evidence.append(EvidenceItem(
                page=pages[0].domain,
                selector="",
                snippet=f"Issues: {'; '.join(issues[:3])}",
                source="html",
            ))

        return self._build_result(
            passed, score, evidence, rec,
            confidence=1.0,
            effort="Low",
            impact="High",
            fix_code=title_tag_example() if not passed else "",
        )
