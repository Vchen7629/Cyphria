from unittest.mock import patch
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


def test_cancel_flag_stops_processing(mock_ranking_service: RankingService) -> None:
    """cancel_requested flag cause the method to return 0"""
    service = mock_ranking_service

    with patch("src.db.queries.fetch_aggregated_product_scores") as mock_fetch_aggregated:
        service.cancel_requested = True

        result = service._calculate_rankings_for_window(product_topic="GPU", time_window="all_time")

        mock_fetch_aggregated.assert_not_called()
        assert result == 0
