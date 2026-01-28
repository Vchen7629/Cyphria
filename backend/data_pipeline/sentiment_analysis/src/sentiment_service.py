from datetime import datetime
from psycopg_pool import ConnectionPool
from src.api.job_state import JobState
from src.api.schemas import SentimentResult
from src.api.schemas import ProductSentiment
from src.core.logger import StructuredLogger
from src.api.schemas import UnprocessedComment
from src.db_utils.queries import mark_comments_processed
from src.db_utils.queries import fetch_unprocessed_comments
from src.db_utils.queries import batch_insert_product_sentiment
from src.preprocessing.extract_pairs import extract_pairs
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis


class SentimentService:
    def __init__(
        self,
        logger: StructuredLogger,
        product_topic: str,
        db_pool: ConnectionPool,
        model: Aspect_Based_Sentiment_Analysis,
    ) -> None:
        self.logger = logger
        self.product_topic = product_topic
        self.db_pool = db_pool
        self.model = model

        # cancellation flag, used to request graceful shutdown
        # This flag is set externally by signal_handler.py when SIGTERM/SIGINT is received
        self.cancel_requested = False

    def _process_sentiment_and_write_to_db(
        self,
        text_product_pairs: list[tuple[str, str]],
        enriched_pairs: list[tuple[str, str, str, str, datetime]],
        comment_ids: set[str],
    ) -> tuple[int, int]:
        """
        Method for taking in a list of tuples (comment_text, product_name) and doing sentiment analysis
        and batch writing to database

        Args:
            text_product_pairs: a list of tuples (comment_text, product_name)
            enriched_pairs: a list of tuples (comment_id, comment_body, product_name, created_utc)
            comment_ids: a set of all unique comment ids that were processed

        Returns:
            tuple containing the number of sentiments_inserted and comments_processed
        """
        product_sentiments: list[ProductSentiment] = []

        sentiment_results = self.model.SentimentAnalysis(text_product_pairs)

        # use zip to preserve comment id ordering
        for (comment_id, _, product_topic, product_name, created_utc), (_, sentiment_score) in zip(
            enriched_pairs, sentiment_results
        ):
            product_sentiments.append(
                ProductSentiment(
                    comment_id=comment_id,
                    product_name=product_name,
                    product_topic=product_topic,
                    sentiment_score=sentiment_score,
                    created_utc=created_utc,
                )
            )

        with self.db_pool.connection() as conn:
            with conn.transaction():
                sentiments_inserted = batch_insert_product_sentiment(conn, product_sentiments)
                comments_processed = mark_comments_processed(conn, list(comment_ids))

        return sentiments_inserted, comments_processed

    def _process_comments(self, comments: list[UnprocessedComment]) -> tuple[int, int]:
        """
        Method for processing comments fetched from the postgres unprocessed_comment table

        Args:
            comments: a list of unprocessed comments

        Returns
            tuple containing the number of sentiments_inserted and comments_processed
        """
        enriched_pairs: list[tuple[str, str, str, str, datetime]] = []
        comment_ids: set[str] = set()

        for comment in comments:
            pairs = extract_pairs(comment)
            enriched_pairs.extend(pairs)
            if pairs:
                comment_ids.add(comment.comment_id)

        if not enriched_pairs:
            return 0, 0

        # absa sentiment analysis only needs text pairs
        text_product_pairs = [
            (comment_text, product_name) for _, comment_text, _, product_name, _ in enriched_pairs
        ]

        sentiments_inserted, comments_processed = self._process_sentiment_and_write_to_db(
            text_product_pairs, enriched_pairs, comment_ids
        )

        return sentiments_inserted, comments_processed

    def _run_sentiment_pipeline(self) -> SentimentResult:
        """
        Main orchestrator method that polls for unprocessed comments for a product_topic and processes them

        Returns
            SentimentResult with counts of posts/comments processed
        """
        self.logger.info(
            event_type="sentiment_analysis worker", message="Starting main worker loop"
        )

        comments_inserted: int = 0
        comments_updated: int = 0

        while not self.cancel_requested:
            with self.db_pool.connection() as conn:
                comments = fetch_unprocessed_comments(conn, self.product_topic, batch_size=200)

            # This stops the service from running once all comments are processed
            if not comments:
                self.logger.info(
                    event_type="sentiment_analysis run",
                    message=f"All comments processed for product_topic {self.product_topic}. Exiting",
                )
                break

            sentiments_inserted, comments_processed = self._process_comments(comments)
            self.logger.info(
                event_type="sentiment_analysis run",
                message=f"Processed batch: {comments_inserted} sentiments inserted, {comments_updated} comments marked processed",
            )

            comments_inserted += sentiments_inserted
            comments_updated += comments_processed

        return SentimentResult(
            comments_inserted=comments_inserted,
            comments_updated=comments_updated,
            cancelled=self.cancel_requested,
        )

    def run_single_cycle(self, job_state: JobState) -> None:
        """
        Run one complete sentiment analysis cycle and update job state
        runs in a background thread and handles all errors internally and updates the job state

        Args:
            job_state: JobState instance to update with progress/results

        Raise:
            Value error if not job state
        """
        # nested import to prevent circular dependency import errors
        from src.api.signal_handler import run_state

        if not job_state:
            raise ValueError("Job state must be provided for the run single cycle")

        try:
            result = self._run_sentiment_pipeline()

            job_state.complete_job(result)

            self.logger.info(
                event_type="sentiment_analysis run",
                message=f"Ranking completed: \
                    {result.comments_inserted} comments inserted, \
                    {result.comments_updated} comments updated",
            )

        except Exception as e:
            self.logger.error(
                event_type="sentiment_analysis run", message=f"Sentiment analysis failed: {str(e)}"
            )
            job_state.fail_job(str(e))
        finally:
            # Clean up run state after job completes or fails
            run_state.run_in_progress = False
            run_state.current_service = None
