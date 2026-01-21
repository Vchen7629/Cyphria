import json
from airflow.sdk import DAG
from airflow.providers.http.operators.http import HttpOperator
from src.config.settings import Settings
from src.config.category_mappings import CategoryMappings
from src.utils.on_task_failure import on_task_failure

settings = Settings()


def create_ranking_dag(category: str) -> DAG:
    """
    Create a ranking DAG for a specific category.
    
    Args:
        category: the product category we are ranking

    Returns:
        a dag that have tasks that fetch and rank products for the specific category
    """
    dag = DAG(
        dag_id=f"product_{category.lower()}_ranking",
        schedule=CategoryMappings.RANKING_SCHEDULES.get(category),
        start_date=settings.START_DATE,
        catchup=False,
        tags=['ranking', category.lower()],
        max_active_runs=settings.MAX_ACTIVE_RUNS,
        doc_md="""
        ## Ranking DAG
        Reads from product_sentiment table for a category and creates ranking
        related metadata like:

        1. Assigning a letter grade (S, A+, A, etc)
        2. Calculate the Bayesian rated score for each product
        3. Assign the ranks (1-indexed) for all products in the category based on the score
        4. Add tags like is_top_rated, is_most_discussed, and has_limited_data

        for both a 90day and all_time time window and writes to the product_ranking table

        **Schedule:** Daily at xx:30
        """
    )

    with dag:
        product_ranking_all_time = HttpOperator(
            task_id=f'rank_{category.lower()}_products_all_time',
            http_conn_id="product_ranking_service",
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'category': category,
                'time_windows': "all_time",
                'bayesian_params': "30"
            }),
            response_check=lambda response: response.json()['status'] in ['completed', 'cancelled'],
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        product_ranking_90_days = HttpOperator(
            task_id=f'rank_{category.lower()}_products_90_day',
            http_conn_id="product_ranking_service",
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'category': category,
                'time_windows': "90d",
                'bayesian_params': "30"
            }),
            response_check=lambda response: response.json()['status'] in ['completed', 'cancelled'],
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        product_ranking_all_time >> product_ranking_90_days

    return dag


# Create DAGs at module level so Airflow can discover them
for _category in CategoryMappings.CATEGORIES:
    globals()[f'product_{_category.lower()}_ranking'] = create_ranking_dag(_category)