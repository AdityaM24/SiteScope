"""
URL validation and normalization utilities.
"""
from __future__ import annotations

import re
from typing import Optional, Tuple
from urllib.parse import urlparse, urljoin

import ipaddress


# Private IP ranges (RFC 1918 + special)
PRIVATE_PATTERNS = [
    r"^localhost$",
    r"^127\.",
    r"^10\.",
    r"^172\.(1[6-9]|2[0-9]|3[01])\.",
    r"^192\.168\.",
    r"^169\.254\.",
    r"^::1$",
    r"^fc00:",
    r"^fe80:",
    r"^\[",  # IPv6 bracket notation
]


def is_private_or_invalid(url: str) -> bool:
    """Return True if the URL points to a private/unreachable host."""
    parsed = urlparse(url)
    host = parsed.hostname or ""

    if not host:
        return True

    # Check against private patterns
    for pattern in PRIVATE_PATTERNS:
        if re.match(pattern, host, re.IGNORECASE):
            return True

    # Try IP address parsing
    try:
        ip = ipaddress.ip_address(host)
        if ip.is_private or ip.is_loopback or ip.is_link_local:
            return True
    except ValueError:
        pass  # Not an IP, it's a domain name — that's fine

    return False


def normalize_url(raw: str) -> Tuple[str, str]:
    """
    Normalize a user-submitted URL.
    Returns (canonical_url, domain).
    Raises ValueError on invalid input.
    """
    raw = raw.strip()
    if not raw:
        raise ValueError("URL is empty")

    # Add scheme if missing
    if not raw.startswith(("http://", "https://")):
        raw = "https://" + raw

    parsed = urlparse(raw)

    # Must be HTTP/HTTPS
    if parsed.scheme not in ("http", "https"):
        raise ValueError(f"Only HTTP/HTTPS URLs are supported, got: {parsed.scheme}")

    host = parsed.hostname
    if not host:
        raise ValueError("URL has no hostname")

    if is_private_or_invalid(raw):
        raise ValueError(f"Private or invalid host not allowed: {host}")

    # Build canonical homepage (strip path, fragment, query)
    scheme = parsed.scheme
    port = f":{parsed.port}" if parsed.port and parsed.port not in (80, 443) else ""
    domain = f"{scheme}://{host}{port}"

    return domain, host


def join_base(base: str, relative: str) -> Optional[str]:
    """Safely join a base URL with a relative path, respecting same-origin."""
    if not relative or not relative.startswith(("/", "http://", "https://")):
        return None
    joined = urljoin(base, relative)
    try:
        parsed = urlparse(joined)
        if parsed.scheme not in ("http", "https"):
            return None
        if is_private_or_invalid(joined):
            return None
        return joined
    except Exception:
        return None
