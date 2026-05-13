"""
Configuration settings for Saṃśodhakaḥ system.
"""

from __future__ import annotations
from pathlib import Path
from typing import Optional
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Data directory
    data_dir: Path = Field(default=Path("runtime/data"), env="DATA_DIR")

    # Ingestion settings
    max_sections: int = 50
    max_draft_tokens: int = 4096

    # Mistral API settings
    mistral_api_url: str = Field(default="https://api.mistral.ai/v1", env="MISTRAL_API_URL")
    mistral_api_key: str = Field(default="", env="MISTRAL_API_KEY")
    mistral_model: str = Field(default="mistral-tiny", env="MISTRAL_MODEL")
    mistral_max_tokens: int = Field(default=1024, env="MISTRAL_MAX_TOKENS")
    mistral_temperature: float = Field(default=0.7, env="MISTRAL_TEMPERATURE")
    mistral_timeout: int = Field(default=30, env="MISTRAL_TIMEOUT")
    mistral_max_retries: int = Field(default=3, env="MISTRAL_MAX_RETRIES")

    # Embedding settings
    embedding_model: str = Field(default="all-MiniLM-L6-v2", env="EMBEDDING_MODEL")

    # Retrieval settings
    bm25_k1: float = 1.5
    bm25_b: float = 0.75

    # Compression settings
    compression_target_ratio: float = 0.3

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()