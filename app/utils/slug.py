"""Slug generation for URLs."""

import re
import unicodedata


def slugify(text: str, max_length: int = 500) -> str:
    """Convert text to a URL-safe slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^\w\s-]", "", text).strip().lower()
    text = re.sub(r"[-\s]+", "-", text)
    return text[:max_length].strip("-") or "slug"
