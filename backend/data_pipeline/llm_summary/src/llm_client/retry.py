from functools import wraps
from typing import Any
from typing import TypeVar
from typing import Callable
from typing import Optional
from openai import APIError
from openai import RateLimitError
from openai import APITimeoutError
from shared_core.logger import StructuredLogger
from src.core.settings_config import settings
import time

ReturnType = TypeVar("ReturnType")


def exponential_backoff(
    name: str, attempt: int, error: Any, error_type: str, logger: Optional[StructuredLogger] = None
) -> None:
    """
    Helper method for exponential backoff logic

    Args:
        name: name of the function the wrapper wraps
        attempt: current retry attempt number
        error: the retry error
        error_type: type of error, either Rate limit, API timeout, or API Error
        logger: optional Structured logger instance
    """
    if attempt == settings.LLM_MAX_RETRIES - 1:
        if logger:
            logger.error(
                event_type="llm_summary api call",
                message=f"{name} failed after {settings.LLM_MAX_RETRIES} retries, {error_type}: {error}",
            )
        raise
    wait_time = 2**attempt  # 1s, 2s, 4s
    if logger:
        logger.warning(
            event_type="llm summary api call",
            message=f"{error_type}, retrying in {wait_time}s (attempt {attempt + 1}/{settings.LLM_MAX_RETRIES})",
        )
    time.sleep(wait_time)


def retry_llm_api(
    logger: Optional[StructuredLogger] = None,
) -> Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]:
    """
    Decorator that retries LLM Api calls with exponential backoff on transient errors

    Args:
        logger: Structured logger instance

    Example:
        @retry_llm_api(logger=my_logger)
        def _generate_summary(self, product_name: str, comments: list[str]) -> str:
            pass
    """

    def decorator(func: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(settings.LLM_MAX_RETRIES):
                try:
                    return func(*args, **kwargs)

                except RateLimitError as e:
                    exponential_backoff(func.__name__, attempt, e, "Rate Limit", logger)
                except APITimeoutError as e:
                    exponential_backoff(func.__name__, attempt, e, "API Timeout", logger)

                except APIError as e:
                    exponential_backoff(func.__name__, attempt, e, "API error", logger)

                except Exception as e:
                    if logger:
                        logger.error(
                            event_type="llm_summary api call",
                            message=f"{func.__name__} failed with non retryable error: {e}",
                        )
                    raise

        return wrapper

    return decorator
