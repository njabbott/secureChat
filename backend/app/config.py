"""Configuration management for Chat Magic"""

from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import List
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Application
    app_name: str = "Chat Magic"
    app_version: str = "1.0.0"
    log_level: str = "INFO"

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: str = "http://localhost:4200,http://localhost:8000"

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"

    # Confluence
    confluence_base_url: str
    confluence_email: str
    confluence_org_id: str
    confluence_api_key: str

    # Jira (reuses Confluence credentials — same Atlassian Cloud instance)
    jira_project_key: str

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "confluence_documents"

    # Indexing
    indexing_schedule_hours: int = 24
    chunk_size: int = 1000
    chunk_overlap: int = 200

    # Hybrid search and reranking
    hybrid_search_top_k: int = 20
    rerank_top_n: int = 5

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_chat_requests: int = 30
    rate_limit_chat_window: int = 60  # seconds
    rate_limit_indexing_requests: int = 5
    rate_limit_indexing_window: int = 3600  # seconds (1 hour)
    rate_limit_cleanup_interval: int = 300  # 5 minutes

    @field_validator('rate_limit_chat_requests', 'rate_limit_indexing_requests')
    @classmethod
    def validate_request_limits(cls, v: int, info) -> int:
        """Validate rate limit request counts are positive and reasonable"""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be positive, got {v}")
        if v > 10000:
            raise ValueError(f"{info.field_name} seems unreasonably high ({v}), max allowed is 10000")
        return v

    @field_validator('rate_limit_chat_window', 'rate_limit_indexing_window', 'rate_limit_cleanup_interval')
    @classmethod
    def validate_time_windows(cls, v: int, info) -> int:
        """Validate rate limit time windows are positive and reasonable"""
        if v <= 0:
            raise ValueError(f"{info.field_name} must be positive, got {v}")
        if v > 86400:  # 24 hours
            raise ValueError(f"{info.field_name} seems unreasonably high ({v}s), max allowed is 86400s (24 hours)")
        return v

    @property
    def cors_origins_list(self) -> List[str]:
        """Convert CORS origins string to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        # Look for .env file in project root (two levels up from this file)
        env_file = Path(__file__).parent.parent.parent / ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
