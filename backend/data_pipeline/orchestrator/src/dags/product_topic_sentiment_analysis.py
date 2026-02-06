from airflow.sdk import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from src.config.settings import Settings
from src.utils.on_task_failure import on_task_failure
import json

settings = Settings()

def create_sentiment_analysis_dag(category: str, topic_list: list[str], subreddit_list: list[str]) -> DAG:
    """
    Create a sentiment analysis DAG for a specific category.

    Args:
        category: the category we are fetching for
        topic_list: the list of all product topics for the category
        subreddit_list: list of unique subreddits to fetch comments from for the current category

    Returns:
        a dag that have tasks that fetch/process comments for the specific category
    """
    from src.config.schedules import INGESTSCHEDULES

    dag = DAG(
        dag_id=f"product_{category.lower().replace(' ', '_')}_sentiment_analysis",
        schedule=INGESTSCHEDULES.get(category.upper()),
        start_date=settings.START_DATE,
        catchup=False,
        tags=['sentiment_analysis', category.lower().replace(' ', '_')],
        max_active_runs=settings.MAX_ACTIVE_RUNS,
        params={
            'category': category,
            'topics': topic_list,
            'subreddits': subreddit_list
        },
        doc_md=f"""
        ## Sentiment analysis DAG for {category}
        Ingests Reddit comments and runs sentiment analysis
        
        **Topics:** {', '.join(topic_list)}
        **Subreddits:** {', '.join(subreddit_list)}
        **Schedule:** Daily
        """
    )

    with dag:
        reddit_raw_comment_ingest = HttpOperator(
            task_id=f'ingest_{category.lower().replace(' ', '_')}_comments',
            http_conn_id='ingestion_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'category': category,
                'subreddit_list': subreddit_list
            }),
            response_check=lambda response: response.json()['status'] == "started",
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        # Wait for all_time task to finish by polling /status endpoint until its done
        wait_raw_comment_ingest = HttpSensor(
            task_id=f"wait_ingest_{category.lower().replace(' ', '_')}_comments",
            http_conn_id="ingestion_service",
            endpoint="/status",
            response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
            poke_interval=settings.STATUS_POLL_INTERVAL,
            timeout=settings.EXECUTION_TIMEOUT,
            mode="reschedule", # Free up worker slot between pokes
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY
        ) 

        sentiment_analysis = HttpOperator(
            task_id=f'analyze_{category.lower().replace(' ', '_')}_product_sentiments',
            http_conn_id='sentiment_analysis_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'topic_list': topic_list}),
            response_check=lambda response: response.json()['status'] == "started",
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        # Wait for all_time task to finish by polling /status endpoint until its done
        wait_sentiment_analysis = HttpSensor(
            task_id=f"wait_analyze_{category.lower().replace(' ', '_')}_product_sentiments",
            http_conn_id="sentiment_analysis_service",
            endpoint="/status",
            response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
            poke_interval=settings.STATUS_POLL_INTERVAL,
            timeout=settings.EXECUTION_TIMEOUT,
            mode="reschedule", # Free up worker slot between pokes
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY
        ) 

        reddit_raw_comment_ingest >> wait_raw_comment_ingest >> sentiment_analysis >> wait_sentiment_analysis

    return dag


# Create DAGs at module level so Airflow can discover them
# Skip during test imports for faster test execution
import sys
if 'pytest' not in sys.modules:
    from src.config.mappings import CATEGORYTOPIC
    from src.utils.extract_subreddit_list import extract_subreddit_list

    for _category in CATEGORYTOPIC:
        topic_list = CATEGORYTOPIC.get(_category, [])
        subreddit_list = extract_subreddit_list(_category)

        globals()[f'product_{_category.lower().replace(" ", "_")}_sentiment_analysis'] = create_sentiment_analysis_dag(_category, topic_list, subreddit_list)