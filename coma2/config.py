from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///coma2.db"
    debug: bool = True
    mixing_duration_seconds: int = 8


settings = Settings()
