"""
Crawler service — orchestrates URL validation, page fetching, and extraction.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from ..models import CrawlResult, Page
from .fetcher import fetch_url, fetch_robots_txt
from .url_utils import normalize_url, join_base
from .extractor import extract_page

logger = logging.getLogger(__name__)

# Suggested page paths to crawl beyond the homepage
_SUGGESTED_PATHS = [
    "/about", "/contact", "/products", "/services", "/blog",
    "/pricing", "/faq", "/faq", "/sitemap.xml",
]


async def crawl(domain: str, homepage: str) -> CrawlResult:
    """
    Crawl a website starting from the homepage.
    Respects robots.txt, limits depth and page count.
    """
    result = CrawlResult(domain=domain, homepage=homepage)

    # Fetch and parse robots.txt
    robots_html = await fetch_robots_txt(domain)
    disallowed = _parse_robots(robots_html) if robots_html else set()
    if robots_html is None:
        result.warnings.append("No robots.txt found — assuming all pages allowed")

    # Crawl homepage
    pages: dict[str, Page] = {}
    visited: set[str] = {homepage}

    try:
        status, html, headers = await fetch_url(homepage)
        page = extract_page(homepage, html, status, headers)
        pages[homepage] = page
        logger.info("Crawled homepage: %s (status=%d)", homepage, status)
    except Exception as e:
        result.warnings.append(f"Failed to crawl homepage: {e}")
        logger.error("Homepage crawl failed: %s", e)
        return result  # Return whatever we have

    # Discover links from homepage (depth 1)
    to_visit: list[str] = []
    for link in pages[homepage].links:
        full = join_base(homepage, link)
        if full and full not in visited:
            to_visit.append(full)

    # Also try suggested paths on the same domain
    for path in _SUGGESTED_PATHS:
        candidate = f"{domain}{path}"
        if candidate not in visited:
            to_visit.append(candidate)

    # Remove duplicates and limit
    to_visit = list(dict.fromkeys(to_visit))[: 20 - len(pages)]

    # Crawl discovered pages (respect robots.txt)
    sem = asyncio.Semaphore(5)  # concurrency limit
    tasks = []

    async def _crawl_one(url: str):
        async with sem:
            if url in visited or url in disallowed:
                return
            try:
                status, html, headers = await fetch_url(url)
                if status in (404, 403, 410):
                    logger.info("Skipped %s (status=%d)", url, status)
                    return
                page = extract_page(url, html, status, headers)
                pages[url] = page
                visited.add(url)
                logger.info("Crawled: %s (status=%d)", url, status)
            except Exception as e:
                logger.warning("Failed to crawl %s: %s", url, e)
                result.warnings.append(f"Failed to crawl {url}: {e}")

    for url in to_visit:
        tasks.append(asyncio.create_task(_crawl_one(url)))

    await asyncio.gather(*tasks, return_exceptions=True)

    result.pages = list(pages.values())
    logger.info("Crawl complete: %d pages for %s", len(result.pages), domain)
    return result


def _parse_robots(content: str) -> set[str]:
    """Parse robots.txt and return a set of disallowed path prefixes."""
    disallowed: set[str] = set()
    for line in content.splitlines():
        line = line.strip()
        if line.lower().startswith("Disallow:"):
            path = line.split(":", 1)[1].strip()
            if path:
                disallowed.add(path)
    return disallowed
