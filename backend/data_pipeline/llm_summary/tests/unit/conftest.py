import pytest
from unittest.mock import MagicMock
from typing import Generator

@pytest.fixture
def mock_cursor() -> MagicMock:
    """Mock database cursor for unit tests."""
    cursor = MagicMock()
    cursor.fetchall.return_value = [] # type: ignore
    cursor.fetchone.return_value = None
    cursor.execute.return_value = None
    cursor.__enter__.return_value = cursor
    cursor.__exit__.return_value = None
    return cursor

@pytest.fixture
def mock_db_connection(mock_cursor: MagicMock) -> Generator[MagicMock, None, None]:
    """Mock database connection"""
    conn = MagicMock()
    conn.cursor.return_value = mock_cursor
    conn.commit.return_value = None
    conn.rollback.return_value = None
    conn.close.return_value = None
    conn.closed = False

    yield conn

