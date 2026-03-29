"""Standard error response envelope for the API."""
from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Consistent error envelope returned for all HTTP errors.

    Attributes:
        detail: Human-readable description of the error.
        code: HTTP status code repeated in the body for client convenience.
    """

    detail: str
    code: int
