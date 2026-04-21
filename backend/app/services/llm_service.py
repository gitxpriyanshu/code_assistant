"""
Groq LLM service.
Provides a configured ChatGroq instance for use in the RAG pipeline.
"""

import logging

from langchain_groq import ChatGroq

from app.config import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Thin wrapper around the Groq-hosted LLM."""

    def __init__(self) -> None:
        self._llm: ChatGroq | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def initialize(self) -> ChatGroq:
        """Create and return a ChatGroq instance."""
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not configured")
        logger.info(f"Initialising Groq LLM: {settings.model_name}")
        self._llm = ChatGroq(
            groq_api_key=settings.groq_api_key,
            model_name=settings.model_name,
            temperature=0.3,
            max_tokens=4096,
        )
        return self._llm

    # ------------------------------------------------------------------
    # Access
    # ------------------------------------------------------------------
    @property
    def llm(self) -> ChatGroq:
        if self._llm is None:
            return self.initialize()
        return self._llm

    async def agenerate(self, prompt: str) -> str:
        """Send a prompt to the LLM with automatic model fallback for 429 Rate Limits."""
        try:
            # 1. Attempt Primary Request
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            # 2. Check for Rate Limit (HTTP 429)
            error_str = str(e).lower()
            if "429" in error_str or "rate limit" in error_str:
                fallback_model = "llama-3.1-8b-instant"
                logger.warning(f"RATE LIMIT on {settings.model_name}. Switching to fallback: {fallback_model}")
                
                try:
                    # Initialize temporary fallback model
                    fallback_llm = ChatGroq(
                        groq_api_key=settings.groq_api_key,
                        model_name=fallback_model,
                        temperature=0.3,
                        max_tokens=2048
                    )
                    response = await fallback_llm.ainvoke(prompt)
                    return response.content
                except Exception as fallback_err:
                    logger.error(f"Fallback model also failed: {fallback_err}")
            
            # Re-raise to trigger local heuristic fallback if LLM is totally down
            raise e
