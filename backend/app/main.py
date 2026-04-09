"""
FastAPI application entry point.
Configures CORS, lifespan events, and includes all routers.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers.debug import router as debug_router
from app.services.vector_store import VectorStoreService
from app.knowledge.seed_data import seed_knowledge_base

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Global vector store instance (initialised at startup)
# ---------------------------------------------------------------------------
vector_store_service = VectorStoreService()


# ---------------------------------------------------------------------------
# Lifespan — runs on app startup / shutdown
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the FAISS vector store and seed knowledge on startup."""
    logger.info("🚀 Starting AI Debugging Assistant backend …")

    # 1. Initialise FAISS
    vector_store_service.initialize()
    logger.info("✅ FAISS vector store ready")

    # 2. Seed knowledge base if the store is empty
    seed_knowledge_base(vector_store_service)
    logger.info("✅ Knowledge base seeded")

    # Expose the service on app.state so routers can access it
    app.state.vector_store = vector_store_service

    yield  # ← app is running

    logger.info("👋 Shutting down …")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="AI Debugging Assistant",
    description="Submit code + error → get explanation, fix & optimization powered by RAG + Groq LLM.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS — allow the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(debug_router, prefix="/api")
