"""
HTTP fetcher — async page downloader with timeout and redirect handling.
"""
from __future__ import annotations

import logging
from typing import Optional

import re

import httpx

from ..config import settings

logger = logging.getLogger(__name__)


async def fetch_url(
    url: str,
    timeout: int = 30,
    max_redirects: int = 5,
    max_size: int = 5_000_000,
) -> tuple[int, str, dict[str, str]]:
    """
    Fetch a URL and return (status_code, html, headers_dict).
    Raises on network failure or timeout.
    """
    async with httpx.AsyncClient(
        follow_redirects=True,
        max_redirects=max_redirects,
        timeout=timeout,
        headers={"User-Agent": settings.USER_AGENT},
        verify=False,  # Allow self-signed certs in dev
    ) as client:
        resp = await client.get(url)
        html = resp.text
        if len(html.encode("utf-8", errors="replace")) > max_size:
            logger.warning("Large page truncated: %s (%d bytes)", url, len(html))
            html = html[: int(max_size * 0.9)]
        headers = {k.lower(): v for k, v in resp.headers.items()}
        return resp.status_code, html, headers


async def fetch_robots_txt(domain: str) -> Optional[str]:
    """Fetch robots.txt for a domain. Returns content or None on 404/error."""
    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}/robots.txt"
        try:
            status, html, _ = await fetch_url(url, timeout=10)
            if status == 200:
                return html
            if status == 404:
                return None
            logger.debug("robots.txt returned %d for %s", status, url)
        except Exception as e:
            logger.debug("robots.txt fetch failed for %s: %s", url, e)
    return None


async def fetch_llms_txt(domain: str) -> Optional[str]:
    """Fetch llms.txt for a domain. Returns content or None on 404/error."""
    for scheme in ("https", "http"):
        url = f"{scheme}://{domain}/llms.txt"
        try:
            status, html, _ = await fetch_url(url, timeout=10)
            if status == 200:
                return html
            if status == 404:
                return None
        except Exception as e:
            logger.debug("llms.txt fetch failed for %s: %s", url, e)
    return None


async def fetch_sitemap(domain: str, declared_urls: list[str] | None = None) -> Optional[str]:
    """
    Fetch sitemap.xml. Tries declared_urls from robots.txt first, then
    the conventional paths as fallback.
    """
    # Build candidate list: declared first, then conventional
    candidates: list[str] = []
    for url in (declared_urls or []):
        if url.startswith(("http://", "https://")):
            candidates.append(url)
    for scheme in ("https", "http"):
        for path in ("/sitemap.xml", "/sitemap_index.xml"):
            candidates.append(f"{scheme}://{domain}{path}")

    seen: set[str] = set()
    for url in candidates:
        if url in seen:
            continue
        seen.add(url)
        try:
            status, html, _ = await fetch_url(url, timeout=10)
            if status == 200 and ("<urlset" in html.lower() or "<sitemapindex" in html.lower()):
                logger.info("Sitemap found: %s", url)
                return html
            if status == 404:
                continue
        except Exception as e:
            logger.debug("sitemap fetch failed for %s: %s", url, e)
    return None


def parse_sitemaps_from_robots(robots_content: str | None) -> list[str]:
    """Extract Sitemap: URLs declared in robots.txt."""
    if not robots_content:
        return []
    pattern = re.compile(r"^\s*Sitemap:\s*(\S+)", re.IGNORECASE | re.MULTILINE)
    return pattern.findall(robots_content)
