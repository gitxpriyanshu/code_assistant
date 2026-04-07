"""
Knowledge base seeder.
Reads .txt files from data/knowledge_base/ and ingests them into the FAISS vector store.
Each file is split into chunks for better retrieval granularity.
"""

import logging
from pathlib import Path

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)

KNOWLEDGE_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "knowledge_base"

# Splitter: chunks of ~500 chars with 50-char overlap for context continuity
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def seed_knowledge_base(vector_store: VectorStoreService) -> None:
    """Load all .txt files from the knowledge directory and ingest them."""

    if not vector_store.is_empty:
        logger.info(
            f"Vector store already contains {vector_store.document_count} vectors — skipping seed"
        )
        return

    if not KNOWLEDGE_DIR.exists():
        logger.warning(f"Knowledge directory not found: {KNOWLEDGE_DIR}")
        return

    txt_files = list(KNOWLEDGE_DIR.glob("*.txt"))
    if not txt_files:
        logger.warning("No .txt files found in knowledge directory")
        return

    all_documents: list[Document] = []

    for filepath in txt_files:
        logger.info(f"Processing {filepath.name} …")
        raw_text = filepath.read_text(encoding="utf-8")

        # Split into chunks
        chunks = text_splitter.split_text(raw_text)

        for i, chunk in enumerate(chunks):
            doc = Document(
                page_content=chunk,
                metadata={
                    "source": filepath.name,
                    "chunk_index": i,
                },
            )
            all_documents.append(doc)

    logger.info(f"Prepared {len(all_documents)} chunks from {len(txt_files)} files")

    # Ingest into FAISS
    vector_store.add_documents(all_documents)
    logger.info("✅ Knowledge base seeding complete")
