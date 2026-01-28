from unittest.mock import MagicMock
from src.db.queries import fetch_top_comments_for_product


def test_empty_input_paramaters(mock_db_connection: MagicMock) -> None:
    """Empty product name or time window should return an empty array"""
    empty_product_name_res = fetch_top_comments_for_product(
        mock_db_connection, product_name="", time_window="all_time"
    )
    assert len(empty_product_name_res) == 0
    assert empty_product_name_res == []

    empty_time_window_res = fetch_top_comments_for_product(
        mock_db_connection, product_name="rtx 4090", time_window=""
    )
    assert len(empty_time_window_res) == 0
    assert empty_time_window_res == []


def test_none_input_paramaters(mock_db_connection: MagicMock) -> None:
    """None product name or time window should return an empty array"""
    none_product_name_res = fetch_top_comments_for_product(
        mock_db_connection,
        product_name=None,  # type: ignore
        time_window="all_time",
    )
    assert len(none_product_name_res) == 0
    assert none_product_name_res == []

    none_time_window_res = fetch_top_comments_for_product(
        mock_db_connection,
        product_name="rtx 4090",
        time_window=None,  # type: ignore
    )
    assert len(none_time_window_res) == 0
    assert none_time_window_res == []
