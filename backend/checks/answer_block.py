"""
Check: Answer Block Detectability

Measures whether the first 100–200 words of a page contain a direct,
quotable answer to a likely user query — the kind of passage an AI engine
will pull into its overview and cite.

This is the "aha moment" check: most SMB sites open with brand language
("We are a mission-driven company...") instead of a direct answer
("We help restaurants reduce food waste by 40% using AI scheduling.").

AI search engines (ChatGPT, Perplexity, Google AI Overviews) look for
passages they can directly quote. If the first answer-like passage is
buried past 300 words, the page has low "answer-block detectability"
and is unlikely to be cited — even if it ranks #1 on Google.

References:
- Ahrefs 2025 AI citation study: cited passages average 18 words; the
  passage must appear early in the content.
- Google AI Overview design: the system extracts the first quotable
  paragraph and formats it as an answer.
"""
from __future__ import annotations

import re

from ..models import CheckResult, EvidenceItem
from .base import CheckBase


# Patterns that signal a direct answer in the opening text
_ANSWER_PATTERNS = [
    # Direct statement of what we do
    re.compile(r"\b(help(?:ing)?\s+\w+\s+(?:to|by|with|through)|solution\s+(?:for|to)|specialize|expert|leading\s+(?:provider|company))\b", re.IGNORECASE),
    # Definition-style opening
    re.compile(r"\b(?:is|are|was|were)\s+(?:a|an|the)\s+(?:software|platform|service|tool|company|solution)\b", re.IGNORECASE),
    # Numbered/quantified claim (strong citation signal)
    re.compile(r"\d+(?:,\d+)?%?\s+(?:of|in|for|reduces?|increases?|saves?|helps?)", re.IGNORECASE),
    # Question heading near top (FAQ-style answer)
    re.compile(r"<h[2-3][^>]*>.*\?.*</h[2-3]>", re.IGNORECASE),
    # "We provide/offer/sell" statement
    re.compile(r"\b(?:we\s+(?:provide|offer|sell|deliver|build|create)|our\s+(?:product|service|platform|tool))\b", re.IGNORECASE),
]

# Patterns that signal brand-first (non-answer) opening
_BRAND_FIRST_PATTERNS = [
    # Generic mission statements
    re.compile(r"\b(?:our\s+)?(?:mission|vision|values?|story|journey)\b", re.IGNORECASE),
    # Vague superlatives with no specifics
    re.compile(r"\b(?:leading|innovative|cutting\s*edge|world\s*class|premier|best\s*in\s*class)\b", re.IGNORECASE),
    # Brand name without context
    re.compile(r"\bwelcome\s+to\b", re.IGNORECASE),
    # Empty hero language
    re.compile(r"\b(?:empower|transform|revolutionize|redefine|disrupt)\b", re.IGNORECASE),
]

# Minimum words before an answer block must appear
_ANSWER_BLOCK_THRESHOLD = 200
# If answer-like pattern is found within this word window, it passes
_ANSWER_WINDOW = 80


def _extract_paragraphs(text: str, max_chars: int = 1500) -> list[str]:
    """Extract top paragraphs from plain text."""
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    collected = []
    total = 0
    for p in paragraphs:
        if total >= max_chars:
            break
        collected.append(p)
        total += len(p)
    return collected


def _count_words(text: str) -> int:
    return len(text.split())


class AnswerBlockCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="answer_block",
            name="Answer-Block Detectability",
            category="Content Quality",
            max_score=5,
        )

    def run(self, pages) -> CheckResult:
        """Check if top paragraphs contain a direct answer for AI extraction."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        evidence: list[EvidenceItem] = []
        failing_pages: list[str] = []
        answer_samples: list[str] = []

        for page in pages:
            paras = _extract_paragraphs(page.text, max_chars=1500)
            if not paras:
                failing_pages.append(page.url)
                continue

            first_block = " ".join(paras[:3])
            word_count = _count_words(first_block)

            # Check for answer patterns in the first N words
            early_text = first_block[: _ANSWER_WINDOW * 5]  # ~first 80 words
            has_answer = any(p.search(early_text) for p in _ANSWER_PATTERNS)
            has_brand_first = any(p.search(early_text) for p in _BRAND_FIRST_PATTERNS)

            # Also check if first H2 is a question (strong signal)
            h2_questions = [h for h in page.headings.get(2, []) if "?" in h]
            has_faq_heading = len(h2_questions) > 0

            if has_answer or has_faq_heading:
                # Good — answer is near the top
                snippet = first_block[:100].strip()
                evidence.append(EvidenceItem(
                    page=page.url,
                    selector="p:first-of-type",
                    snippet=f'Answer-like opening detected. First {word_count} words contain a quotable statement.',
                    source="html",
                ))
            else:
                # Bad — answer is buried or not present
                failing_pages.append(page.url)
                opening = first_block[:120].strip()
                if has_brand_first:
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="p:first-of-type",
                        snippet=f'Brand-first opening (first {word_count} words). AI engines need a direct answer, not a mission statement. Opening: "{opening}..."',
                        source="html",
                    ))
                else:
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="p:first-of-type",
                        snippet=f'No answer-like statement in first {word_count} words. AI engines can\'t find a quotable passage to cite. Opening: "{opening}..."',
                        source="html",
                    ))

        # Scoring
        if not failing_pages:
            return self._build_result(
                True, 5, evidence,
                "All pages open with direct, answer-like statements AI can cite.",
                confidence=0.9,
                effort="Medium",
                impact="High",
            )

        # How many pages have the problem
        fail_ratio = len(failing_pages) / len(pages)
        if fail_ratio > 0.7:
            score = 0
            passed = False
        elif fail_ratio > 0.3:
            score = 2
            passed = False
        else:
            score = 4
            passed = True

        recommendation = (
            "AI search engines extract the first quotable passage and cite it as an answer. "
            "Your homepage opens with brand language instead of a direct answer — "
            "ChatGPT and Perplexity can't find a passage to cite, so they skip your site entirely. "
            "Fix: rewrite the opening paragraph to lead with what you do for whom, "
            "ideally with a specific number or outcome. Example: 'We help [who] achieve [result] by [method].'"
        )

        return self._build_result(
            passed, score, evidence,
            recommendation,
            confidence=0.85,
            effort="Medium",
            impact="High",
            fix_code=self._fix_template(pages),
        )

    def _fix_template(self, pages) -> str:
        """Generate a before/after fix based on detected brand language."""
        homepage = pages[0]
        opening = homepage.text[:200].strip()
        # Extract a plausible company name from title
        title = (homepage.title or "").split(" - ")[0].split(" – ")[0].strip()
        return (
            "## Fix: Rewrite your opening paragraph\n\n"
            "### Current opening (brand-first):\n"
            "```\n"
            f"{opening[:150]}...\n"
            "```\n\n"
            "### Suggested opening (answer-first):\n"
            "```\n"
            f"{title} helps [your target customer] [achieve specific result] "
            f"by [your unique method]. [One supporting stat or proof point.]\n"
            "```\n\n"
            "**Why this matters:** AI search engines scan the first 100 words for a "
            "quotable answer. If they find a direct statement, they cite it. "
            "If they find brand language, they skip the page. This single change "
            "can double your AI citation rate."
        )
