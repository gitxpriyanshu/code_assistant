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
    """Start up instantly and initialize heavy AI components asynchronously."""
    logger.info("🚀 Web server is online. Initializing AI components in background...")
    
    # Expose the service on app.state
    app.state.vector_store = vector_store_service
    
    # Run heavy initialization in a BACKGROUND task so it doesn't block the port
    import asyncio
    
    async def bg_init():
        try:
            # Run the synchronous seeding in a separate thread so the server stays responsive
            await asyncio.to_thread(seed_knowledge_base, vector_store_service)
            logger.info("✅ AI Background Initialization Complete")
        except Exception as e:
            logger.error(f"❌ Background init failed: {e}")

    asyncio.create_task(bg_init())

    yield
    logger.info("👋 Shutting down …")


# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Code Debugging Assistant",
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
