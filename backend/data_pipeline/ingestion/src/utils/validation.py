from src.core.logger import StructuredLogger
from fastapi import HTTPException
from typing import Optional


def validate_string(
    value: Optional[str],
    field_name: str,
    logger: Optional[StructuredLogger] = None,
    raise_http: bool = False,
    log_error: bool = False,
    raise_on_error: bool = True,
    status_code: int = 400,
) -> bool:
    """
    Validate that a string is not None, empty or whitespace-only

    Args:
        value: the string value to validate
        field_name: Name of the field for error message
        logger: Optional logger for error logging
        raise_http: raises HTTPException if true and raise_on_error is true
        log_error: logs error if true and logger is provided
        raise_on_error: if False, returns False instead of raising exceptions
        status_code: http status code which is only used if raise_http is true

    Returns:
        True if validation passes, False if validation fails and raise_on_error is False
    """
    if not value or not value.strip():
        error_msg = f"Missing {field_name}"
        if log_error and logger:
            logger.error(event_type="ingestion_service run", message=error_msg)
        if raise_on_error:
            if raise_http:
                raise HTTPException(status_code, error_msg)
            raise ValueError(error_msg)

        return False

    return True


def validate_list(
    value: Optional[list[str]],
    field_name: str,
    logger: Optional[StructuredLogger] = None,
    raise_http: bool = False,
    log_error: bool = False,
    raise_on_error: bool = True,
    status_code: int = 400,
) -> bool:
    """
    Validate that a list is not None or empty

    Args:
        value: the list to validate
        field_name: Name of the field for error message
        logger: Optional logger for error logging
        raise_http: raises HTTPException if true and raise_on_error is true
        log_error: logs error if true and logger is provided
        raise_on_error: if False, returns False instead of raising exceptions
        status_code: http status code which is only used if raise_http is true

    Returns:
        True if validation passes, False if validation fails and raise_on_error is False
    """
    if not value:
        error_msg = f"Missing {field_name}"
        if log_error and logger:
            logger.error(event_type="ingestion_service run", message=error_msg)
        if raise_on_error:
            if raise_http:
                raise HTTPException(status_code, error_msg)
            raise ValueError(error_msg)

        return False

    return True

