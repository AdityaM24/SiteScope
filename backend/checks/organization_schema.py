"""
Check: Organization Schema — detect Organization/LocalBusiness JSON-LD.
"""
from __future__ import annotations

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import derive_site_name, org_schema

ORG_TYPES = {"Organization", "LocalBusiness", "Corporation", "NGO", "Person"}


class OrganizationSchemaCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="organization_schema",
            name="Organization Schema",
            category="Structured Data",
            max_score=10,
        )

    def run(self, pages) -> CheckResult:
        """Check for Organization schema across pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        found_org = False
        found_name = False
        evidence: list[EvidenceItem] = []
        snippet_text = ""

        for page in pages:
            for item in page.json_ld:
                if any(t in ORG_TYPES for t in item.types):
                    found_org = True
                    name = item.data.get("name", "")
                    if name:
                        found_name = True
                    snippet_text = item.raw[:200]
                    evidence.append(EvidenceItem(
                        page=page.url,
                        selector="script[type='application/ld+json']",
                        snippet=f"@type: {', '.join(item.types)}",
                        source="schema",
                    ))
                    if found_org and found_name:
                        break
            if found_org and found_name:
                break

        if found_org and found_name:
            return self._build_result(
                True, 10, evidence,
                "Organization schema found with name and URL.",
                confidence=1.0,
                effort="Low",
                impact="High",
            )
        elif found_org:
            return self._build_result(
                False, 5, evidence,
                "Organization schema found but missing name or URL. Add 'name' and 'url' fields.",
                confidence=0.9,
                effort="Low",
                impact="High",
            )
        else:
            # Gather what schema types were actually found (for specific evidence)
            found_types = set()
            for item in (i for p in pages for i in p.json_ld):
                for t in item.types:
                    found_types.add(t)
            schema_detail = (
                f". Found {len(pages)} page(s) with schema: {', '.join(sorted(found_types))}."
                if found_types
                else f". Checked {len(pages)} page(s) — no schema of any type found."
            )
            homepage = f"https://{pages[0].domain}"
            name = derive_site_name(pages)
            return self._build_result(
                False, 0,
                [EvidenceItem(
                    page=pages[0].domain,
                    selector="",
                    snippet=f"No Organization schema on any of {len(pages)} crawled pages"
                    + schema_detail,
                    source="schema",
                )],
                "Add Organization JSON-LD schema with name, logo, and contact info to help AI identify your business.",
                confidence=1.0,
                effort="Low",
                impact="High",
                fix_code=org_schema(name, homepage),
            )
