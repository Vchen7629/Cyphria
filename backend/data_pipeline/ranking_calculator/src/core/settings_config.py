from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import numpy as np

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):
    """All of the worker configs live here"""

    PRODUCTION_MODE: bool = False
    GRADE_THRESHOLDS: np.ndarray = np.array([0.95, 0.9, 0.85, 0.75, 0.7, 0.45, 0.1, -0.1, -0.3, -0.5])
    GRADE_VALUES: np.ndarray = np.array(["S", "A", "A-", "B-", "B", "C", "C-", "D", "D-", "F", "F-"])
    
    # --- Injected params by airflow ---
    FASTAPI_PORT: int = 8000    
    BAYESIAN_PARAMS: int # optional, minimum mentions threshold

    # --- DB Settings --- 
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "cyphria"
    DB_USER: str = "postgres"
    DB_PASS: str = ''

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
        env_file=str(ENV_FILE) if not PRODUCTION_MODE else None,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()