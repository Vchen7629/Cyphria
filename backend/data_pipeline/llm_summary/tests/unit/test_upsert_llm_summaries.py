from unittest.mock import MagicMock
from src.db.queries import upsert_llm_summaries

def test_empty_input_params(mock_db_connection: MagicMock) -> None:
    """Empty input parameters should return false"""
    empty_product_name = upsert_llm_summaries(mock_db_connection, product_name="", tldr="tldr", time_window="90d", model_used="chatgpt")
    assert empty_product_name == False

    empty_tldr = upsert_llm_summaries(mock_db_connection, product_name="product", tldr="", time_window="90d", model_used="chatgpt")
    assert empty_tldr == False

    empty_time_window = upsert_llm_summaries(mock_db_connection, product_name="product", tldr="tldr", time_window="", model_used="chatgpt")
    assert empty_time_window == False

    empty_model = upsert_llm_summaries(mock_db_connection, product_name="product", tldr="tldr", time_window="90d", model_used="")
    assert empty_model == False

    all_empty = upsert_llm_summaries(mock_db_connection, product_name="", tldr="", time_window="", model_used="")
    assert all_empty == False

def test_none_input_params(mock_db_connection: MagicMock) -> None:
    """Empty input parameters should return false"""
    empty_product_name = upsert_llm_summaries(mock_db_connection, product_name="", tldr="tldr", time_window="90d", model_used="chatgpt")
    assert empty_product_name == False

    empty_tldr = upsert_llm_summaries(mock_db_connection, product_name="product", tldr="", time_window="90d", model_used="chatgpt")
    assert empty_tldr == False

    empty_time_window = upsert_llm_summaries(mock_db_connection, product_name="product", tldr="tldr", time_window="", model_used="chatgpt")
    assert empty_time_window == False

    empty_model = upsert_llm_summaries(mock_db_connection, product_name="product", tldr="tldr", time_window="90d", model_used="")
    assert empty_model == False

    all_empty = upsert_llm_summaries(mock_db_connection, product_name="", tldr="", time_window="", model_used="")
    assert all_empty == False