from src.ranking_service import RankingService
import pytest


@pytest.mark.parametrize(
    "product_topic,time_window",
    [
        (None, "all_time"),  # None value tests
        ("GPU", None),
        ("", "all_time"),  # empty string tests
        ("GPU", ""),
        ("  ", "all_time"),  # whitespace tests
        ("GPU", "  "),
    ],
)
def test_invalid_input_params(
    mock_ranking_service: RankingService, product_topic: str | None, time_window: str | None
) -> None:
    """Invalid (None, empty string, whitespace) input params should return 0"""
    RankingService = mock_ranking_service

    result = RankingService._calculate_rankings_for_window(
        product_topic=product_topic,  # type: ignore
        time_window=time_window,  # type: ignore
    )

    assert result == 0
