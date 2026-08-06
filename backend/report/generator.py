"""
Report generator — assembles the final audit report JSON.
"""
from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from ..models import AuditReport, CategoryScore, CheckResult, Issue, PriorityItem
from ..scoring.engine import build_issues, build_priority, compute_overall, compute_scores
from ..llm.service import generate_executive_summary, generate_issue_explanation

logger = logging.getLogger(__name__)


async def generate_report(
    domain: str,
    check_results: list[CheckResult],
) -> AuditReport:
    """
    Assemble the final audit report from check results.
    Uses LLM for executive summary if configured, otherwise template.
    """
    # Compute scores
    category_scores = compute_scores(check_results)
    overall = compute_overall(category_scores)

    # Build issues and priority
    issues = build_issues(check_results)
    priority = build_priority(issues)

    # Generate a business-friendly "why it matters" explanation for each issue
    # (LLM when a key is configured, otherwise template). Run concurrently.
    explanations = await asyncio.gather(
        *[generate_issue_explanation(issue) for issue in issues],
        return_exceptions=True,
    )
    for issue, text in zip(issues, explanations):
        if isinstance(text, str):
            issue.explanation = text
        elif isinstance(text, Exception):
            logger.warning("Explanation failed for '%s': %s", issue.title, text)
        # keep the pre-computed template explanation on failure

    # Generate executive summary (async LLM call)
    summary = await generate_executive_summary(overall, category_scores, issues)

    # Build the report
    report = AuditReport(
        executiveSummary=summary,
        overallScore=overall,
        categoryScores=category_scores,
        issues=issues,
        priority=priority,
        generatedAt=datetime.now(timezone.utc).isoformat(),
    )

    return report


def report_to_json(report: AuditReport) -> str:
    """Serialize report to JSON string."""
    return report.model_dump_json(indent=2)
