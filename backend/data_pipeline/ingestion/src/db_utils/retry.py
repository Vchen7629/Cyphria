import time
from functools import wraps
from typing import Any, Callable, TypeVar, Optional
import psycopg

from src.core.logger import StructuredLogger

ReturnType = TypeVar('ReturnType')

# Transient errors that are safe to retry
RETRYABLE_ERRORS = (
    psycopg.OperationalError,  # Connection issues, timeouts
    psycopg.errors.DeadlockDetected,
    psycopg.errors.SerializationFailure,
    psycopg.errors.AdminShutdown,
    psycopg.errors.CrashShutdown,
)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_multiplier: float = 2.0,
    logger: Optional[StructuredLogger] = None,
) -> Callable[[Callable[..., ReturnType]], Callable[..., ReturnType]]:
    """
    Decorator that retries a function with exponential backoff on transient database errors.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay in seconds between retries (default: 30.0)
        backoff_multiplier: Multiplier for exponential backoff (default: 2.0)
        logger: Optional StructuredLogger instance for logging failures

    Example:
        @retry_with_backoff(max_retries=3, initial_delay=1.0, logger=my_logger)
        def my_db_operation(conn, data):
            # Database operation that might fail transiently
            pass
    """
    def decorator(func: Callable[..., ReturnType]) -> Callable[..., ReturnType]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> ReturnType:
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except RETRYABLE_ERRORS as e:
                    if attempt == max_retries:
                        # Final failure - log it
                        if logger:
                            logger.error(
                                event_type="Database Retry",
                                message=f"{func.__name__} failed after {max_retries} retries",
                                error=str(e),
                                error_type=type(e).__name__,
                            )
                        raise

                    # Retry with exponential backoff
                    time.sleep(delay)
                    delay = min(delay * backoff_multiplier, max_delay)
                except Exception as e:
                    # Non-retryable error - fail immediately
                    if logger:
                        logger.error(
                            event_type="Database Error",
                            message=f"{func.__name__} failed with non-retryable error",
                            error=str(e),
                            error_type=type(e).__name__,
                        )
                    raise

        return wrapper
    return decorator