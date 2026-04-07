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
        ...,
        min_length=1,
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
class DebugResponse(BaseModel):
    """Structured debugging result returned to the frontend."""

    explanation: str = Field(
        ...,
        description="Plain-English explanation of why the error occurs",
    )
    fix: str = Field(
        ...,
        description="Corrected version of the code",
    )
    optimized_code: str = Field(
        ...,
        description="Optimized / best-practice version of the code",
    )
    relevant_context: list[str] = Field(
        default_factory=list,
        description="Relevant knowledge-base snippets used for context",
    )


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    """Health-check response."""

    status: str = "healthy"
    service: str = "AI Debugging Assistant"
    version: str = "1.0.0"
