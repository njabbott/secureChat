"""Configuration management for Chat Magic"""

from pydantic_settings import BaseSettings
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

    # ChromaDB
    chroma_persist_dir: str = "./data/chroma"
    chroma_collection_name: str = "confluence_documents"

    # Indexing
    indexing_schedule_hours: int = 24
    chunk_size: int = 1000
    chunk_overlap: int = 200

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
