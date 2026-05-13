"""
Application configuration via Pydantic Settings.
All environment variables are parsed and validated at startup.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────
    app_name: str = "Saṃśodhakaḥ"
    app_version: str = "0.1.0"
    debug: bool = False

    # ── Server ──────────────────────────────────────────────────
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    log_level: str = "info"
    cors_origins: list[str] = ["*"]

    # ── Paths ───────────────────────────────────────────────────
    base_dir: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = base_dir / "runtime" / "data"
    cache_dir: Path = base_dir / "runtime" / "cache"
    log_dir: Path = base_dir / "runtime" / "logs"

    # ── Storage ────────────────────────────────────────────────
    storage_root: Path = base_dir / "runtime" / "data" / "storage"

    # ── Database (SQLite) ──────────────────────────────────────
    database_url: str = f"sqlite:///{base_dir / 'runtime' / 'data' / 'samsodhakah.db'}"

    # ── LLM Providers ──────────────────────────────────────────
    mistral_api_key: Optional[str] = None
    groq_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None

    # Default LLM model
    llm_model: str = "mistral-small-latest"
    llm_provider: str = "mistral"  # mistral | groq | openai

    # ── Embeddings ────────────────────────────────────────────
    embedding_model: str = "all-MiniLM-L6-v2"  # local sentence-transformers
    embedding_dimension: int = 384

    # ── Retrieval ──────────────────────────────────────────────
    bm25_k1: float = 1.5
    bm25_b: float = 0.75
    retrieval_top_k: int = 20
    reranking_top_k: int = 10

    # ── Verification ──────────────────────────────────────────
    lexical_similarity_threshold: float = 0.7
    semantic_similarity_threshold: float = 0.75
    numerical_tolerance: float = 0.05

    # ── Drafting / Token Economics ────────────────────────────
    max_context_tokens: int = 4096
    max_draft_tokens: int = 2048
    max_sections: int = 8
    compression_target_ratio: float = 0.3  # compress context to 30% of original

    # ── Web Search ────────────────────────────────────────────
    serper_api_key: Optional[str] = None
    duckduckgo_max_results: int = 5

    def ensure_directories(self) -> None:
        """Create all required runtime directories if they don't exist."""
        for directory in [self.data_dir, self.cache_dir, self.log_dir, self.storage_root]:
            directory.mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.ensure_directories()