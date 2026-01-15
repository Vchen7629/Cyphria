from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """All of the worker settings live here"""

    production_mode: bool = False

    # --- Injected variables by airflow ---
    product_category: str

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

    @field_validator('product_category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """
        Validate and normalize the product_category field.
        Converts to uppercase and checks against allowed categories.
        Raises ValueError if invalid, causing the worker to crash on startup
        so Airflow can detect the failure and retry.
        """
        ALLOWED_CATEGORIES = {"GPU", "LAPTOP", "HEADPHONE"}

        normalized = v.upper().strip()

        if normalized not in ALLOWED_CATEGORIES:
            raise ValueError(
                f"Invalid category: {v}. Allowed categories: {', '.join(sorted(ALLOWED_CATEGORIES))}"
            )

        return normalized

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE) if not production_mode else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()