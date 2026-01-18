"""
Airflow DAG for fetching comments, doing sentiment analysis and generate product summaries
For all the product categories
"""
from airflow.sdk import DAG
from airflow.providers.http.operators.http import HttpOperator
from src.config.category_mappings import CategoryMappings
from src.config.settings import Settings
from src.utils.on_task_failure import on_task_failure
import json

settings = Settings()

def create_pipeline_dag(category: str) -> DAG:
    """
    Create a pipeline DAG for a specific category.
    
    Args:
        category: the product category we are fetching for

    Returns:
        a dag that have tasks that fetch/process comments for the specific category
    """
    dag = DAG(
        dag_id=f"product_{category.lower()}_pipeline",
        schedule=CategoryMappings.CATEGORY_SCHEDULES.get(category),
        start_date=settings.START_DATE,
        catchup=False,
        tags=['pipeline', category.lower()],
        max_active_runs=settings.MAX_ACTIVE_RUNS,
        doc_md="""
        ## Pipeline DAG
        Ingests Reddit comments, runs sentiment analysis, generates summaries.

        **Schedule:** Daily
        """
    )

    with dag:
        reddit_raw_comment_ingest = HttpOperator(
            task_id=f'ingest_{category.lower()}_comments',
            http_conn_id='ingestion_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'category': category,
                'subreddits': CategoryMappings.CATEGORY_SUBREDDITS.get(category, [])
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

        sentiment_analysis = HttpOperator(
            task_id=f'analyze_{category.lower()}_product_sentiments',
            http_conn_id='sentiment_analysis_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'category': category}),
            response_check=lambda response: response.json()['status'] in ['completed', 'cancelled'],
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        llm_summary = HttpOperator(
            task_id=f'generate_{category.lower()}_product_summaries',
            http_conn_id='llm_summary_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'category': category}),
            response_check=lambda response: response.json()['status'] in ['completed', 'cancelled'],
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        reddit_raw_comment_ingest >> [sentiment_analysis, llm_summary]

    return dag


# Create DAGs at module level so Airflow can discover them
for _category in CategoryMappings.CATEGORIES:
    globals()[f'product_{_category.lower()}_pipeline'] = create_pipeline_dag(_category)