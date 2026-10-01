import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Pharmacy Management API")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./pharmacy.db")
    jwt_secret: str = os.getenv("JWT_SECRET", "development-only-change-me")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
    cors_origins: tuple[str, ...] = tuple(
        value.strip()
        for value in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
        if value.strip()
    )
    pharmacy_name: str = os.getenv("PHARMACY_NAME", "My Pharmacy")


settings = Settings()

