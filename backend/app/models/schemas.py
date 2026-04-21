"""
Pydantic schemas for request / response validation.
"""

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------
class DebugRequest(BaseModel):
    """Payload sent by the frontend when the user requests debugging help."""

    code: str = Field(
        ...,
        min_length=1,
        description="The source code to debug",
        json_schema_extra={"example": "def add(a, b):\n    return a + b\n\nprint(add(1, '2'))"},
    )
    error_message: str = Field(
        default="",
        description="The error or traceback the user encountered",
        json_schema_extra={"example": "TypeError: unsupported operand type(s) for +: 'int' and 'str'"},
    )
    language: str = Field(
        default="python",
        description="Programming language of the code snippet",
        json_schema_extra={"example": "python"},
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------
class BaseAIResponse(BaseModel):
    """Shared fields across all AI-generated responses."""
    explanation: str
    confidence: float
    warning: str | None = None


class DebugResponse(BaseAIResponse):
    """Full debug pipeline response including fix, optimized code, and sources."""
    line_by_line: str = ""
    fix: str
    optimized_code: str
    why_fix_works: str = ""
    sources: list[str] = []
    error_type: str | None = None
    confidence_reason: str | None = None


class ExplainResponse(BaseAIResponse):
    """Line-by-line code explanation response."""
    error_type: str | None = None


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "healthy"
    service: str = "AI Debugging Assistant"
    version: str = "1.0.0"
