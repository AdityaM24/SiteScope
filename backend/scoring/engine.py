"""
Scoring engine — deterministic aggregation of check results.
"""
from __future__ import annotations

from ..models import CheckResult, CategoryScore, Issue, PriorityItem

# Category definitions with their checks and max weights
CATEGORY_CONFIG: dict[str, dict] = {
    "Content Quality": {
        "max": 25,
        "checks": ["title", "meta_description", "headings", "freshness"],
    },
    "Structured Data": {
        "max": 20,
        "checks": ["organization_schema", "faq_schema", "article_schema", "breadcrumb_schema"],
    },
    "AI Accessibility": {
        "max": 20,
        "checks": ["robots_txt", "llms_txt", "sitemap"],
    },
    "Entity Trust": {
        "max": 20,
        "checks": ["nap_consistency"],
    },
    "Citation Readiness": {
        "max": 15,
        "checks": [],  # Composite — derived from FAQ + Article schema presence
    },
}


def compute_scores(check_results: list[CheckResult]) -> list[CategoryScore]:
    """
    Aggregate check results into category scores.
    Each category score is clamped to [0, max].
    """
    # Group checks by category
    category_checks: dict[str, list[CheckResult]] = {cat: [] for cat in CATEGORY_CONFIG}
    other: list[CheckResult] = []

    for cr in check_results:
        found = False
        for cat in category_checks:
            if cr.category == cat:
                category_checks[cat].append(cr)
                found = True
                break
        if not found:
            other.append(cr)

    category_scores = []
    for cat_name, cat_info in CATEGORY_CONFIG.items():
        checks = category_checks[cat_name]
        max_score = cat_info["max"]
        total = sum(cr.score for cr in checks)
        actual = min(total, max_score)
        check_names = [cr.name for cr in checks]
        category_scores.append(CategoryScore(
            category=cat_name,
            score=actual,
            max_score=max_score,
            checks=check_names,
        ))

    # Citation Readiness is a composite of FAQ + Article schema presence
    faq_passed = any(cr.passed and cr.id == "faq_schema" for cr in check_results)
    article_passed = any(cr.passed and cr.id == "article_schema" for cr in check_results)
    citation_score = 0
    if faq_passed:
        citation_score += 8
    if article_passed:
        citation_score += 5
    # Additional points for meta description and title
    for cr in check_results:
        if cr.id == "meta_description" and cr.passed:
            citation_score += min(cr.score, 2)
        if cr.id == "title" and cr.passed:
            citation_score += min(cr.score, 2)
    citation_score = min(citation_score, 15)

    # Replace Citation Readiness entry
    found = False
    for i, cs in enumerate(category_scores):
        if cs.category == "Citation Readiness":
            category_scores[i] = CategoryScore(
                category="Citation Readiness",
                score=citation_score,
                max_score=15,
                checks=["faq_schema", "article_schema", "meta_description", "title"],
            )
            found = True
            break
    if not found:
        category_scores.append(CategoryScore(
            category="Citation Readiness",
            score=citation_score,
            max_score=15,
            checks=["faq_schema", "article_schema"],
        ))

    return category_scores


def compute_overall(category_scores: list[CategoryScore]) -> int:
    """Sum all category scores for overall 0-100 score."""
    return sum(cs.score for cs in category_scores)


def build_issues(check_results: list[CheckResult]) -> list[Issue]:
    """Convert failing checks into Issue objects with evidence."""
    issues: list[Issue] = []
    for cr in check_results:
        if cr.passed:
            continue

        # Determine severity
        score_ratio = cr.score / cr.max_score if cr.max_score > 0 else 0
        if score_ratio == 0:
            severity = "High"
        elif score_ratio < 0.5:
            severity = "Medium"
        else:
            severity = "Low"

        # Build evidence string
        evidence_parts = []
        for ev in cr.evidence:
            evidence_parts.append(f"{ev.page}: {ev.snippet}")
        evidence_str = "; ".join(evidence_parts) if evidence_parts else cr.recommendation

        # Map effort/impact to numeric
        effort_map = {"Low": 1, "Medium": 2, "High": 3}
        impact_map = {"Low": 1, "Medium": 2, "High": 3}
        effort_val = effort_map.get(cr.effort, 2)
        impact_val = impact_map.get(cr.impact, 2)
        estimated_gain = cr.max_score - cr.score

        priority = round((impact_val * cr.confidence) / effort_val, 2) if effort_val > 0 else 0

        issues.append(Issue(
            id=len(issues) + 1,
            title=cr.name,
            page=evidence_parts[0].split(": ")[0] if evidence_parts else cr.evidence[0].page if cr.evidence else "",
            severity=severity,
            evidence=evidence_str or cr.recommendation,
            recommendation=cr.recommendation,
            fixCode=cr.fix_code,
            impact=estimated_gain,
            confidence=cr.confidence,
            effort=cr.effort,
            estimatedScoreGain=estimated_gain,
            priority=priority,
        ))

    # Sort by priority descending
    issues.sort(key=lambda x: x.priority, reverse=True)
    # Reassign IDs after sort
    for i, issue in enumerate(issues, 1):
        issue.id = i

    return issues


def build_priority(issues: list[Issue]) -> list[PriorityItem]:
    """Build priority list from issues."""
    return [
        PriorityItem(
            issueId=issue.id,
            impact=float(issue.impact),
            confidence=issue.confidence,
            effort=float({"Low": 1, "Medium": 2, "High": 3}.get(issue.effort, 2)),
            priority=issue.priority,
        )
        for issue in issues
    ]
