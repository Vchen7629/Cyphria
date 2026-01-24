from datetime import timezone
from datetime import datetime
from psycopg_pool import ConnectionPool
from src.api.job_state import JobState
from src.api.schemas import ProductScore
from src.api.schemas import RankingResult
from src.api.schemas import SentimentAggregate
from src.db.queries import batch_upsert_product_score
from src.db.queries import fetch_aggregated_product_scores
from src.calculation_utils.grading import assign_ranks
from src.calculation_utils.grading import assign_grades
from src.calculation_utils.badge import assign_is_top_pick
from src.calculation_utils.badge import assign_has_limited_data
from src.calculation_utils.badge import assign_is_most_discussed
from src.calculation_utils.bayesian import calculate_bayesian_scores
from src.core.logger import StructuredLogger
from src.core.settings_config import Settings
import numpy as np

class RankingService:
    def __init__(
        self, 
        logger: StructuredLogger, 
        db_pool: ConnectionPool,
        product_topic: str,
        time_window: str
    ) -> None:
        self.settings = Settings()
        self.logger = logger
        self.db_pool = db_pool
        self.product_topic = product_topic
        self.time_window = time_window

        # cancellation flag, used to request graceful shutdown
        self.cancel_requested = False
    
    def _build_product_ranking_object(
        self, 
        product_scores: list[SentimentAggregate],
        product_topic: str,
        time_window: str,
        ranks: np.ndarray,
        grades: np.ndarray,
        bayesian_scores: np.ndarray,
        is_top_pick: np.ndarray,
        is_most_discussed: np.ndarray,
        has_limited_data: np.ndarray,
        calculation_date: datetime
    ) -> list[ProductScore]:
        """
        Take in the params and build the ranking object for product for inserting to db

        Args:
            product_scores: list of aggregated product sentiment scores 
            product_topic: the product_topic for the products
            time_window: the time window, either "90d" or "all_time"
            ranks: Numpy array of rank numbers (1-indexed)
            grades: Numpy array of letter grade for the product (S, A+, A, etc)
            bayesian_scores: Numpy array of bayesian score floats
            is_top_pick: Numpy array of bools (true if the product is top pick, false otherwise)
            is_most_discussed: Numpy array of bools (true if the  product is most mentioned, false otherwise)        
            has_limited_data: Numpy array of bools (true if the mention count for product is below threshold, false otherwise)
            calculation_date: Timestamp when its processed
        
        Returns:
            list of product score objects with metadata, or empty array if missing params or cancelled
        """
        if not all([product_scores, product_topic, time_window, ranks, grades, bayesian_scores, is_top_pick, is_most_discussed, has_limited_data, calculation_date]):
            self.logger.warning(event_type="ranking_service run", message="Missing a input param")
            return []

        if product_topic.strip() == "" or time_window.strip() == "":
            self.logger.warning(event_type="ranking_service run", message="Missing a product_topic or time window")
            return []
            
        rankings: list[ProductScore] = []

        for i, product in enumerate(product_scores):
            if self.cancel_requested:
                self.logger.info(event_type="ranking_service run", message="Cancel requested, build product ranking object...")
                return []

            ranking = ProductScore(
                product_name=product.product_name,
                product_topic=product_topic,
                time_window=time_window,
                rank=int(ranks[i]),
                grade=str(grades[i]),
                bayesian_score=float(bayesian_scores[i]),
                avg_sentiment=product.avg_sentiment,
                approval_percentage=product.approval_percentage,
                mention_count=product.mention_count,
                positive_count=product.positive_count,
                negative_count=product.negative_count,
                neutral_count=product.neutral_count,
                is_top_pick=bool(is_top_pick[i]),
                is_most_discussed=bool(is_most_discussed[i]),
                has_limited_data=bool(has_limited_data[i]),
                calculation_date=calculation_date
            )
            rankings.append(ranking)

        if not rankings:
            return []

        return rankings

    def _calculate_rankings_for_window(self, product_topic: str, time_window: str) -> int:
        """
        Process rankings for a single topic/time window combination:

        Args:
            product_topic: Product topic like "GPU" or "Laptop"
            time_window: Time window, "90d" or "all_time"

        Returns:
            number of products processed, or 0 if missing params
        """
        if not product_topic or not product_topic.strip == "" or not time_window or not time_window.strip() == "":
            self.logger.warning(event_type="ranking_service run", message="Missing product_topic or time window")
            return 0

        with self.db_pool.connection() as conn:
            if self.cancel_requested:
                self.logger.info(event_type="ranking_service run", message="Cancel requested, skipping fetch_aggregated...")
                return 0

            product_scores = fetch_aggregated_product_scores(conn, product_topic, time_window)

            if not product_scores:
                self.logger.info(event_type="ranking calculation", message=f"No products found for {product_topic}/{time_window}")
                return 0
            
            # to extract numpy arrays from pydantic models
            avg_sentiments = np.array([p.avg_sentiment for p in product_scores])
            mention_counts = np.array([p.mention_count for p in product_scores])

            bayesian_scores = calculate_bayesian_scores(
                avg_sentiments,
                mention_counts,
                min_mentions=self.settings.BAYESIAN_PARAMS
            )

            grades = assign_grades(bayesian_scores)
            ranks = assign_ranks(bayesian_scores)

            is_top_pick = assign_is_top_pick(ranks)
            is_most_discussed = assign_is_most_discussed(mention_counts)
            has_limited_data = assign_has_limited_data(mention_counts, self.settings.BAYESIAN_PARAMS)

            calculation_date = datetime.now(tz=timezone.utc)

            product_ranking_list = self._build_product_ranking_object(
                product_scores, 
                product_topic,
                time_window,
                ranks,
                grades,
                bayesian_scores,
                is_top_pick,
                is_most_discussed,
                has_limited_data,
                calculation_date
            )

            if not product_ranking_list:
                return 0
            
            batch_upsert_product_score(conn, product_ranking_list)
            conn.commit()

            self.logger.info(
                event_type="ranking calculation", 
                message=f"Processed {len(product_ranking_list)} for {product_topic}/{time_window}")
            
            return len(product_ranking_list)

    def _run_ranking_pipeline(self) -> RankingResult:
        """
        Main orchestrator function: fetch, process, and write to db for products
        
        Returns:
            RankingResult with counts of posts/comments processed
        """
        products_processed = self._calculate_rankings_for_window(self.product_topic, self.time_window)

        return RankingResult(
            products_processed=products_processed,
            cancelled=self.cancel_requested
        )
    
    def run_single_cycle(self, job_state: JobState) -> None:
        """
        Run one complete ranking cycle and update job state
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
            result = self._run_ranking_pipeline()

            job_state.complete_job(result)

            self.logger.info(
                event_type="ranking_service run",
                message=f"Ingestion completed: {result.products_processed} products processed"
            )

        except Exception as e:
            self.logger.error(event_type="ranking_service run", message=f"Ranking failed: {str(e)}")
            job_state.fail_job(str(e))
        finally:
            # Clean up run state after job completes or fails
            run_state.run_in_progress = False
            run_state.current_service = None
