from unittest.mock import patch
from src.ranking_service import RankingService


def test_no_products_returns_zero_counts(create_ranking_service: RankingService) -> None:
    """Worker should return 0 for products_copunt when there are 0 products to process"""
    service = create_ranking_service

    with patch.object(service, "_calculate_rankings_for_window", return_value=0):
        result = service._run_ranking_pipeline()

    assert result.products_processed == 0
    assert result.cancelled is False
