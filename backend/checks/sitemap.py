"""
Check: sitemap.xml — check for XML sitemap presence and homepage inclusion.
"""
from __future__ import annotations

import re

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import sitemap_xml


class SitemapCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="sitemap",
            name="sitemap.xml",
            category="AI Accessibility",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check if /sitemap.xml exists and contains the audited URLs."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        domain = pages[0].domain
        sitemap_content = getattr(pages[0], "_sitemap_content", None)

        if sitemap_content is None:
            homepage = f"https://{domain}"
            return self._build_result(
                False, 0,
                [EvidenceItem(page=domain, selector="", snippet="No sitemap.xml found", source="http")],
                "Create a sitemap.xml to help AI crawlers discover your pages.",
                confidence=1.0,
                effort="Low",
                impact="Medium",
                fix_code=sitemap_xml(homepage),
            )

        # Count URLs and check homepage inclusion
        locs = re.findall(r"<loc>(.*?)</loc>", sitemap_content, re.IGNORECASE)
        url_count = len(locs)
        homepage_url = pages[0].url.rstrip("/")
        homepage_in_sitemap = any(homepage_url in loc for loc in locs)

        if url_count == 0:
            return self._build_result(
                False, 1,
                [EvidenceItem(page=domain, selector="", snippet="sitemap.xml exists but contains no <loc> entries", source="http")],
                "Sitemap exists but is empty. Add <url><loc>...</loc></url> entries for each important page.",
                confidence=0.9,
                effort="Low",
                impact="Medium",
                fix_code=sitemap_xml(homepage_url),
            )

        # Show first 3 URLs as evidence
        snippet = f"Found {url_count} URLs: {', '.join(locs[:3])}"
        if not homepage_in_sitemap:
            snippet += f". NOTE: homepage ({homepage_url}) is missing from sitemap"

        score = 5 if homepage_in_sitemap else 3
        return self._build_result(
            score == 5,
            score,
            [EvidenceItem(page=domain, selector="", snippet=snippet, source="http")],
            f"Sitemap found with {url_count} URLs" + (". Homepage is listed." if homepage_in_sitemap else f" but homepage ({homepage_url}) is not listed — add it."),
            confidence=1.0,
        )
