import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    # CRITICAL: Use a read-only user for this connection string!
    DATABASE_URL: str = "postgresql://readonly_user:password@localhost:5432/analytics_db"
    VECTOR_STORE_PATH: str = "./data/chroma_db"

    class Config:
        env_file = ".env"

settings = Settings()