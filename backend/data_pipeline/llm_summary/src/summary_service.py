from openai import OpenAI
from psycopg_pool import ConnectionPool
from src.core.logger import StructuredLogger
from src.db.queries import fetch_top_comments_for_product
from src.db.queries import fetch_unique_products
from src.db.queries import upsert_llm_summaries
from src.api.job_state import JobState
from src.api.schemas import SummaryResult
from src.llm_client.prompts import SYSTEM_PROMPT
from src.llm_client.prompts import build_user_prompt
from src.llm_client.response_parser import parse_tldr
from src.llm_client.response_parser import TLDRValidationError
from src.llm_client.retry import retry_llm_api
import psycopg


class LLMSummaryService:
    def __init__(
        self,
        time_window: str,
        llm_model_name: str,
        llm_client: OpenAI,
        logger: StructuredLogger,
        db_pool: ConnectionPool,
    ) -> None:
        self.time_window = time_window
        self.llm_model_name = llm_model_name
        self.llm_client = llm_client
        self.logger = logger
        self.db_pool = db_pool

        # cancellation flag, used to request graceful shutdown
        # This flag is set externally by signal_handler.py when SIGTERM/SIGINT is received
        self.cancel_requested = False

    def _fetch_products_with_comments(
        self, db_conn: psycopg.Connection
    ) -> list[tuple[str, list[str]]]:
        """
        Fetch all products and their top comments

        Args:
            db_conn: psycopg database connection

        Returns:
            a list of tuples (product_name, [comment_1, comment_2, ...])
        """
        result: list[tuple[str, list[str]]] = []

        product_name_list: list[str] = fetch_unique_products(db_conn, self.time_window)

        for product_name in product_name_list:
            if self.cancel_requested:
                self.logger.info(
                    event_type="llm_summary run",
                    message="Cancellation requested during fetch, stopping early",
                )
                break

            top_comments: list[str] = fetch_top_comments_for_product(
                db_conn, product_name, self.time_window
            )

            if not top_comments:
                continue

            result.append((product_name, top_comments))

        return result

    def _generate_summary(self, product_name: str, comments: list[str]) -> str:
        """
        Generate LLM summary for a product from their top comments

        Args:
            product_name: the product we are generating summary for
            comments: the list of the products top comments based on their sentiment score

        Returns:
            A llm summary string, or empty string if generation fails
        """
        if not product_name or not comments:
            self.logger.warning(
                event_type="llm_summary run", message="No product name or comment list, skipping"
            )
            return ""

        user_prompt = build_user_prompt(product_name, comments)

        response = self.llm_client.responses.create(
            model=self.llm_model_name, instructions=SYSTEM_PROMPT, input=user_prompt
        )

        response_text = response.output_text
        if not response_text:
            raise TLDRValidationError("Empty response from LLM")

        tldr = parse_tldr(response_text, self.logger)

        self.logger.info(
            event_type="llm_summary run",
            message=f"Generated TLDR for {product_name}, time window: {self.time_window}",
        )

        return tldr

    def _insert_summary(self, db_conn: psycopg.Connection, product_name: str, summary: str) -> bool:
        """
        Insert the llm summary for a product into the database

        Args:
            db_conn: psycopg database connection
            product_name: the name of the product we are inserting the summary for
            summary: the llm summary

        Returns:
            true if the insert is successful, false otherwise
        """
        inserted: bool = upsert_llm_summaries(
            db_conn, product_name, summary, self.time_window, self.llm_model_name
        )

        return inserted

    def _run_summary_pipeline(self) -> SummaryResult:
        """Run the entire processing pipeline"""
        products_processed = 0

        with self.db_pool.connection() as conn:
            products_list: list[tuple[str, list[str]]] = self._fetch_products_with_comments(conn)
            self.logger.info(
                "llm_summary run",
                message=f"fetched {len(products_list)} products, for {self.time_window} time window",
            )

            for product_name, comments in products_list:
                try:
                    if self.cancel_requested:
                        self.logger.info(
                            "llm_summary run",
                            message=f"Cancellation requested, stopping. processed {products_processed} products",
                        )
                        break

                    # wrapping the generate summary here instead of over private method since it can't access self.logger
                    generate_with_retry = retry_llm_api(logger=self.logger)(
                        lambda: self._generate_summary(product_name, comments)
                    )

                    summary: str = generate_with_retry()
                    if not summary:
                        continue

                    inserted: bool = self._insert_summary(conn, product_name, summary)
                    if not inserted:
                        continue

                    products_processed += 1
                except Exception as e:
                    self.logger.error(
                        "llm_summary run",
                        message=f"Unexpected error processing {product_name}, error={str(e)}",
                    )
                    continue

        return SummaryResult(products_summarized=products_processed, cancelled=False)

    def run_single_cycle(self, job_state: JobState) -> None:
        """
        Run one complete summary cycle and update job state
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
            result = self._run_summary_pipeline()

            job_state.complete_job(result)

            self.logger.info(
                event_type="llm_summary run",
                message=f"Ingestion completed: {result.products_summarized} products summarized",
            )

        except Exception as e:
            self.logger.error(event_type="llm_summary run", message=f"Summary failed: {str(e)}")
            job_state.fail_job(str(e))
        finally:
            # Clean up run state after job completes or fails
            run_state.run_in_progress = False
            run_state.current_service = None
