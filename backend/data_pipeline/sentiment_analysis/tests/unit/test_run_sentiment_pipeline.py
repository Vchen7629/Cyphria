from unittest.mock import patch
from src.sentiment_service import SentimentService


def test_no_comments(mock_sentiment_service: SentimentService) -> None:
    """No comments should break and not invoke the _process_comments method"""
    service = mock_sentiment_service

    with (
        patch("src.sentiment_service.fetch_unprocessed_comments", return_value=[]),
        patch.object(service, "_process_comments") as mock_process_comments,
    ):
        result = service._run_sentiment_pipeline()

        mock_process_comments.assert_not_called()

        assert result.comments_inserted == 0
        assert result.comments_updated == 0


def test_cancel_requested_breaks_while_loop(mock_sentiment_service: SentimentService) -> None:
    """If cancel requested, it should break while loop"""
    service = mock_sentiment_service

    with (
        patch("src.sentiment_service.fetch_unprocessed_comments") as mock_db_call,
        patch.object(service, "_process_comments") as mock_process_comments,
    ):
        service.cancel_requested = True

        result = service._run_sentiment_pipeline()

        mock_process_comments.assert_not_called()
        mock_db_call.assert_not_called()

        assert result.comments_inserted == 0
        assert result.comments_updated == 0
