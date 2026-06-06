"""
Config module for the ReviewLens API.
Loads environment variables using Pydantic Settings.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App environment
    APP_ENV: str = "development"

    # API version
    API_VERSION: str = "v1"

    # Database URL — defaults to local SQLite
    DATABASE_URL: str = "sqlite+aiosqlite:///./reviewlens.db"

    # CORS — comma-separated list of allowed frontend origins
    # In Render: set ALLOWED_ORIGINS=https://your-app.vercel.app
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,   # ensures ALLOWED_ORIGINS matches allowed_origins etc.
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated origins into a list."""
        origins = [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]
        return origins


settings = Settings()
