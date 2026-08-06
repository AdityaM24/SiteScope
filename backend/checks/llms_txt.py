"""
Check: llms.txt — check for the emerging LLM crawler standard.
"""
from __future__ import annotations

import re

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import derive_site_name, llms_txt


class LLMsTxtCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="llms_txt",
            name="llms.txt",
            category="AI Accessibility",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check if /llms.txt exists and is valid."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        domain = pages[0].domain
        llms_content = getattr(pages[0], "_llms_content", None)

        if llms_content is None:
            homepage = f"https://{domain}"
            return self._build_result(
                False, 0,
                [EvidenceItem(page=domain, selector="", snippet="No /llms.txt file found", source="http")],
                "Add a /llms.txt file to guide AI crawlers. Include a site description and links to key pages.",
                confidence=1.0,
                effort="Low",
                impact="Medium",
                fix_code=llms_txt(derive_site_name(pages), homepage),
            )

        # Validate llms.txt format: should start with H1 (# title)
        lines = llms_content.strip().splitlines()
        has_h1 = any(line.strip().startswith("# ") for line in lines)
        has_links = any("[" in line and "]" in line for line in lines if line.strip())

        if has_h1:
            first_line = lines[0].strip()
            return self._build_result(
                True, 5,
                [EvidenceItem(page=domain, selector="", snippet=f"llms.txt found. First line: {first_line}", source="http")],
                "llms.txt is present and properly formatted.",
                confidence=1.0,
            )
        else:
            homepage = f"https://{domain}"
            return self._build_result(
                False, 2,
                [EvidenceItem(page=domain, selector="", snippet="llms.txt exists but missing H1 title", source="http")],
                "llms.txt found but should start with '# Site Name' as H1 heading.",
                confidence=0.8,
                fix_code=llms_txt(derive_site_name(pages), homepage),
            )
