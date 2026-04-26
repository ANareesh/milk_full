"""Application configuration settings."""
from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional

# Delivery Services
allowed_cities: list = [
    "Bangalore",
    "Chandigarh", 
    "Chennai",
    "Delhi NCR",
    "Hyderabad",
    "Jaipur",
    "Mumbai",
    "Pune",
    "Coimbatore",
    "Guntur",
    "Kolkata",
    "Lucknow",
    "Mysore",
    "Nashik",
    "Surat",
    "Vijayawada",
    "Warangal"
]

class Settings(BaseSettings):
    """Application settings."""

    # Project
    project_name: str = "ASN Dairy Farm API"
    project_version: str = "1.0.0"
    api_v1_str: str = "/api/v1"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/asn_dairy_farm"
    sqlalchemy_echo: bool = True
    # Optional individual Postgres settings (may be provided in .env)
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "asn_dairy_farm"
    postgres_user: str = "postgres"
    postgres_password: str = "password"
    
    # Security
    secret_key: str = "your-super-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    algorithm: str = "HS256"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    
    # Payment (Stripe)
    stripe_api_key: Optional[str] = None
    stripe_webhook_secret: Optional[str] = None
    
    # UPI/Payment Methods
    upi_enabled: bool = True
    card_enabled: bool = True
    cash_enabled: bool = True
    
    # Email
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    
    # CORS
    cors_origins: list = ["http://localhost:3000", "http://localhost:8000"]
    
    class Config:
        """Pydantic config."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get settings instance."""
    return Settings()
