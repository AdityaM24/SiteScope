"""
Copy-pasteable fix snippets.

These are the "hand it to them" deliverables from the assignment: not a prose
description of the fix, but the actual code a site owner can paste.

Where possible the snippet is filled with data detected during the crawl
(company name, homepage URL, real FAQ questions) so it is site-specific,
not a generic template.
"""
from __future__ import annotations

import re
from typing import Any


# ---------------------------------------------------------------------------
# Site-data derivation helpers
# ---------------------------------------------------------------------------

_STRIP_RE = re.compile(
    r"\s*[\-–—|:]\s*(home|homepage|official|company|about us)$",
    re.IGNORECASE,
)


def derive_site_name(pages: list[Any]) -> str:
    """Best-guess company name from the homepage title."""
    for page in pages:
        title = (page.title or "").strip()
        if not title:
            continue
        # "Stripe - Online payments" -> "Stripe"
        for sep in (" - ", " – ", " — ", " | ", ": "):
            if sep in title:
                title = title.split(sep)[0]
                break
        # "Stripe - Home" -> "Stripe"
        title = _STRIP_RE.sub("", title).strip()
        if title:
            return title[:60]
    return "Your Company Name"


def derive_logo(pages: list[Any]) -> str:
    """Best-guess logo URL from og:image, twitter:image, or favicon."""
    for page in pages:
        if page.og_image:
            return page.og_image
        if page.twitter_image:
            return page.twitter_image
        return f"{page.domain}/favicon.ico"
    return "https://example.com/logo.png"


def derive_faq_questions(pages: list[Any], limit: int = 5) -> list[str]:
    """Extract question-like headings to seed an FAQ schema snippet."""
    questions: list[str] = []
    for page in pages:
        for h in page.headings.get(2, []) + page.headings.get(3, []):
            h = h.strip()
            if h.endswith("?") and h.lower() not in (q.lower() for q in questions):
                questions.append(h)
            if len(questions) >= limit:
                return questions
    return questions


# ---------------------------------------------------------------------------
# JSON-LD snippets
# ---------------------------------------------------------------------------

def org_schema(name: str, url: str) -> str:
    url = url.rstrip("/")
    return (
        '<script type="application/ld+json">\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Organization",\n'
        f'  "name": "{_escape_json(name)}",\n'
        f'  "url": "{url}/",\n'
        f'  "logo": "{url}/favicon.ico",\n'
        '  "sameAs": [\n'
        '    "https://twitter.com/yourhandle",\n'
        '    "https://www.linkedin.com/company/yourcompany"\n'
        "  ]\n"
        "}\n"
        "</script>"
    )


def faq_schema(questions: list[str]) -> str:
    if not questions:
        questions = ["What is your most common question here?"]
    blocks = []
    for i, q in enumerate(questions, 1):
        blocks.append(
            "    {\n"
            '      "@type": "Question",\n'
            f'      "name": "{_escape_json(q)}",\n'
            "      \"acceptedAnswer\": {\n"
            '        "@type": "Answer",\n'
            '        "text": "Paste the answer here."\n'
            "      }\n"
            "    }"
        )
    return (
        '<script type="application/ld+json">\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "FAQPage",\n'
        '  "mainEntity": [\n'
        + ",\n".join(blocks)
        + "\n  ]\n"
        "}\n"
        "</script>"
    )


def article_schema(title: str, url: str) -> str:
    url = url.rstrip("/")
    return (
        '<script type="application/ld+json">\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Article",\n'
        f'  "headline": "{_escape_json(title or "Your Article Title")}",\n'
        '  "datePublished": "2026-08-06",\n'
        '  "dateModified": "2026-08-06",\n'
        '  "author": {\n'
        '    "@type": "Person",\n'
        '    "name": "Author Name"\n'
        "  },\n"
        f'  "url": "{url}/"\n'
        "}\n"
        "</script>"
    )


def breadcrumb_schema(url: str) -> str:
    url = url.rstrip("/")
    return (
        '<script type="application/ld+json">\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "BreadcrumbList",\n'
        '  "itemListElement": [\n'
        "    {\n"
        '      "@type": "ListItem",\n'
        '      "position": 1,\n'
        '      "name": "Home",\n'
        f'      "item": "{url}/"\n'
        "    },\n"
        "    {\n"
        '      "@type": "ListItem",\n'
        '      "position": 2,\n'
        '      "name": "Current Page",\n'
        f'      "item": "{url}/current-page"\n'
        "    }\n"
        "  ]\n"
        "}\n"
        "</script>"
    )


def nap_schema(name: str) -> str:
    return (
        '<script type="application/ld+json">\n'
        "{\n"
        '  "@context": "https://schema.org",\n'
        '  "@type": "Organization",\n'
        f'  "name": "{_escape_json(name)}",\n'
        "  \"address\": {\n"
        '    "@type": "PostalAddress",\n'
        '    "streetAddress": "123 Main Street",\n'
        '    "addressLocality": "City",\n'
        '    "addressRegion": "State",\n'
        '    "postalCode": "12345",\n'
        '    "addressCountry": "US"\n'
        "  },\n"
        '  "telephone": "+1-555-123-4567",\n'
        '  "email": "hello@yourdomain.com"\n'
        "}\n"
        "</script>"
    )


# ---------------------------------------------------------------------------
# File / meta snippets
# ---------------------------------------------------------------------------

def robots_txt_allow_ai() -> str:
    return (
        "# Allow AI crawlers (so your site can appear in ChatGPT, Perplexity, etc.)\n"
        "User-agent: GPTBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: OAI-SearchBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: ClaudeBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: PerplexityBot\n"
        "Allow: /\n"
        "\n"
        "User-agent: Googlebot\n"
        "Allow: /\n"
        "\n"
        "# General rules\n"
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin/\n"
        "Disallow: /login/\n"
    )


def llms_txt(name: str, url: str) -> str:
    url = url.rstrip("/")
    return (
        f"# {_escape_md(name)}\n"
        "\n"
        f"> A short description of {_escape_md(name)} and what the site offers.\n"
        "\n"
        "## Key Pages\n"
        "\n"
        f"- [Home]({url}/)\n"
        f"- [About]({url}/about)\n"
        f"- [Contact]({url}/contact)\n"
        f"- [Products]({url}/products)\n"
    )


def sitemap_xml(url: str) -> str:
    url = url.rstrip("/")
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        "  <url>\n"
        f"    <loc>{url}/</loc>\n"
        "    <lastmod>2026-08-06</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "  </url>\n"
        "</urlset>\n"
    )


def date_modified_meta() -> str:
    return (
        '<meta property="article:modified_time" content="2026-08-06T10:00:00+00:00" />\n'
        '<meta property="og:updated_time" content="2026-08-06T10:00:00+00:00" />'
    )


def title_tag_example() -> str:
    return "<title>Page Name — Under 60 Characters</title>"


def meta_description_example() -> str:
    return (
        '<meta name="description" content="Write a 150–160 character summary of this page '
        "that describes exactly what visitors will find here.\" />"
    )


def heading_structure_example() -> str:
    return (
        "<h1>Page Title</h1>\n"
        "<h2>Main Section Heading</h2>\n"
        "<p>Content...</p>\n"
        "<h3>Subsection Heading</h3>\n"
        "<p>More content...</p>"
    )


# ---------------------------------------------------------------------------
# small escaping helpers
# ---------------------------------------------------------------------------

def _escape_json(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"').replace("\n", " ")


def _escape_md(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")
