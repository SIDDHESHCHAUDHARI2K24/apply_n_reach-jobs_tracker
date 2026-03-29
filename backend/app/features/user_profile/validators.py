"""Input validation and sanitization helpers for the user_profile feature."""
import re
from typing import Optional

import bleach

# Matches <script>...</script> and <style>...</style> with their inner content
_SCRIPT_STYLE_RE = re.compile(
    r"<(script|style)[^>]*>.*?</(script|style)>",
    flags=re.IGNORECASE | re.DOTALL,
)


def sanitize_text(value: Optional[str], max_length: int = 5000) -> Optional[str]:
    """Strip all HTML tags from a text value and enforce a maximum length.

    Args:
        value: The input string to sanitize. Returns None unchanged.
        max_length: Maximum allowed character length after sanitization.

    Returns:
        Sanitized string with all HTML stripped, or None if input is None.

    Raises:
        ValueError: If the cleaned text exceeds max_length characters.
    """
    if value is None:
        return None
    # Remove script/style elements including their inner content before bleach
    cleaned = _SCRIPT_STYLE_RE.sub("", value)
    cleaned = bleach.clean(cleaned, tags=[], attributes={}, strip=True)
    cleaned = cleaned.strip()
    if len(cleaned) > max_length:
        raise ValueError(f"Field exceeds maximum length of {max_length} characters")
    return cleaned
