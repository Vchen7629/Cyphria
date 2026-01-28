from unittest.mock import patch
from psycopg_pool.pool import ConnectionPool
from src.summary_service import LLMSummaryService


def test_cancel_flag_stops_fetch_top_comments(
    db_pool: ConnectionPool, create_summary_service: LLMSummaryService
) -> None:
    """Cancel flag should cause fetch top comments db call to not go through"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(10):
                cursor.execute(
                    """
                    INSERT INTO product_sentiment (
                        comment_id, product_name, category, sentiment_score, created_utc
                    ) VALUES (
                        %s, %s, 'computing', 10, NOW()
                    )
                """,
                    (f"c{i}", f"product_{i}"),
                )

    service = create_summary_service

    with patch("src.summary_service.fetch_top_comments_for_product") as mock_fetch_comments:
        mock_fetch_comments.return_value = ["comment1", "comment2"]

        service.cancel_requested = True

        service._run_summary_pipeline()

        mock_fetch_comments.assert_not_called()


def test_cancel_flag_stops_generate_summary(
    db_pool: ConnectionPool, create_summary_service: LLMSummaryService
) -> None:
    """Cancel flag should cause generate summary llm call to not go through"""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            for i in range(100):
                cursor.execute(
                    """
                    INSERT INTO raw_comments (
                        comment_id, post_id, comment_body, detected_products, subreddit,
                        author, score, created_utc, category, sentiment_processed
                    ) VALUES (
                        %s, 'p1', 'Test comment', ARRAY['product1'],
                        'test_sub', 'test_author', 10, NOW(), 'GPU', FALSE
                    )
                """,
                    (f"c{i}",),
                )

    service = create_summary_service

    with patch.object(service, "_generate_summary") as mock_generate_summary:
        mock_generate_summary.return_value = "placeholder"

        service.cancel_requested = True

        service._run_summary_pipeline()

        mock_generate_summary.assert_not_called()


def test_no_posts_returns_zero_counts(create_summary_service: LLMSummaryService) -> None:
    """Worker should return 0 for all counts when there are 0 posts to process"""
    service = create_summary_service

    with patch.object(service, "_fetch_products_with_comments", return_value=[]):
        result = service._run_summary_pipeline()

    assert result.products_summarized == 0
    assert result.cancelled is False


def test_cancel_flag_stops_product_list_loop(
    create_summary_service: LLMSummaryService,
) -> None:
    """cancel_requested flag should stop worker at product_list iteration loop"""
    service = create_summary_service

    with patch.object(service, "_generate_summary") as mock_generate_summary:
        service.cancel_requested = True

        result = service._run_summary_pipeline()

        mock_generate_summary.assert_not_called()
        assert result.products_summarized == 0
