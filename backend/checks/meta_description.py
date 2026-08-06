"""
Check: Meta Description — validate meta description presence and quality.
"""
from __future__ import annotations

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import meta_description_example


class MetaDescriptionCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="meta_description",
            name="Meta Description",
            category="Content Quality",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check meta descriptions across crawled pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        evidence: list[EvidenceItem] = []
        issues: list[str] = []
        total_pages = len(pages)
        pages_with_desc = 0

        for page in pages:
            desc = page.meta_description.strip() if page.meta_description else ""
            if desc:
                pages_with_desc += 1
                if len(desc) < 50 or len(desc) > 160:
                    issues.append(f"{page.url}: description length {len(desc)} (ideal: 50-160)")
                evidence.append(EvidenceItem(
                    page=page.url,
                    selector="meta[name='description']",
                    snippet=desc[:100],
                    source="html",
                ))
            else:
                issues.append(f"{page.url}: missing meta description")

        if pages_with_desc == total_pages:
            score = 5
            passed = True
            rec = "All pages have meta descriptions."
        elif pages_with_desc > total_pages * 0.5:
            score = 3
            passed = False
            rec = f"{total_pages - pages_with_desc} page(s) missing meta descriptions. Add <meta name='description'> tags."
        else:
            score = 0
            passed = False
            rec = "Most pages lack meta descriptions. Add descriptive <meta name='description'> tags to all pages."

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
            impact="Medium",
            fix_code=meta_description_example() if not passed else "",
        )
