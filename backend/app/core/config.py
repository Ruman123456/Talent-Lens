from pydantic_settings import BaseSettings
from typing import Optional, List
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "TalentLens AI"
    API_V1_STR: str = "/api"
    DATABASE_URL: str = "sqlite:///./backend/talentlens.db"
    
    # LLM Settings
    LLM_PROVIDER: str = "demo"  # "gemini", "openai", "demo"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    OPENAI_BASE_URL: Optional[str] = None
    
    # Embedding & Chroma
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    CHROMA_PERSIST_DIRECTORY: str = "./backend/chroma_db"
    
    # Knowledge & Uploads
    UPLOAD_DIRECTORY: str = "./backend/uploads"
    KNOWLEDGE_BASE_DIR: str = "./backend/knowledge_base"
    
    # Chunking
    CHUNK_SIZE: int = 900
    CHUNK_OVERLAP: int = 150
    
    # Retrieval
    RETRIEVAL_TOP_K: int = 4
    SIMILARITY_THRESHOLD: float = 0.35
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:5173", "http://localhost:3000", "*"]

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

