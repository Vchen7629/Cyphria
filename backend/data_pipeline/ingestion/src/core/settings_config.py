from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """All of the worker settings live here"""

    PRODUCTION_MODE: bool = False
    FASTAPI_PORT: int = 8000

    # --- DB Settings ---
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cyphria"
    DB_USER: str = "postgres"
    DB_PASS: str = ""

    # --- Reddit Client ---
    REDDIT_API_CLIENT_ID: str
    REDDIT_API_CLIENT_SECRET: str
    REDDIT_ACCOUNT_USERNAME: str
    REDDIT_ACCOUNT_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if not PRODUCTION_MODE else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
