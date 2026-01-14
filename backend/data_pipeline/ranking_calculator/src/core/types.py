from pydantic import BaseModel
from datetime import date

class SentimentAggregate(BaseModel):
    """Aggregated sentiment data for a single product from product_sentiment table."""

    product_name: str
    avg_sentiment: float
    mention_count: int
    positive_count: int
    negative_count: int
    neutral_count: int


class ProductRanking(BaseModel):
    """Data model for product ranking row to be inserted into gold layer."""
    product_name: str
    category: str
    time_window: str  # "90d" or "all_time"

    # Ranking
    rank: int
    grade: str  # "S", "A+", "A", "A-", "B+", etc.

    # Scores
    bayesian_score: float
    avg_sentiment: float
    approval_percentage: int

    # Metrics
    mention_count: int
    positive_count: int
    negative_count: int
    neutral_count: int

    # Badges
    is_top_pick: bool = False
    is_most_discussed: bool = False
    has_limited_data: bool = False

    # Metadata
    calculation_date: date
