"""
Check: FAQ Schema — detect FAQPage JSON-LD or visible Q&A content.
"""
from __future__ import annotations

import re

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import derive_faq_questions, faq_schema

FAQ_TYPES = {"FAQPage", "Question", "Answer"}
FAQ_HEADING_RE = re.compile(r"\?(?:\s|$)", re.IGNORECASE)


class FAQSchemaCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="faq_schema",
            name="FAQ Schema",
            category="Structured Data",
            max_score=8,
        )

    def run(self, pages) -> CheckResult:
        """Check for FAQ schema or visible Q&A content."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        has_faq_schema = False
        has_faq_content = False
        faq_questions: list[str] = []
        evidence: list[EvidenceItem] = []

        for page in pages:
            # Check JSON-LD for FAQPage
            for item in page.json_ld:
                if "FAQPage" in item.types or "Question" in item.types:
                    has_faq_schema = True
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="script[type='application/ld+json']",
                        snippet="FAQPage schema found",
                        source="schema",
                    ))

            # Check visible content for Q&A patterns
            text = page.text.lower()
            headings_text = " ".join(h for hs in page.headings.values() for h in hs).lower()

            # Look for question-like headings or FAQ sections
            if re.search(r"faq|frequently asked questions", text) or \
               re.search(r"\?(?:\s|$)", headings_text):
                has_faq_content = True
                # Extract question-like headings
                q_headings = [h for h in headings_text.split() if "?" in h]
                faq_questions.extend(q_headings[:5])

        if has_faq_schema:
            return self._build_result(
                True, 8, evidence,
                "FAQPage schema found. Well structured for AI extraction.",
                confidence=1.0,
                effort="Low",
                impact="High",
            )
        elif has_faq_content:
            questions = derive_faq_questions(pages) or faq_questions
            return self._build_result(
                False, 0,
                [EvidenceItem(page=pages[0].domain, selector="", snippet=f"FAQ content detected but no FAQPage schema. Questions: {', '.join(faq_questions[:3])}", source="html")],
                "FAQ content detected but no FAQPage JSON-LD schema. Add FAQPage schema for better AI visibility.",
                confidence=0.85,
                effort="Low",
                impact="High",
                fix_code=faq_schema(questions),
            )
        else:
            return self._build_result(
                True, 8,
                [EvidenceItem(page=pages[0].domain, selector="", snippet="No FAQ content detected (not applicable)", source="html")],
                "No FAQ content found. Consider adding FAQ section if relevant.",
                confidence=1.0,
                effort="Low",
                impact="Low",
            )
