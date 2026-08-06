"""
Project configuration via environment variables.
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load backend/.env before reading any env vars so os.getenv() picks it up.
# Path is anchored to this file, so it works no matter where uvicorn is launched from.
# override=True: the .env file wins over stale machine-level env vars (e.g. an old API key).
_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH, override=True)


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )


# ---------------------------------------------------------------------------
# Settings (loaded from env or defaults)
# ---------------------------------------------------------------------------

class Settings:
    """All tunable settings for the GEO Auditor."""

    # LLM
    # Provider: "groq" (free, fast) or "openai". OpenAIs' AsyncOpenAI client is reused for
    # both — Groq exposes an OpenAI-compatible API, so no extra SDK is required.
    LLM_PROVIDER: str = os.getenv("GEO_LLM_PROVIDER", "groq").lower()
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    LLM_MODEL: str = os.getenv("GEO_LLM_MODEL", "gpt-4o-mini")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    GROQ_LLM_MODEL: str = os.getenv("GROQ_LLM_MODEL", "llama-3.3-70b-versatile")
    GROQ_BASE_URL: str = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
    LLM_TEMPERATURE: float = 0.0
    MAX_LLM_TOKENS: int = int(os.getenv("GEO_MAX_LLM_TOKENS", "2000"))

    # Crawler
    CRAWL_TIMEOUT_SECONDS: int = int(os.getenv("GEO_CRAWL_TIMEOUT", "30"))
    MAX_PAGES: int = int(os.getenv("GEO_MAX_PAGES", "20"))
    MAX_CRAWL_DEPTH: int = int(os.getenv("GEO_MAX_DEPTH", "2"))
    MAX_HTML_BYTES: int = int(os.getenv("GEO_MAX_HTML", "5000000"))
    USER_AGENT: str = os.getenv(
        "GEO_USER_AGENT",
        "Mozilla/5.0 (compatible; GEO-Auditor/1.0; +https://geo-auditor.dev/bot)",
    )

    # Server
    HOST: str = os.getenv("GEO_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("GEO_PORT", "8000"))


settings = Settings()
