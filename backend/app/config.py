"""
Application configuration.
Loads environment variables from .env and exposes them as typed settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    groq_api_key: str = Field(..., description="Groq API key for LLM access")
    model_name: str = Field(
        default="llama-3.3-70b-versatile",
        description="Groq model identifier",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
        description="HuggingFace embedding model name",
    )
    faiss_index_path: str = Field(
        default="./data/faiss_index",
        description="Path to persist the FAISS index",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Singleton instance — import this throughout the app
settings = Settings()
