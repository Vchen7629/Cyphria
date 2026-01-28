from unittest.mock import MagicMock
from src.db.queries import upsert_llm_summaries
import pytest

@pytest.mark.parametrize(argnames="product_name,tldr,time_window,model_used", argvalues=[
    # empty input params
    ("", "tldr", "90d", "chatgpt"),
    ("product", "", "90d", "chatgpt"),
    ("product", "tldr", "", "chatgpt"),
    ("product", "tldr", "90d", ""),
    # none input params
    (None, "tldr", "90d", "chatgpt"),
    ("product", None, "90d", "chatgpt"),
    ("product", "tldr", None, "chatgpt"),
    ("product", "tldr", "90d", None)
])
def test_invalid_input_params(
    product_name: str | None,
    tldr: str | None,
    time_window: str | None,
    model_used: str | None,
    mock_db_connection: MagicMock
) -> None:
    """Invalid input parameters (none or empty) should return false"""
    empty_product_name = upsert_llm_summaries(mock_db_connection, product_name, tldr, time_window, model_used) # type: ignore

    assert not empty_product_name
