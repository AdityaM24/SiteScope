"""
Base class for all GEO checks.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

from ..models import CheckResult, EvidenceItem


@dataclass
class CheckBase(ABC):
    """Abstract base for all GEO checks."""

    check_id: str = ""
    name: str = ""
    category: str = ""
    max_score: int = 10

    @abstractmethod
    def run(self, pages: list[Any]) -> CheckResult:
        """Run the check on the given pages and return a CheckResult."""
        ...

    def _make_evidence(
        self,
        page: str,
        snippet: str,
        source: str = "html",
        selector: str = "",
    ) -> EvidenceItem:
        return EvidenceItem(page=page, selector=selector, snippet=snippet, source=source)

    def _build_result(
        self,
        passed: bool,
        score: int,
        evidence: list[EvidenceItem],
        recommendation: str,
        confidence: float = 1.0,
        effort: str = "Low",
        impact: str = "Medium",
        fix_code: str = "",
    ) -> CheckResult:
        return CheckResult(
            id=self.check_id,
            name=self.name,
            category=self.category,
            passed=passed,
            score=score,
            max_score=self.max_score,
            confidence=confidence,
            evidence=evidence,
            recommendation=recommendation,
            fix_code=fix_code,
            effort=effort,
            impact=impact,
        )
