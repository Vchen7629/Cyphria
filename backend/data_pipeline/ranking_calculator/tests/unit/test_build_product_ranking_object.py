from src.api.schemas import SentimentAggregate
from datetime import timezone
from datetime import datetime
from src.ranking_service import RankingService
import pytest
import numpy as np

MOCK_SENTIMENT_AGGREGATE = SentimentAggregate(
    product_name="jaja",
    avg_sentiment=0.23,
    mention_count=2,
    positive_count=2,
    negative_count=0,
    neutral_count=0,
    approval_percentage=100
)

@pytest.mark.parametrize(
    "product_scores,category,time_window,ranks,grades,bayesian_scores,is_top_pick,is_most_discussed,has_limited_data,calculation_date", [
    # None value tests
    (None, "GPU", "all_time", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], None, "all_time", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", None, [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", None, ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], None, [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], None, [False], None, [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], None, [False], None, datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], [False], None, [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], [False], [False], None, datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], [False], [False], [False], None),

    # empty input string tests
    ([MOCK_SENTIMENT_AGGREGATE], "", "all_time", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),

    # empty array
    ([], "GPU", "all_time", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], [], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], [False], [], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "all_time", [1], ["S"], [1], [False], [False], [], datetime.now(tz=timezone.utc)),

    # whitespace strings
    ([MOCK_SENTIMENT_AGGREGATE], "   ", "all_time", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
    ([MOCK_SENTIMENT_AGGREGATE], "GPU", "  ", [1], ["S"], [1], [False], [False], [False], datetime.now(tz=timezone.utc)),
])
def test_invalid_input_params(
    mock_ranking_service: RankingService,
    product_scores: list[SentimentAggregate] | None,
    category: str | None,
    time_window: str | None,
    ranks: np.ndarray | None,
    grades: np.ndarray | None,
    bayesian_scores: np.ndarray | None,
    is_top_pick: np.ndarray | None,
    is_most_discussed: np.ndarray | None,
    has_limited_data: np.ndarray | None,
    calculation_date: datetime | None
) -> None:
    """Invalid (None, empty string, whitespace) input params should return 0"""
    RankingService = mock_ranking_service

    result = RankingService._build_product_ranking_object(
        product_scores=product_scores,      # type: ignore
        category=category,                  # type: ignore
        time_window=time_window,            # type: ignore
        ranks=ranks,                        # type: ignore
        grades=grades,                      # type: ignore
        bayesian_scores=bayesian_scores,    # type: ignore
        is_top_pick=is_top_pick,            # type: ignore
        is_most_discussed=is_most_discussed,# type: ignore
        has_limited_data=has_limited_data,  # type: ignore
        calculation_date=calculation_date   # type: ignore
    )

    assert result == []

def test_cancel_flag_stops_processing(mock_ranking_service: RankingService) -> None:
    """cancel_requested flag cause the method to return 0"""
    service = mock_ranking_service
    service.cancel_requested = True
    
    result = service._build_product_ranking_object(
        product_scores=[MOCK_SENTIMENT_AGGREGATE],
        category="GPU", 
        time_window="all_time",
        ranks=np.array([2]),
        grades=np.array(["S"]),
        bayesian_scores=np.array([0.88]),
        is_top_pick=np.array([True]),
        is_most_discussed=np.array([False]),
        has_limited_data=np.array([False]),
        calculation_date=datetime.now(tz=timezone.utc)
    )

    assert result == []
