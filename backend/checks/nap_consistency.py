"""
Check: NAP Consistency — validate Name/Address/Phone consistency across pages.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Optional

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import derive_site_name, nap_schema

PHONE_RE = re.compile(r"[\+]?[\d\s\-\(\)]{7,}")
ADDRESS_RE = re.compile(r"\d+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:St|Street|Ave|Avenue|Rd|Road|Blvd|Boulevard|Dr|Drive|Ln|Lane|Way|Court| Ct|Cir|Circle)", re.IGNORECASE)


class NAPConsistencyCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="nap_consistency",
            name="Business Info Consistency",
            category="Entity Trust",
            max_score=10,
        )

    def run(self, pages) -> CheckResult:
        """Check consistency of business name, address, and phone across pages."""
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        # Collect names from Organization schema
        org_names: set[str] = set()
        org_addresses: set[str] = set()
        org_phones: set[str] = set()
        all_names: list[str] = []
        all_phones: list[str] = []
        all_addresses: list[str] = []

        evidence: list[EvidenceItem] = []

        for page in pages:
            # From JSON-LD
            for item in page.json_ld:
                if "Organization" in item.types or "LocalBusiness" in item.types:
                    name = item.data.get("name", "")
                    if name:
                        org_names.add(name.lower().strip())
                    address = item.data.get("address", {})
                    if isinstance(address, dict):
                        addr_str = f"{address.get('streetAddress', '')} {address.get('addressLocality', '')} {address.get('addressRegion', '')}".strip()
                        if addr_str:
                            org_addresses.add(addr_str.lower())
                    phone = item.data.get("telephone", "")
                    if phone:
                        org_phones.add(phone)

            # From visible text
            text = page.text
            found_phones = PHONE_RE.findall(text)
            found_addresses = ADDRESS_RE.findall(text)
            all_phones.extend(found_phones)
            all_addresses.extend(found_addresses)

        # Check consistency
        issues: list[str] = []

        if len(org_names) > 1:
            issues.append(f"Multiple organization names: {', '.join(org_names)}")
        elif len(org_names) == 1:
            # Consistent name found
            pass
        else:
            issues.append("No organization name found in schema")

        if len(org_addresses) > 1:
            issues.append(f"Multiple addresses in schema: {', '.join(org_addresses)}")

        # Check if phone/address appear consistently
        if org_phones and all_phones:
            phone_counts = Counter(all_phones)
            most_common = phone_counts.most_common(1)[0]
            if most_common[1] < len(pages) * 0.5:
                issues.append(f"Phone numbers inconsistent across pages (found {len(phone_counts)} unique)")

        if len(org_phones) == 0 and len(org_addresses) == 0:
            issues.append("No business contact info found in schema")

        if issues:
            # Populate evidence with the concrete values found, so the finding
            # is not generic ("name the exact page / show what you found").
            if not evidence:
                for page in pages:
                    phones = PHONE_RE.findall(page.text)[:2]
                    if phones or org_names or org_addresses or org_phones:
                        evidence.append(EvidenceItem(
                            page=page.url,
                            selector="",
                            snippet="; ".join(
                                [f"phone: {p}" for p in phones]
                                + [f"name: {n}" for n in list(org_names)[:1]]
                                + [f"address: {a}" for a in list(org_addresses)[:1]]
                            ),
                            source="html",
                        ))
            return self._build_result(
                False, max(0, 10 - len(issues) * 3),
                evidence,
                f"Entity consistency issues: {'; '.join(issues[:3])}. Use consistent Name/Address/Phone across all pages and schema.",
                confidence=0.8,
                effort="Medium",
                impact="Medium",
                fix_code=nap_schema(derive_site_name(pages)),
            )
        else:
            return self._build_result(
                True, 10, evidence,
                "Business information is consistent across pages.",
                confidence=1.0,
            )
