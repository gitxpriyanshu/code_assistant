"""
FAISS vector store service.
Manages the embedding model, FAISS index creation, persistence,
document ingestion, and similarity search.
"""

import logging
import os
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from langchain.schema import Document

from app.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """Wraps a FAISS vector store with convenience methods."""

    def __init__(self) -> None:
        self._embeddings: FastEmbedEmbeddings | None = None
        self._store: FAISS | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    def initialize(self) -> None:
        """Load the embedding model and — if available — a persisted index."""
        logger.info(f"Loading lightweight FastEmbed embedding model: {settings.embedding_model}")
        self._embeddings = FastEmbedEmbeddings(
            model_name="BAAI/bge-small-en-v1.5",
        )

        index_path = Path(settings.faiss_index_path)
        if index_path.exists() and (index_path / "index.faiss").exists():
            logger.info(f"Loading existing FAISS index from {index_path}")
            self._store = FAISS.load_local(
                str(index_path),
                self._embeddings,
                allow_dangerous_deserialization=True,
            )
        else:
            logger.info("No existing index found — will create on first ingestion")

    # ------------------------------------------------------------------
    # Ingestion
    # ------------------------------------------------------------------
    def add_documents(self, documents: list[Document]) -> None:
        """Add LangChain `Document` objects to the FAISS index and persist."""
        if not documents:
            return

        if self._store is None:
            self._store = FAISS.from_documents(documents, self._embeddings)
        else:
            self._store.add_documents(documents)

        self._persist()
        logger.info(f"Added {len(documents)} documents to FAISS index")

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------
    def similarity_search(self, query: str, k: int = 4) -> list[Document]:
        """Return the top-k most relevant documents for a query."""
        if self._store is None:
            logger.warning("Vector store is empty — returning no results")
            return []

        return self._store.similarity_search(query, k=k)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    @property
    def is_empty(self) -> bool:
        return self._store is None

    @property
    def document_count(self) -> int:
        if self._store is None:
            return 0
        return self._store.index.ntotal

    def _persist(self) -> None:
        """Save the FAISS index to disk."""
        index_path = Path(settings.faiss_index_path)
        index_path.mkdir(parents=True, exist_ok=True)
        self._store.save_local(str(index_path))
        logger.info(f"FAISS index persisted to {index_path}")
