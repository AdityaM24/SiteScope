"""
Check: robots.txt — ensure AI crawlers are not blocked.
"""
from __future__ import annotations

import re

from ..models import CheckResult, EvidenceItem
from .base import CheckBase
from .fix_snippets import robots_txt_allow_ai

# AI bot user agents we care about
AI_BOTS = ["GPTBot", "OAI-SearchBot", "PerplexityBot", "ClaudeBot", "Googlebot"]


class RobotsTxtCheck(CheckBase):
    def __init__(self):
        super().__init__(
            check_id="robots_txt",
            name="robots.txt",
            category="AI Accessibility",
            max_score=10,
        )
        self._disallow_re = re.compile(r"^\s*Disallow:\s*(.+)", re.IGNORECASE)
        self._useragent_re = re.compile(r"^\s*User-agent:\s*(.+)", re.IGNORECASE)

    def run(self, pages) -> CheckResult:
        """
        Fetch robots.txt for the domain and check if AI bots are blocked.
        """
        if not pages:
            return self._build_result(False, 0, [], "No pages to check.")

        domain = pages[0].domain
        # We need the raw robots.txt content — fetched separately in the audit pipeline
        robots_content = getattr(self, "aux", None)
        robots_content = robots_content.robots_content if robots_content else None

        if robots_content is None:
            # robots.txt not available — default allow, but score 0 (missing file)
            return self._build_result(
                False, 0,
                [EvidenceItem(
                    page=domain,
                    selector="",
                    snippet=f"GET https://{domain}/robots.txt returned 404. No robots.txt exists. AI crawlers (GPTBot, ClaudeBot, PerplexityBot) will use site defaults — you have no control over which pages they access.",
                    source="http",
                )],
                "Add a robots.txt file to guide AI and search crawlers.",
                confidence=0.7,
                effort="Low",
                impact="Medium",
                fix_code=robots_txt_allow_ai(),
            )

        # Parse robots.txt
        rules: dict[str, list[str]] = {}  # user_agent -> [disallow paths]
        current_agent = "*"
        for line in robots_content.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            ua_match = self._useragent_re.match(line)
            if ua_match:
                current_agent = ua_match.group(1).strip()
                if current_agent not in rules:
                    rules[current_agent] = []
                continue
            dis_match = self._disallow_re.match(line)
            if dis_match and current_agent in rules:
                rules[current_agent].append(dis_match.group(1).strip())

        # Check if any AI bot is explicitly blocked
        blocked_bots = []
        all_blocked = False
        for bot in AI_BOTS:
            bot_rules = rules.get(bot, []) + rules.get("*", [])
            if any(self._is_blocking(bot_rules, "/")):
                blocked_bots.append(bot)

        # Check if there's a blanket Disallow: /
        for agent, paths in rules.items():
            if "/" in paths:
                all_blocked = True
                break

        if all_blocked:
            return self._build_result(
                False, 0,
                [EvidenceItem(page=domain, selector="", snippet="robots.txt blocks all pages (Disallow: /)", source="http")],
                "robots.txt blocks all crawling. Remove 'Disallow: /' to allow AI crawlers access.",
                confidence=1.0,
                impact="High",
                fix_code=robots_txt_allow_ai(),
            )

        if blocked_bots:
            return self._build_result(
                False, 3,
                [EvidenceItem(page=domain, selector="", snippet=f"AI bots blocked: {', '.join(blocked_bots)}", source="http")],
                f"The following AI crawlers are blocked in robots.txt: {', '.join(blocked_bots)}. Allow them to improve AI visibility.",
                confidence=0.9,
                impact="High",
                fix_code=robots_txt_allow_ai(),
            )

        return self._build_result(
            True, 10,
            [EvidenceItem(page=domain, selector="", snippet="No AI bots blocked in robots.txt", source="http")],
            "robots.txt looks good for AI crawlers.",
            confidence=1.0,
        )

    def _is_blocking(self, disallow_paths: list[str], url_path: str) -> bool:
        """Check if any Disallow rule would block the given path."""
        for path in disallow_paths:
            if path == "/" or path == "":
                return True
            if url_path.startswith(path):
                return True
        return False
