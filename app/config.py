from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./urlshortener.db"
    redis_url: str | None = None
    base_url: str = "http://127.0.0.1:8000"
    rate_limit_per_minute: int = 60

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
