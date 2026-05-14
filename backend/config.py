"""
Configuration management for Bank Anomaly Detection Engine.

Uses Pydantic BaseSettings for environment variable validation and type safety.
All secrets must be provided via environment variables, never hardcoded.
"""

from __future__ import annotations

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    
    Attributes:
        PLAID_CLIENT_ID: Plaid API client identifier
        PLAID_SECRET: Plaid API secret key
        PLAID_ENV: Plaid environment (sandbox, development, production)
        NVIDIA_NIM_API_KEY: NVIDIA NIM API key for LLM access
        DATABASE_PATH: Path to SQLite database file
        ENVIRONMENT: Application environment (development, production)
    """
    
    PLAID_CLIENT_ID: str = Field(..., description="Plaid API client ID")
    PLAID_SECRET: str = Field(..., description="Plaid API secret")
    PLAID_ENV: str = Field(default="sandbox", description="Plaid environment")
    PLAID_ACCESS_TOKEN: str = Field(default="", description="Plaid access token for sandbox")
    NVIDIA_NIM_API_KEY: str = Field(..., description="NVIDIA NIM API key")
    DATABASE_PATH: str = Field(
        default="./anomalies.db",
        description="Path to SQLite database file"
    )
    ENVIRONMENT: str = Field(default="development", description="Application environment")
    
    @field_validator("PLAID_CLIENT_ID", "PLAID_SECRET", "NVIDIA_NIM_API_KEY")
    @classmethod
    def validate_required_secrets(cls, v: str, info) -> str:
        """Validate that critical secrets are not empty."""
        if not v or v.strip() == "":
            raise ValueError(f"{info.field_name} must not be empty")
        return v
    
    @field_validator("PLAID_ENV")
    @classmethod
    def validate_plaid_env(cls, v: str) -> str:
        """Validate Plaid environment is one of the allowed values."""
        allowed = ["sandbox", "development", "production"]
        if v not in allowed:
            raise ValueError(f"PLAID_ENV must be one of {allowed}")
        return v
    
    @field_validator("DATABASE_PATH")
    @classmethod
    def set_production_db_path(cls, v: str, info) -> str:
        """Set database path to /data for production environment."""
        # Access other fields via info.data
        environment = info.data.get("ENVIRONMENT", "development")
        if environment == "production" and v == "./anomalies.db":
            return "/data/anomalies.db"
        return v
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


# Global settings instance
settings = Settings()
