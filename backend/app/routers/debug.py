"""
Debug router.
Exposes endpoints for the AI debugging assistant.
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import DebugRequest, DebugResponse, ExplainResponse, HealthResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["debug"])
_PLACEHOLDER_LINE_BY_LINE = "Line-by-line analysis provided in summary."


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------
@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Simple health check endpoint."""
    return HealthResponse()


# ---------------------------------------------------------------------------
# Debug endpoint
# ---------------------------------------------------------------------------
@router.post("/debug", response_model=DebugResponse)
async def debug_code(request: DebugRequest, req: Request):
    """
    Accept code + error and return an AI-generated explanation, fix,
    and optimized version of the code.
    """
    try:
        # Get the vector store from app state (set during lifespan)
        vector_store = req.app.state.vector_store

        # Create the RAG service and run the pipeline
        rag_service = RAGService(vector_store=vector_store)
        result = await rag_service.debug(request)

        logger.info("Debug request processed successfully")
        return result

    except Exception as e:
        logger.error(f"Error processing debug request: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to process debugging request.",
        )

# ---------------------------------------------------------------------------
# Explain endpoint
# ---------------------------------------------------------------------------
@router.post("/explain", response_model=ExplainResponse)
async def explain_code(req: DebugRequest, request: Request):
    """
    Accept code and return a line-by-line explanation.
    """
    try:
        vector_store = request.app.state.vector_store
        rag_service = RAGService(vector_store=vector_store)
        
        # Backward compatibility: use the merged debug call but return only explain fields
        full_result = await rag_service.debug(req)
        explanation = full_result.line_by_line
        if not explanation or explanation == _PLACEHOLDER_LINE_BY_LINE:
            explanation = full_result.explanation
        
        return ExplainResponse(
            explanation=explanation,
            confidence=full_result.confidence,
            warning=full_result.warning,
            error_type=full_result.error_type,
        )

    except Exception as e:
        logger.error(f"Error processing explain request: {e}", exc_info=True)
        raise HTTPException(
            status_code=503,
            detail="Failed to process explanation request.",
        )
