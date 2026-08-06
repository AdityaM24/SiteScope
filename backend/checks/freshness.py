"""
Check: Content Freshness — validate last-modified dates.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta
from typing import Optional

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import date_modified_meta

DATE_PATTERNS = [
    re.compile(r"(?:last\s*updated|modified|published|updated)\s*:?\s*(\d{4}[-/]\d{1,2}[-/]\d{1,2})", re.IGNORECASE),
    re.compile(r"(\d{4}[-/]\d{1,2}[-/]\d{1,2})"),
]


def _parse_date(text: str) -> Optional[datetime]:
    """Try to extract a date from text."""
    for pattern in DATE_PATTERNS:
        match = pattern.search(text)
        if match:
            date_str = match.group(1)
            try:
                return datetime.strptime(date_str, "%Y-%m-%d")
            except ValueError:
                try:
                    return datetime.strptime(date_str, "%Y/%m/%d")
                except ValueError:
                    continue
    return None


class FreshnessCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="freshness",
            name="Content Freshness",
            category="Content Quality",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check content freshness across pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        now = datetime.now()
        evidence: list[EvidenceItem] = []
        dates_found: list[tuple[str, datetime]] = []
        dates_missing: list[str] = []

        for page in pages:
            # Check explicit date sources
            date_str = None
            if page.last_modified:
                date_str = page.last_modified[:10]  # ISO date part

            # Also search page text for dates
            if not date_str:
                date_str = _parse_date(page.text)
                if date_str:
                    date_str = date_str.strftime("%Y-%m-%d")

            if date_str:
                try:
                    parsed_date = datetime.strptime(date_str, "%Y-%m-%d")
                    days_old = (now - parsed_date).days
                    dates_found.append((page.url, parsed_date))
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="time, meta[property='article:modified_time']",
                        snippet=f"Last updated: {date_str} ({days_old} days ago)",
                        source="html",
                    ))
                except ValueError:
                    pass
            else:
                dates_missing.append(page.url)

        if not dates_found:
            return self._build_result(
                False, 0,
                [EvidenceItem(page=pages[0].domain, selector="", snippet=f"No dates found on {len(pages)} pages", source="html")],
                "Add 'last modified' dates to pages. AI assistants prefer fresh content.",
                confidence=0.9,
                effort="Low",
                impact="Medium",
                fix_code=date_modified_meta(),
            )

        # Calculate average freshness
        avg_days = sum((now - d).days for _, d in dates_found) / len(dates_found)
        old_pages = [url for url, d in dates_found if d < now - timedelta(days=730)]

        if len(old_pages) > len(dates_found) * 0.5:
            return self._build_result(
                False, 1,
                evidence,
                f"Most content is stale. {len(old_pages)}/{len(dates_found)} pages older than 2 years. Update content regularly.",
                confidence=0.8,
                effort="High",
                impact="Medium",
                fix_code=date_modified_meta(),
            )
        elif avg_days > 365:
            return self._build_result(
                False, 3,
                evidence,
                f"Average content age is {int(avg_days)} days. Consider updating older content.",
                confidence=0.7,
                effort="Medium",
                impact="Low",
                fix_code=date_modified_meta(),
            )
        else:
            return self._build_result(
                True, 5,
                evidence,
                f"Content is fresh. Average age: {int(avg_days)} days.",
                confidence=1.0,
            )
