"""LinkedIn import error taxonomy.

HTTP status mapping (agreed matrix — see development plan Appendix C):
- Missing/invalid server config (apify_api_token) → 503
- Invalid/non-LinkedIn URL after validation → 422
- Empty scrape result / unparsable profile → 422 or 502
- Apify 401/403/quota → 502
- Transient network / 5xx to Apify (retries exhausted) → 502 or 503
- LLM / mapping failure → 424 (or 503 + error_code)
"""

from enum import StrEnum


class ImportStage(StrEnum):
    config = "config"
    validation = "validation"
    scrape = "scrape"
    map = "map"


class ErrorCode(StrEnum):
    MISSING_API_TOKEN = "MISSING_API_TOKEN"
    INVALID_LINKEDIN_URL = "INVALID_LINKEDIN_URL"
    APIFY_QUOTA_EXCEEDED = "APIFY_QUOTA_EXCEEDED"
    APIFY_BAD_CREDENTIALS = "APIFY_BAD_CREDENTIALS"
    EMPTY_SCRAPE_RESULT = "EMPTY_SCRAPE_RESULT"
    UPSTREAM_ERROR = "UPSTREAM_ERROR"
    SCRAPE_TIMEOUT = "SCRAPE_TIMEOUT"
    RETRIES_EXHAUSTED = "RETRIES_EXHAUSTED"
    LLM_FAILURE = "LLM_FAILURE"
    UNEXPECTED_RESULT = "UNEXPECTED_RESULT"


class LinkedInImportAppError(Exception):
    """Domain error for LinkedIn import pipeline.

    Carries stage, error_code, message, and target http_status so the
    router can map to HTTPException with structured detail.
    """

    def __init__(
        self,
        message: str,
        *,
        stage: ImportStage,
        code: ErrorCode,
        http_status: int = 502,
    ):
        super().__init__(message)
        self.stage = stage
        self.code = code
        self.http_status = http_status

    def to_http_detail(self) -> dict:
        """Produce the structured detail dict for HTTPException."""
        return {
            "message": str(self),
            "error_code": self.code.value,
            "stage": self.stage.value,
        }
