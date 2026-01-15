from src.core.types import SentimentAggregate, ProductScore
from src.db_utils.conn import create_connection_pool
from src.db_utils.queries import fetch_aggregated_product_scores, batch_upsert_product_score
from src.calculation_utils.bayesian import calculate_bayesian_scores
from src.calculation_utils.grading import assign_grades, assign_ranks
from src.calculation_utils.badge import assign_is_top_pick, assign_is_most_discussed, assign_has_limited_data
from src.core.logger import StructuredLogger
from src.core.settings_config import Settings
from datetime import date
import signal
import numpy as np

class RankingCalculatorWorker:
    def __init__(self) -> None:
        self.settings = Settings()
        self.logger = StructuredLogger(pod="Ranking_Calculator")
        self.shutdown_requested: bool = False

        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        self._db_conn_lifespan()
        self.logger.info(event_type="ranking calculator startup", message="Worker init complete")
    
    def _db_conn_lifespan(self) -> None:
        """
        Method for handling database connection lifespan including creating connection pool,
        and checking the health
        """
        self.logger.info(event_type="ranking calculator startup", message="Creating database connection pool")
        self.db_pool = create_connection_pool()

        # Perform health check for db connection on startup
        self.logger.info(event_type="ranking calculator startup", message="Checking Database health...")
        try:
            with self.db_pool.connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    cursor.fetchone()
                self.logger.info(event_type="ranking calculator startup", message="Database health check passed")
        except Exception as e:
            self.logger.error(event_type="ranking calculator startup", message=f"Database health check failed: {e}")
            self.db_pool.close()
            raise 

    def _signal_handler(self, signum: int, _frame: object) -> None:
        """
        Signal handler for graceful shutdown

        Args:
            signum: Signal number
            _frame: Current stack frame (unused but required by signal handler signature)
        """
        signal_name = signal.Signals(signum).name
        self.logger.info(event_type="ranking calculator shutdown", message=f"Received {signal_name} signal, initiating graceful shutdown")
        self.shutdown_requested = True

    def _cleanup(self) -> None:
        """Cleanup resources on shutdown"""
        self.logger.info(event_type="ranking calculator shutdown", message="Cleaning up resources")

        # Close database connection pool
        self.db_pool.close()
        self.logger.info(event_type="ranking calculator shutdown", message="Database connection pool closed")

        self.logger.info(event_type="ranking calculator shutdown", message="Shutdown complete")
    
    def _build_product_ranking_object(
        self, 
        product_scores: list[SentimentAggregate],
        category: str,
        window: str,
        ranks: np.ndarray,
        grades: np.ndarray,
        bayesian_scores: np.ndarray,
        is_top_pick: np.ndarray,
        is_most_discussed: np.ndarray,
        has_limited_data: np.ndarray,
        calculation_date: date
    ) -> list[ProductScore]:
        """
        Take in the params and build the ranking object for product for inserting to db

        Args:
            product_scores: list of aggregated product sentiment scores 
            category: the category for the products
            window: the time window, either "90d" or "all_time"
            ranks: Numpy array of rank numbers (1-indexed)
            grades: Numpy array of letter grade for the product (S, A+, A, etc)
            bayesian_scores: Numpy array of bayesian score floats
            is_top_pick: Numpy array of bools (true if the product is top pick, false otherwise)
            is_most_discussed: Numpy array of bools (true if the  product is most mentioned, false otherwise)        
            has_limited_data: Numpy array of bools (true if the mention count for product is below threshold, false otherwise)
            calculation_date: Timestamp when its processed
        
        Returns:
            list of product score objects with metadata
        """
        rankings: list[ProductScore] = []

        for i, product in enumerate(product_scores):
            ranking = ProductScore(
                product_name=product.product_name,
                category=category,
                time_window=window,
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

    def _calculate_rankings_for_window(self, category: str, window: str) -> int:
        """
        Process rankings for a single category/time window combination:

        Args:
            category: Product category like "GPU" or "Laptop"
            window: Time window, "90d" or "all_time"

        Returns:
            number of products processed
        """
        with self.db_pool.connection() as conn:
            product_scores = fetch_aggregated_product_scores(conn, category, window)

            if not product_scores:
                self.logger.info(event_type="ranking calculation", message=f"No products found for {category}/{window}")
                return 0
            
            # to extract numpy arrays from pydantic models
            avg_sentiments = np.array([p.avg_sentiment for p in product_scores])
            mention_counts = np.array([p.mention_count for p in product_scores])

            bayesian_scores = calculate_bayesian_scores(
                avg_sentiments,
                mention_counts,
                min_mentions=self.settings.bayesian_params
            )

            grades = assign_grades(bayesian_scores)
            ranks = assign_ranks(bayesian_scores)

            is_top_pick = assign_is_top_pick(ranks)
            is_most_discussed = assign_is_most_discussed(mention_counts)
            has_limited_data = assign_has_limited_data(mention_counts, self.settings.bayesian_params)

            calculation_date = date.today()

            product_ranking_list = self._build_product_ranking_object(
                product_scores, 
                category,
                window,
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
                message=f"Processed {len(product_ranking_list)} for {category}/{window}")
            
            return len(product_ranking_list)

    def run(self) -> None:
        """Main worker loop"""
        try:
            res = self._calculate_rankings_for_window(self.settings.product_category, self.settings.time_windows)
        except Exception as e:
            self.logger.error(event_type="ranking calculator worker", message=f"Error in worker loop: {e}")
            raise
        finally:
            self._cleanup()

if __name__ == "__main__":
    RankingCalculatorWorker().run()