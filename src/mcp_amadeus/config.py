"""Pydantic Settings configuration for Amadeus MCP server."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Amadeus API configuration.

    Reads from environment variables with AMADEUS_ prefix or .env file.
    """

    client_id: str = Field(default="", description="Amadeus API client ID")
    client_secret: str = Field(default="", description="Amadeus API client secret")
    base_url: str = Field(
        default="https://test.api.amadeus.com",
        description="Amadeus API base URL (test or production)",
    )

    model_config = SettingsConfigDict(
        env_prefix="AMADEUS_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Get configuration from environment variables or .env file."""
    return Settings()
