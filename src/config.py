"""
Configuration management for the application.
"""
import os
from typing import Any, Dict, Optional

from pydantic import BaseSettings, PostgresDsn, validator


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        PROJECT_NAME: Name of the application
        ENVIRONMENT: Current environment (development, testing, production)
        DEBUG: Debug mode flag
        DATABASE_URL: Database connection string
        SECRET_KEY: Secret key for JWT token generation
        ACCESS_TOKEN_EXPIRE_MINUTES: Token expiration time in minutes
        CORS_ORIGINS: List of allowed CORS origins
    """
    PROJECT_NAME: str = "PurchaseTracker"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./purchase_tracker.db"
    DATABASE_CONNECT_DICT: Dict[str, Any] = {"check_same_thread": False}
    
    @validator("DATABASE_CONNECT_DICT", pre=True)
    def validate_db_connect(cls, v: Optional[Dict[str, Any]], values: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate database connection parameters based on database URL.
        
        Args:
            v: Connection dictionary
            values: Other setting values
        
        Returns:
            Dict[str, Any]: Connection parameters
        """
        if values.get("DATABASE_URL", "").startswith("sqlite"):
            return {"check_same_thread": False}
        return {}
    
    # Security settings
    SECRET_KEY: str = "REPLACE_THIS_WITH_A_SECURE_SECRET_KEY"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS settings
    CORS_ORIGINS: list[str] = ["*"]
    
    class Config:
        """Settings configuration."""
        env_file = ".env"
        case_sensitive = True


# Create global settings object
settings = Settings()

# Export settings
__all__ = ["settings"]
