from src.api.schemas import UnprocessedComment
from src.api.schemas import ProductSentiment
from src.core.logger import StructuredLogger
from src.core.model import sentiment_analysis_model
from src.core.settings_config import Settings
from src.preprocessing.sentiment_analysis import Aspect_Based_Sentiment_Analysis
from src.preprocessing.extract_pairs import extract_pairs
from src.db_utils.conn import create_connection_pool
from src.db_utils.queries import (
    fetch_unprocessed_comments,
    batch_insert_product_sentiment,
    mark_comments_processed
)
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import signal

class StartService:
    def __init__(self) -> None:
        self.settings = Settings()
        self.structured_logger = StructuredLogger(pod="sentiment-analysis-worker")
        self.executor = ThreadPoolExecutor(max_workers=1)
        self.sentiment_batch_size: int = 64
        self.shutdown_requested: bool = False

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self._database_conn_lifespan()
        self._initialize_absa_model()

        self.structured_logger.info(event_type="sentiment_analysis startup", message="Worker init complete")

    def _database_conn_lifespan(self) -> None:
        """
        Method for handling database connection lifespan including creating connection pool,
        and checking the health
        """
        self.structured_logger.info(event_type="sentiment_analysis startup", message="Creating database conenction pool")
        self.db_pool = create_connection_pool()

        # Perform health check for db connection on startup
        self.structured_logger.info(event_type="sentiment_analysis startup", message="Checking Database health check...")
        try:
            with self.db_pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                self.structured_logger.info(event_type="sentiment_analysis startup", message="Database health check passed")
        except Exception as e:
            self.structured_logger.error(event_type="sentiment_analysis startup", message=f"Database health check failed: {e}")
            self.db_pool.close()
            raise 
  
    def _initialize_absa_model(self) -> None:
        """Method for initializing the ABSA sentiment analysis model"""
        self.structured_logger.info(event_type="sentiment_analysis startup", message="loading ABSA model")

        model_data = sentiment_analysis_model("yangheng/deberta-v3-base-absa-v1.1")
        tokenizer, model = model_data
        self.ABSA = Aspect_Based_Sentiment_Analysis(tokenizer, model, self.executor, model_batch_size=self.sentiment_batch_size)

    def _signal_handler(self, signum: int, _frame: object) -> None:
        """
        Signal handler for graceful shutdown

        Args:
            signum: Signal number
            _frame: Current stack frame (unused but required by signal handler signature)
        """
        signal_name = signal.Signals(signum).name
        self.structured_logger.info(event_type="sentiment_analysis shutdown", message=f"Received {signal_name} signal, initiating graceful shutdown")
        self.shutdown_requested = True
        
    def _cleanup(self) -> None:
        """Cleanup resources on shutdown"""
        self.structured_logger.info(event_type="sentiment_analysis shutdown", message="Cleaning up resources")

        # Close thread pool executor
        self.executor.shutdown(wait=True)
        self.structured_logger.info(event_type="sentiment_analysis shutdown", message="Thread pool executor closed")

        # Close database connection pool
        self.db_pool.close()
        self.structured_logger.info(event_type="sentiment_analysis shutdown", message="Database connection pool closed")

        self.structured_logger.info(event_type="sentiment_analysis shutdown", message="Shutdown complete")

    def _process_sentiment_and_write_to_db(
        self, 
        text_product_pairs: list[tuple[str, str]],
        enriched_pairs: list[tuple[str, str, str, str, datetime]],
        comment_ids: set[str]
    ) -> tuple[int, int]:
        """
        Method for taking in a list of tuples (comment_text, product_name) and doing sentiment analysis
        and batch writing to database

        Args:
            text_product_pairs: a list of tuples (comment_text, product_name)
            enriched_pairs: a list of tuples (comment_id, comment_body, product_name, created_utc)
            comment_ids: a set of all unique comment ids that were processed

        Returns:
            tuple containing the number of rows inserted and rows updated
        """
        product_sentiments: list[ProductSentiment] = []

        sentiment_results = self.ABSA.SentimentAnalysis(text_product_pairs)

        # use zip to preserve comment id ordering
        for (comment_id, _, category, product_name, created_utc), (_, sentiment_score) in zip(enriched_pairs, sentiment_results):
            product_sentiments.append(ProductSentiment(
                comment_id=comment_id,
                product_name=product_name,
                category=category,
                sentiment_score=sentiment_score,
                created_utc=created_utc
            ))

        with self.db_pool.connection() as conn:
            with conn.transaction():
                rows_inserted = batch_insert_product_sentiment(conn, product_sentiments)
                rows_updated = mark_comments_processed(conn, list(comment_ids))

        return rows_inserted, rows_updated

    def _process_comments(self, comments: list[UnprocessedComment]) -> tuple[int, int]:
        """
        Method for processing comments fetched from the postgres unprocessed_comment table

        Args:
            comments: a list of unprocessed comments
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
        text_product_pairs = [(comment_text, product_name)
                              for _, comment_text, _, product_name, _ in enriched_pairs]
        
        rows_inserted, rows_updated = self._process_sentiment_and_write_to_db(text_product_pairs, enriched_pairs, comment_ids)
        
        return rows_inserted, rows_updated

    def run(self) -> None:
        """Main worker loop that polls for unprocessed comments for a category and processes them"""
        try:
            category = self.settings.product_category
            self.structured_logger.info(event_type="sentiment_analysis worker", message="Starting main worker loop")

            while not self.shutdown_requested:
                with self.db_pool.connection() as conn:
                    comments = fetch_unprocessed_comments(conn, category, batch_size=200)

                # This stops the service from running once all comments are processed
                if not comments:
                    self.structured_logger.info(
                        event_type="sentiment analysis worker",
                        message=f"All comments processed for category {category}. Exiting"
                    )
                    break

                rows_inserted, rows_updated = self._process_comments(comments)
                self.structured_logger.info(
                    event_type="sentiment_analysis worker",
                    message=f"Processed batch: {rows_inserted} sentiments inserted, {rows_updated} comments marked processed"
                )

        except Exception as e:
            self.structured_logger.error(event_type="sentiment_analysis worker", message=f"Error in worker loop: {e}")
            raise
        finally:
            self._cleanup()
                

if __name__ == "__main__":
    StartService().run()
