from unittest.mock import MagicMock
from src.db.queries import fetch_unique_products


def test_empty_input_paramaters(mock_db_connection: MagicMock) -> None:
    """Empty product name or time window should return an empty array"""
    empty_input = fetch_unique_products(mock_db_connection, time_window="")
    assert len(empty_input) == 0
    assert empty_input == []


def test_none_input_paramaters(mock_db_connection: MagicMock) -> None:
    """None product name or time window should return an empty array"""
    none_input = fetch_unique_products(mock_db_connection, time_window=None)  # type: ignore
    assert len(none_input) == 0
    assert none_input == []
