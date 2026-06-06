"""
Config module for the ReviewLens API.
Loads environment variables using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    # App environment (development/production)
    APP_ENV: str = "development"
    
    # API settings
    API_VERSION: str = "v1"
    
    # Database configuration (defaults to a local async SQLite database if not provided)
    DATABASE_URL: str = "sqlite+aiosqlite:///./reviewlens.db"
    
    # CORS settings: accepts a comma-separated list and parses it to a Python list
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    @property
    def cors_origins(self) -> List[str]:
        # Split allowed origins string by comma and remove spaces
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]

    # Read from a .env file located in the root of the backend directory
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

# Instantiate a settings singleton to import across the app
settings = Settings()
