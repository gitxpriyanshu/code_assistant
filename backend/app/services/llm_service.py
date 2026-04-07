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
        """Send a prompt to the LLM and return the response text."""
        response = await self.llm.ainvoke(prompt)
        return response.content
