"""
Debug router.
Exposes endpoints for the AI debugging assistant.
"""

import logging

from fastapi import APIRouter, HTTPException, Request

from app.models.schemas import DebugRequest, DebugResponse, HealthResponse
from app.services.rag_service import RAGService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["debug"])


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
            detail=f"Failed to process debugging request: {str(e)}",
        )
