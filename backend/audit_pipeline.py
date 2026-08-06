"""
Audit pipeline — orchestrates the full audit workflow.
"""
from __future__ import annotations

import asyncio
import logging
from typing import Optional

from .crawler.fetcher import fetch_llms_txt, fetch_robots_txt, fetch_sitemap, parse_sitemaps_from_robots
from .crawler.service import crawl
from .checks import ALL_CHECKS
from .models import AuditRequest, CrawlResult
from .report.generator import generate_report
from .scoring.engine import compute_scores, compute_overall

logger = logging.getLogger(__name__)


async def run_audit(request: AuditRequest) -> dict:
    """
    Run the full GEO audit pipeline.
    Returns a dict matching the REPORT_SCHEMA.
    """
    # 1. Validate and normalize URL
    from .crawler.url_utils import normalize_url
    try:
        domain, host = normalize_url(request.url)
    except ValueError as e:
        raise ValueError(f"Invalid URL: {e}")

    homepage = domain.rstrip("/") + "/"

    # 2. Crawl
    logger.info("Starting crawl for %s", homepage)
    crawl_result: CrawlResult = await crawl(domain, homepage)

    if not crawl_result.pages:
        raise RuntimeError(f"Could not crawl any pages from {homepage}")

    # 3. Fetch auxiliary files (robots.txt, llms.txt, sitemap)
    #    Sitemap URLs may be declared in robots.txt, so fetch robots first,
    #    parse its Sitemap: directives, then fetch llms + sitemap concurrently.
    try:
        robots = await fetch_robots_txt(domain)
    except Exception as e:
        logger.warning("Failed to fetch robots.txt: %s", e)
        robots = None

    declared_sitemaps = parse_sitemaps_from_robots(robots)
    try:
        llms, sitemap = await asyncio.gather(
            fetch_llms_txt(domain),
            fetch_sitemap(domain, declared_sitemaps),
            return_exceptions=True,
        )
    except Exception as e:
        logger.warning("Failed to fetch aux files: %s", e)
        llms, sitemap = None, None

    # Attach to pages
    for page in crawl_result.pages:
        page._robots_content = robots if isinstance(robots, str) else None
        page._llms_content = llms if isinstance(llms, str) else None
        page._sitemap_content = sitemap if isinstance(sitemap, str) else None

    # 4. Run all checks
    logger.info("Running %d checks on %d pages", len(ALL_CHECKS), len(crawl_result.pages))
    check_results = await asyncio.gather(*[asyncio.to_thread(check.run, crawl_result.pages) for check in ALL_CHECKS])

    # 5. Generate report
    logger.info("Generating report")
    report = await generate_report(domain, list(check_results))

    return report.model_dump()
