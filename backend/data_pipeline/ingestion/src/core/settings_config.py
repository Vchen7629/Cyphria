from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """All of the worker settings live here"""

    production_mode: bool = False
    fastapi_port: int = 8000

    # --- DB Settings --- 
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "cyphria"
    db_user: str = "postgres"
    db_pass: str = ''

    # --- Reddit Client ---
    Reddit_Api_Client_ID: str
    Reddit_Api_Client_Secret: str
    Reddit_Account_Username: str
    Reddit_Account_Password: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if not production_mode else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()