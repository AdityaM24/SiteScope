"""
HTML content extractor — turns raw HTML into structured Page objects.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Optional

from bs4 import BeautifulSoup, Tag

from ..models import JSONLDItem, Page

logger = logging.getLogger(__name__)

# Pre-compiled patterns
_H1_RE = re.compile(r"<h1[^>]*>(.*?)</h1>", re.IGNORECASE | re.DOTALL)
_H2_RE = re.compile(r"<h2[^>]*>(.*?)</h2>", re.IGNORECASE | re.DOTALL)
_H3_RE = re.compile(r"<h3[^>]*>(.*?)</h3>", re.IGNORECASE | re.DOTALL)
_TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)
_META_DESC_RE = re.compile(
    r'<meta\s+name=["\']description["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_CANONICAL_RE = re.compile(
    r'<link\s+rel=["\']canonical["\']\s+href=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_OG_TITLE_RE = re.compile(
    r'<meta\s+property=["\']og:title["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_OG_DESC_RE = re.compile(
    r'<meta\s+property=["\']og:description["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_TWITTER_TITLE_RE = re.compile(
    r'<meta\s+name=["\']twitter:title["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_TWITTER_DESC_RE = re.compile(
    r'<meta\s+name=["\']twitter:description["\']\s+content=["\']([^"\']*)["\']',
    re.IGNORECASE,
)
_LINK_RE = re.compile(r'<a\s+[^>]*href=["\']([^"\']*)["\'][^>]*>')
_JSONLD_RE = re.compile(r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', re.DOTALL | re.IGNORECASE)


def _strip_html(text: str) -> str:
    """Remove HTML tags and return plain text."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.get_text(separator=" ", strip=True)


def _extract_heading_text(tag: Tag) -> str:
    """Get plain-text content from a heading tag."""
    return _strip_html(str(tag))


def extract_headings(html: str) -> dict[int, list[str]]:
    """Extract H1, H2, H3 texts from HTML."""
    soup = BeautifulSoup(html, "html.parser")
    result: dict[int, list[str]] = {}
    for level in (1, 2, 3):
        tags = soup.find_all(f"h{level}")
        texts = [_strip_html(str(t)) for t in tags if _strip_html(str(t)).strip()]
        if texts:
            result[level] = texts
    return result


def extract_json_ld(html: str) -> list[JSONLDItem]:
    """Parse all <script type='application/ld+json'> blocks."""
    items: list[JSONLDItem] = []
    for match in _JSONLD_RE.findall(html):
        text = match.strip()
        if not text:
            continue
        try:
            data = json.loads(text)
            # Normalize to list for easier handling
            if isinstance(data, dict):
                data = [data]
            if not isinstance(data, list):
                continue
            for item in data:
                if not isinstance(item, dict):
                    continue
                types: list[str] = []
                t = item.get("@type", "")
                if isinstance(t, str):
                    types.append(t)
                elif isinstance(t, list):
                    types.extend(t)
                # Also check nested items
                for ent in item.get("mainEntity", []):
                    if isinstance(ent, dict):
                        et = ent.get("@type", "")
                        if isinstance(et, str):
                            types.append(et)
                        elif isinstance(et, list):
                            types.extend(et)
                items.append(JSONLDItem(raw=text, data=item, types=list(set(types))))
        except (json.JSONDecodeError, ValueError) as e:
            logger.debug("Failed to parse JSON-LD block: %s", e)
    return items


def extract_page(url: str, html: str, status_code: int, headers: dict[str, str]) -> Page:
    """Extract structured data from raw HTML into a Page model."""
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title_tag = soup.find("title")
    title = _strip_html(str(title_tag)) if title_tag else ""

    # Meta description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = (meta_desc_tag.get("content", "").strip() if meta_desc_tag else "")

    # Canonical
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else None

    # OG tags
    og_title_tag = soup.find("meta", attrs={"property": "og:title"})
    og_title = og_title_tag.get("content", "").strip() if og_title_tag else None
    og_desc_tag = soup.find("meta", attrs={"property": "og:description"})
    og_description = og_desc_tag.get("content", "").strip() if og_desc_tag else None

    # Twitter tags
    twitter_title_tag = soup.find("meta", attrs={"name": "twitter:title"})
    twitter_title = twitter_title_tag.get("content", "").strip() if twitter_title_tag else None
    twitter_desc_tag = soup.find("meta", attrs={"name": "twitter:description"})
    twitter_description = twitter_desc_tag.get("content", "").strip() if twitter_desc_tag else None
    og_image_tag = soup.find("meta", attrs={"property": "og:image"})
    og_image = og_image_tag.get("content", "").strip() if og_image_tag else None
    twitter_image_tag = soup.find("meta", attrs={"name": "twitter:image"})
    twitter_image = twitter_image_tag.get("content", "").strip() if twitter_image_tag else None

    # Headings
    headings = extract_headings(html)

    # Links
    links: list[str] = []
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href and not href.startswith(("javascript:", "mailto:", "tel:")):
            links.append(href)

    # JSON-LD
    json_ld = extract_json_ld(html)

    # Full text
    body = soup.find("body")
    text = _strip_html(str(body)) if body else _strip_html(html)

    # Last modified — try multiple sources
    last_modified: Optional[str] = None
    # HTTP header
    lm_header = headers.get("last-modified") or headers.get("Last-Modified")
    if lm_header:
        last_modified = lm_header
    # Meta tag
    else:
        for attr_name in ("dateModified", "article:modified_time", "og:updated_time"):
            tag = soup.find("meta", attrs={"property": attr_name}) or soup.find(
                "meta", attrs={"name": attr_name}
            )
            if tag and tag.get("content"):
                last_modified = tag["content"].strip()
                break
        if not last_modified:
            time_tag = soup.find("time")
            if time_tag:
                last_modified = time_tag.get("datetime") or time_tag.get_text(strip=True)

    # Domain and path from URL
    from urllib.parse import urlparse
    parsed = urlparse(url)
    domain = parsed.netloc
    path = parsed.path or "/"

    return Page(
        url=url,
        status_code=status_code,
        html=html,
        text=text,
        title=title,
        meta_description=meta_description,
        canonical=canonical,
        og_title=og_title,
        og_description=og_description,
        og_image=og_image,
        twitter_title=twitter_title,
        twitter_description=twitter_description,
        twitter_image=twitter_image,
        headings=headings,
        links=links,
        json_ld=json_ld,
        last_modified=last_modified,
        headers=headers,
        domain=domain,
        path=path,
    )
