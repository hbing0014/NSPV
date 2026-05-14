from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "NSPV API"
    database_url: str = "sqlite:///./nspv.db"
    frontend_origin: str = "http://localhost:3000"
    scraper_provider: str = "mock"
    jwt_secret_key: str = "dev-only-change-me"
    jwt_access_token_expire_minutes: int = 60 * 24

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
