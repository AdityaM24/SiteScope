"""
Check: Heading Structure — validate H1/H2/H3 hierarchy.
"""
from __future__ import annotations

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import heading_structure_example


class HeadingsCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="headings",
            name="Heading Structure",
            category="Content Quality",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check heading structure across pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        evidence: list[EvidenceItem] = []
        issues: list[str] = []
        total_checked = 0
        all_good = True

        for page in pages:
            headings = page.headings
            h1_count = len(headings.get(1, []))
            h2_count = len(headings.get(2, []))
            h3_count = len(headings.get(3, []))

            total_checked += 1

            if h1_count == 0:
                issues.append(f"{page.url}: no H1 tag")
                all_good = False
            elif h1_count > 1:
                issues.append(f"{page.url}: {h1_count} H1 tags (should be 1)")
                all_good = False

            evidence.append(EvidenceItem(
                page=page.url,
                selector="h1, h2, h3",
                snippet=f"H1: {h1_count}, H2: {h2_count}, H3: {h3_count}",
                source="html",
            ))

        if all_good and total_checked > 0:
            return self._build_result(
                True, 5, evidence,
                "All pages have proper heading structure.",
                confidence=1.0,
            )
        else:
            score = 0 if total_checked == 0 else max(0, 5 - len(issues))
            return self._build_result(
                False, score, evidence,
                f"{'; '.join(issues[:3])}. Use exactly one H1 per page and logical H2/H3 hierarchy.",
                confidence=1.0,
                effort="Low",
                impact="Medium",
                fix_code=heading_structure_example(),
            )
