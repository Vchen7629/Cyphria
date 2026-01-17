
from datetime import timezone
from datetime import timedelta
from datetime import datetime
from pathlib import Path
from pydantic import field_validator
from pydantic_settings import BaseSettings

PROJECT_ROOT = Path(__file__).parent.parent.parent
ENV_FILE = PROJECT_ROOT / ".env"

class Settings(BaseSettings):

    PRODUCTION_MODE: bool = True

    # Airflow settings
    SEND_LOGS: bool = True
    MAX_ACTIVE_RUNS: int = 1 # Run only one at a time to prevent overlapping runs of same dag
    DATA_INGESTION_SVC_PORT: int = 8000
    SENTIMENT_ANALYSIS_SVC_PORT: int = 8000
    LLM_SUMMARY_SVC_PORT: int = 8000
    RANKING_SVC_PORT: int = 8000

    # Dag settings
    START_DATE: datetime = datetime(2024, 1, 1, 0, 0, tzinfo=timezone.utc)

    # Error handling Settings
    NUM_RETRIES: int = 2
    RETRY_DELAY: timedelta = timedelta(minutes=5)
    MAX_RETRY_DELAY: timedelta = timedelta(minutes=30)
    EXECUTION_TIMEOUT: timedelta = timedelta(hours=1) # Kill pod if running more than 1 hour

    @field_validator("EXECUTION_TIMEOUT", "RETRY_DELAY", "MAX_RETRY_DELAY", mode="before")
    @classmethod
    def parse_timedelta(cls, v: str | int | float | timedelta) -> timedelta:
        """Parse duration strings like '60s', '5m', '1h', '2d' into timedelta."""
        if isinstance(v, timedelta):
            return v
        if isinstance(v, (int, float)):
            return timedelta(seconds=v)
        if isinstance(v, str):
            v = v.strip().lower()
            if not v:
                raise ValueError("Empty duration string")
            unit = v[-1]
            try:
                value = float(v[:-1])
            except ValueError:
                raise ValueError(f"Invalid duration format: {v}")
            match unit:
                case "s":
                    return timedelta(seconds=value)
                case "m":
                    return timedelta(minutes=value)
                case "h":
                    return timedelta(hours=value)
                case "d":
                    return timedelta(days=value)
                case _:
                    raise ValueError(f"Unknown time unit '{unit}'. Use s, m, h, or d")
        raise ValueError(f"Cannot parse {type(v).__name__} as timedelta")

settings = Settings()