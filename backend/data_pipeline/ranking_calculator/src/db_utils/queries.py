import psycopg
from psycopg.rows import dict_row
from src.core.types import SentimentAggregate, ProductRanking
from src.core.logger import StructuredLogger
from src.db_utils.retry import retry_with_backoff

structured_logger = StructuredLogger(pod="idk")

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def fetch_aggregated_product_scores(conn: psycopg.Connection, category: str, time_window: str) -> list[SentimentAggregate]:
    """
    Fetch a aggregated sentiment scores per product for a category and time window.
    Joins product sentiment with raw comments to filter by category

    Args:
        conn: psycopg3 database connection
        category: the product category to filter by, like 'GPU' or 'Laptop'
        time_window: 90d or all_time

    Returns:
        list of SentimentAggregate with:
            - product_name: name of the product
            - avg_sentiment: the avg sentiment score of the product
            - mention_count: the amount of comments mentioning the product
            - positive_count: the amount of comments where the sentiment is positive (> 0.2)
            - negative_count: the amount of comments where the sentiment is negative (< -0.2)
            - neutral_count: the amount of comments where the sentiment is neutral (-0.2 < sentiment < 0.2)
    """
    normalized_time_window: str = time_window.lower().strip()
    normalized_category: str = category.strip().upper()

    if not normalized_time_window:
        return []

    if not normalized_category:
        return []

    if normalized_time_window == "all_time":
        query = """
            SELECT
                product_name,
                AVG(sentiment_score) AS avg_sentiment,
                COUNT(*) AS mention_count,
                COUNT(*) FILTER (WHERE sentiment_score > 0.2) AS positive_count,
                COUNT(*) FILTER (WHERE sentiment_score < -0.2) AS negative_count,
                COUNT(*) FILTER (WHERE sentiment_score BETWEEN -0.2 AND 0.2) AS neutral_count
            FROM product_sentiment
            WHERE category = %(category)s
            GROUP BY product_name
            HAVING COUNT(*) >= 1
            ORDER BY AVG(sentiment_score) DESC
        """
        params = {"category": normalized_category}
    else:
        query = """
            SELECT
                product_name,
                AVG(sentiment_score) AS avg_sentiment,
                COUNT(*) AS mention_count,
                COUNT(*) FILTER (WHERE sentiment_score > 0.2) AS positive_count,
                COUNT(*) FILTER (WHERE sentiment_score < -0.2) AS negative_count,
                COUNT(*) FILTER (WHERE sentiment_score BETWEEN -0.2 AND 0.2) AS neutral_count
            FROM product_sentiment
            WHERE category = %(category)s
              AND created_utc >= NOW() - %(time_window)s::INTERVAL
            GROUP BY product_name
            HAVING COUNT(*) >= 1
            ORDER BY AVG(sentiment_score) DESC
        """
        params = {"category": normalized_category, "time_window": time_window}

    with conn.cursor(row_factory=dict_row) as cursor:
        cursor.execute(query, params)
        results = cursor.fetchall()

    return [SentimentAggregate.model_validate(row) for row in results]

@retry_with_backoff(max_retries=3, initial_delay=1.0, logger=structured_logger)
def batch_upsert_product_score(conn: psycopg.Connection, sentiments: list[ProductRanking]) -> None:
    """
    Batch upsert multiple processed product scores to the product rankings table (gold layer).

    Args:
        conn: psycopg3 database connection
        sentiments: list of product scores calculated using baysian estimate formula:
            - product_name: name of the product
            - category: the category of the product
            - time_window: time window its calculated from, either 90d or all_time
            - rank: the ranking score 
            - grade: grade of the product, S, A+, A, A-, B+, etc
            - baysian_score: the number calculated using bayesian estimate formula
            - avg_sentiment: avg sentiment score of the product
            - approval percentage: amount of positive comments in the total mentions
            - mention_count: amount of comments where the product is mentioned
            - positive_count: the amount of co comments where the sentiment is positive (> 0.2)
            - negative_count: the amount of comments where the sentiment is negative (< -0.2)
            - neutral_count: the amount of comments where the sentiment is neutral (-0.2 < sentiment < 0.2)
            - is_top_pick: boolean marking the product as the highest ranked
            - is_most_discussed: boolean marking the product as having the most mentions
            - has_limited_data: boolean marking the product having less than a threshold amount of mentions
            - calculation_date: the utc timestamp when the product was last calculated ranking for
    """
    if not sentiments:
        return None

    query = """
        INSERT INTO product_rankings (
            product_name, category, time_window, rank, grade, bayesian_score, avg_sentiment, approval_percentage, mention_count,
            positive_count, negative_count, neutral_count, is_top_pick, is_most_discussed, has_limited_data, calculation_date
        ) VALUES (
            %(product_name)s, %(category)s, %(time_window)s, %(rank)s, %(grade)s, %(bayesian_score)s, %(avg_sentiment)s, %(approval_percentage)s, %(mention_count)s,
            %(positive_count)s, %(negative_count)s, %(neutral_count)s, %(is_top_pick)s, %(is_most_discussed)s, %(has_limited_data)s, %(calculation_date)s
        )
        ON CONFLICT (product_name, time_window) 
        DO UPDATE SET
            rank = EXCLUDED.rank,
            grade = EXCLUDED.grade,
            bayesian_score = EXCLUDED.bayesian_score,
            avg_sentiment = EXCLUDED.avg_sentiment,
            approval_percentage = EXCLUDED.approval_percentage,
            mention_count = EXCLUDED.mention_count,
            positive_count = EXCLUDED.positive_count,
            negative_count = EXCLUDED.negative_count,
            neutral_count = EXCLUDED.neutral_count,
            is_top_pick = EXCLUDED.is_top_pick,
            is_most_discussed = EXCLUDED.is_most_discussed,
            has_limited_data = EXCLUDED.has_limited_data,
            calculation_date = EXCLUDED.calculation_date;
    """

    with conn.cursor() as cursor:
        cursor.executemany(query, [s.model_dump() for s in sentiments])