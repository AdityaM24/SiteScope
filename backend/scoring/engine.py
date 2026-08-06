"""
Scoring engine — deterministic aggregation of check results.

Content-strength dampening:
    Structured Data and AI Accessibility deductions are reduced when the site
    already has strong content signals (title, headings, freshness, meta,
    FAQ/article schema).  The rationale: an established site that has good
    content but is missing schema.org markup is less invisible to AI than a
    small site missing everything — AI already finds it through other means.

    Formula (documented, deterministic):
        content_signal_ratio = (content_quality + citation_readiness) / 40
        factor = clamp((content_signal_ratio - 0.3) / 0.5, 0, 1)
        sd_reduction  = factor × 0.45   (max 45 %)
        ai_reduction  = factor × 0.35   (max 35 %)
"""
from __future__ import annotations

from ..models import CheckResult, CategoryScore, Issue, PriorityItem

# Category definitions with their checks and max weights
CATEGORY_CONFIG: dict[str, dict] = {
    "Content Quality": {
        "max": 25,
        "checks": ["title", "meta_description", "headings", "freshness", "answer_block"],
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


def _compute_content_signal_ratio(
    content_quality: int,
    citation_readiness: int,
    content_max: int = 25,
    citation_max: int = 15,
) -> float:
    """
    Ratio measuring how strong the site's raw content signals are,
    independent of schema.org or crawlability.  Used to dampen
    Structured Data / AI Accessibility penalties when content is strong.
    """
    return min(1.0, (content_quality + citation_readiness) / (content_max + citation_max))


def _apply_content_dampening(
    category_scores: list[CategoryScore],
) -> tuple[list[CategoryScore], float, float]:
    """
    If content signals are strong, reduce SD / AI deductions proportionally.
    Returns the adjusted scores and the two reduction fractions (for the
    scope note).
    """
    # Find content-quality and citation-readiness scores
    cq = next((cs.score for cs in category_scores if cs.category == "Content Quality"), 0)
    cr = next((cs.score for cs in category_scores if cs.category == "Citation Readiness"), 0)

    ratio = _compute_content_signal_ratio(cq, cr)
    # Factor: 0 below 0.3, scales linearly to 1.0 at 0.8+
    factor = max(0.0, min(1.0, (ratio - 0.3) / 0.5))

    sd_reduction = factor * 0.45   # max 45 % fewer SD deductions
    ai_reduction = factor * 0.35   # max 35 % fewer AI deductions

    if sd_reduction == 0 and ai_reduction == 0:
        return category_scores, 0.0, 0.0

    adjusted: list[CategoryScore] = []
    for cs in category_scores:
        if cs.category == "Structured Data" and sd_reduction > 0:
            deduction = cs.max_score - cs.score
            new_deduction = round(deduction * (1.0 - sd_reduction))
            adjusted.append(CategoryScore(
                category=cs.category,
                score=cs.max_score - new_deduction,
                max_score=cs.max_score,
                checks=cs.checks,
            ))
        elif cs.category == "AI Accessibility" and ai_reduction > 0:
            deduction = cs.max_score - cs.score
            new_deduction = round(deduction * (1.0 - ai_reduction))
            adjusted.append(CategoryScore(
                category=cs.category,
                score=cs.max_score - new_deduction,
                max_score=cs.max_score,
                checks=cs.checks,
            ))
        else:
            adjusted.append(cs)

    return adjusted, sd_reduction, ai_reduction


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


def compute_scores_dampened(
    check_results: list[CheckResult],
) -> tuple[list[CategoryScore], float, float]:
    """
    Compute category scores and apply content-strength dampening.
    Returns (category_scores, sd_reduction_pct, ai_reduction_pct).
    """
    category_scores = compute_scores(check_results)
    return _apply_content_dampening(category_scores)


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
