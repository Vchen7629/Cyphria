from functools import wraps
from typing import Any, Callable, TypeVar, Optional, Coroutine
from sqlalchemy.exc import OperationalError, DBAPIError, InterfaceError
from src.core.logger import StructuredLogger
import asyncio

ReturnType = TypeVar('ReturnType')

# Transient errors that are safe to retry
RETRYABLE_ERRORS = (
    OperationalError,  # Connection issues, timeouts
    InterfaceError # Connection interface errors
)

# PostgreSQL error codes for transient failures
RETRYABLE_PG_CODES = {
    "40001",  # serialization_failure                                                                   
    "40P01",  # deadlock_detected                                                                       
    "57P01",  # admin_shutdown                                                                          
    "57P02",  # crash_shutdown                                                                          
    "08000",  # connection_exception                                                                    
    "08003",  # connection_does_not_exist                                                               
    "08006",  # connection_failure 
}

def is_retryable_error(exc: Exception) -> bool:
    """Check if an exception is retryable"""
    if isinstance(exc, RETRYABLE_ERRORS):
        return True
    
    if isinstance(exc, DBAPIError):
        orig = exc.orig
        if orig is not None and hasattr(orig, "sqlstate"):
            return orig.sqlstate in RETRYABLE_PG_CODES

    return False


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_multiplier: float = 2.0,
    logger: Optional[StructuredLogger] = None,
) -> Callable[[Callable[..., Coroutine[Any, Any, ReturnType]]], Callable[..., Coroutine[Any, Any, ReturnType]]]:
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
    def decorator(
        func: Callable[..., Coroutine[Any, Any, ReturnType]]
    ) -> Callable[..., Coroutine[Any, Any, ReturnType]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            delay = initial_delay

            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if is_retryable_error(e):
                        if attempt == max_retries:
                            if logger:
                                logger.error(
                                    event_type="Database Retry",
                                    message=f"{func.__name__} failed after {max_retries} retries",
                                    error=str(e),
                                    error_type=type(e).__name__,
                                )
                            raise
                        if logger:
                            logger.error(
                                event_type="Database Retry",
                                message=f"{func.__name__} attempt {attempt + 1} failed, retrying in {delay}s",
                                error=str(e),
                                error_type=type(e).__name__,
                            )
                            await asyncio.sleep(delay)
                            delay = min(delay * backoff_multiplier, max_delay)
                    else:
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