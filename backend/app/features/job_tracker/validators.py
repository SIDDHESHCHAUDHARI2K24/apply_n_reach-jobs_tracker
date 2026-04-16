"""Input validation helpers for the job_tracker feature."""
from urllib.parse import urlparse

from app.features.user_profile.validators import sanitize_text

_MAX_URL_LENGTH = 2048


def validate_url(url: str | None) -> str | None:
    """Validate and sanitize a URL string.

    Args:
        url: The URL to validate. Returns None if None.

    Returns:
        Sanitized URL string, or None if input is None.

    Raises:
        ValueError: If the URL scheme is not http/https or exceeds the max length.
    """
    if url is None:
        return None
    url = sanitize_text(url, max_length=_MAX_URL_LENGTH)
    if url is None:
        return None
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError(
            f"URL must use http or https scheme, got: {parsed.scheme!r}"
        )
    if not parsed.netloc:
        raise ValueError("URL must include a valid host")
    return url
