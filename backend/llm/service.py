"""
LLM explanation service with template fallback.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from openai import AsyncOpenAI

from ..config import settings
from ..models import Issue

logger = logging.getLogger(__name__)


def _get_llm() -> tuple[AsyncOpenAI | None, str | None]:
    """
    Return (client, model) for the configured provider, or (None, None) when
    the provider's API key is missing so callers fall back to templates.
    """
    if settings.LLM_PROVIDER == "groq":
        if not settings.GROQ_API_KEY:
            return None, None
        return (
            AsyncOpenAI(api_key=settings.GROQ_API_KEY, base_url=settings.GROQ_BASE_URL),
            settings.GROQ_LLM_MODEL,
        )
    # default: openai
    if not settings.OPENAI_API_KEY:
        return None, None
    return AsyncOpenAI(api_key=settings.OPENAI_API_KEY), settings.LLM_MODEL


async def _chat(system_prompt: str, user_prompt: str, max_tokens: int = 300) -> str | None:
    """
    Send a single chat completion through the configured provider.
    Returns the trimmed text, or None on any failure (network, quota, key, etc.).
    """
    client, model = _get_llm()
    if client is None or model is None:
        logger.info("No API key configured for provider=%s — skipping LLM", settings.LLM_PROVIDER)
        return None

    try:
        resp = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=max_tokens,
        )
        text = resp.choices[0].message.content
        return text.strip() if text else None
    except Exception as e:
        logger.warning("LLM (%s/%s) call failed — using template: %s", settings.LLM_PROVIDER, model, e)
        return None

# Pre-defined templates for common issues (used when LLM is unavailable)
TEMPLATE_EXPLANATIONS: dict[str, str] = {
    "robots.txt": (
        "Your robots.txt file is blocking AI crawlers like GPTBot or ClaudeBot. "
        "AI assistants won't be able to read your content, making your business invisible in AI answers. "
        "Fix: Remove any 'Disallow: /' lines and explicitly allow AI bot user agents."
    ),
    "llms.txt": (
        "Your site doesn't have an llms.txt file. This emerging standard helps AI crawlers "
        "understand your site's structure and prioritize important content. "
        "Fix: Create a /llms.txt file starting with '# Your Site Name' followed by a brief description "
        "and links to your key pages."
    ),
    "sitemap.xml": (
        "No sitemap.xml was found. Sitemaps help AI crawlers discover and prioritize your pages. "
        "Fix: Generate an XML sitemap listing your important URLs with <lastmod> dates."
    ),
    "Organization Schema": (
        "Your site is missing Organization schema (JSON-LD). AI assistants use this to identify your business "
        "entity, connect your pages, and cite you by name. Without it, AI may not trust or attribute content correctly. "
        "Fix: Add a JSON-LD script with @type: 'Organization', including name, url, logo, and contactPoint."
    ),
    "FAQ Schema": (
        "FAQ content exists on your site but isn't marked up with FAQPage schema. "
        "AI assistants heavily favor structured Q&A — pages with FAQ schema are cited significantly more often. "
        "Fix: Add FAQPage JSON-LD with each question/answer pair, or ensure Q&A is clearly formatted in HTML."
    ),
    "Article Schema": (
        "Your article/blog pages are missing Article or BlogPosting schema. "
        "This markup tells AI systems your content has an author, publish date, and topic — key signals for citation. "
        "Fix: Add Article JSON-LD with headline, datePublished, author, and description."
    ),
    "Breadcrumb Schema": (
        "No BreadcrumbList schema was found. While less critical, breadcrumbs help AI understand your site hierarchy. "
        "Fix: Add BreadcrumbList JSON-LD showing the path from Home to the current page."
    ),
    "Title Tag": (
        "Some pages are missing title tags. Titles are the strongest retrieval signal for AI — they appear in snippets "
        "and help AI understand what each page is about. "
        "Fix: Add a unique <title> tag (50-60 characters) to every page."
    ),
    "Meta Description": (
        "Meta descriptions are missing on several pages. AI uses these to verify page context and generate summaries. "
        "Fix: Add <meta name='description'> tags (150-160 characters) summarizing each page."
    ),
    "Heading Structure": (
        "Heading structure is inconsistent across pages. AI extracts answers from well-structured content — "
        "clear H1/H2/H3 hierarchy makes it easy for AI to find and cite specific sections. "
        "Fix: Use exactly one H1 per page, and organize sections with H2/H3 tags."
    ),
    "Business Info Consistency": (
        "Business name, address, or phone number is inconsistent across pages. AI relies on entity consistency "
        "to build accurate knowledge graphs. Inconsistencies confuse AI and reduce trust. "
        "Fix: Use a single canonical business name, address, and phone across all pages and schema."
    ),
    "Content Freshness": (
        "Content on your site appears stale. AI assistants prefer recently updated content — "
        "studies show AI-cited pages are ~25% fresher than organic results. "
        "Fix: Add 'last modified' dates and update content older than 2 years."
    ),
}


def _get_template_explanation(issue_name: str) -> str:
    """Get a template explanation for a known issue."""
    for key, text in TEMPLATE_EXPLANATIONS.items():
        if key.lower() in issue_name.lower() or issue_name.lower() in key.lower():
            return text
    return (
        f"Issue: {issue_name}. "
        "This finding suggests an area for improvement in your site's AI citation readiness. "
        "Addressing it can increase visibility in AI search results."
    )


async def generate_executive_summary(
    overall_score: int,
    category_scores: list,
    issues: list[Issue],
) -> str:
    """
    Generate a business-friendly executive summary.
    Uses LLM if API key is configured, otherwise falls back to template.
    """
    # Build a concise context for the LLM
    context = f"Overall score: {overall_score}/100.\nCategories: " + ", ".join(
        f"{cs.category} {cs.score}/{cs.max_score}" for cs in category_scores
    ) + f"\nTop issues: {', '.join(i.title for i in issues[:5])}"

    llm_text = await _chat(
        system_prompt=(
            "You are a GEO (Generative Engine Optimization) auditor. Write concise, "
            "business-friendly executive summaries. No jargon — explain terms inline. "
            "Max 3 sentences. Always mention the score and top 2-3 issues."
        ),
        user_prompt=f"Summarize this audit: {context}",
        max_tokens=300,
    )
    if llm_text:
        return llm_text

    # Fallback template
    strengths = [cs for cs in category_scores if cs.score == cs.max_score]
    weaknesses = sorted(
        [cs for cs in category_scores if cs.score < cs.max_score],
        key=lambda x: x.score,
    )

    summary = f"Your site scores {overall_score}/100 for AI citation readiness. "
    if strengths:
        summary += "Strengths: " + ", ".join(s.category for s in strengths) + ". "
    if weaknesses:
        summary += "Key issues: " + ", ".join(w.category for w in weaknesses[:2]) + ". "
    if issues:
        summary += f"Priority fixes: {', '.join(i.title for i in issues[:2])}."
    return summary


async def generate_issue_explanation(issue: Issue) -> str:
    """
    Generate a business-friendly explanation for a single issue.
    Uses LLM if available, otherwise returns template.
    """
    llm_text = await _chat(
        system_prompt=(
            "You are a GEO consultant. Explain WHY this issue matters for AI visibility "
            "in plain business language (2-3 sentences). No jargon without explanation."
        ),
        user_prompt=f"Issue: {issue.title}\nEvidence: {issue.evidence}\nRecommendation: {issue.recommendation}",
        max_tokens=200,
    )
    if llm_text:
        return llm_text

    return _get_template_explanation(issue.title)
