"""
Application configuration.
Loads environment variables from .env and exposes them as typed settings.
"""

from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Central configuration loaded from environment variables."""

    groq_api_key: str = Field(
        default="",
        alias="GROQ_API_KEY",
        validation_alias="GROQ_API_KEY",
    )
    model_name: str = Field(
        default="llama-3.1-8b-instant",
        alias="MODEL_NAME",
    )
    embedding_model: str = Field(
        default="sentence-transformers/all-MiniLM-L6-v2",
    )
    faiss_index_path: str = Field(
        default="./data/faiss_index",
    )
    allow_unsafe_faiss_load: bool = Field(
        default=True,
    )

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


# Singleton instance
settings = Settings()
