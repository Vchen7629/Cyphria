"""
Airflow DAG for fetching comments, doing sentiment analysis and generate product summaries
For all the product categories
"""
from airflow.sdk import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from src.config.topic_mappings import ProductTopicMappings
from src.config.settings import Settings
from src.utils.on_task_failure import on_task_failure
import json

settings = Settings()

def create_sentiment_analysis_dag(product_topic: str) -> DAG:
    """
    Create a sentiment analysis DAG for a specific product_topic.
    
    Args:
        product_topic: the product topic we are fetching for

    Returns:
        a dag that have tasks that fetch/process comments for the specific product_topic
    """
    dag = DAG(
        dag_id=f"product_{product_topic.lower()}_sentiment_analysis",
        schedule=ProductTopicMappings.TOPIC_SCHEDULES.get(product_topic),
        start_date=settings.START_DATE,
        catchup=False,
        tags=['sentiment_analysis', product_topic.lower()],
        max_active_runs=settings.MAX_ACTIVE_RUNS,
        doc_md="""
        ## Sentiment analysis DAG
        Ingests Reddit comments and runs sentiment analysis
        
        **Schedule:** Daily
        """
    )

    with dag:
        reddit_raw_comment_ingest = HttpOperator(
            task_id=f'ingest_{product_topic.lower()}_comments',
            http_conn_id='ingestion_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'product_topic': product_topic,
                'subreddits': ProductTopicMappings.TOPIC_SUBREDDITS.get(product_topic, [])
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
            task_id=f"wait_ingest_{product_topic.lower()}_comments",
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
            task_id=f'analyze_{product_topic.lower()}_product_sentiments',
            http_conn_id='sentiment_analysis_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'product_topic': product_topic}),
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
            task_id=f"wait_analyze_{product_topic.lower()}_product_sentiments",
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
for _topic in ProductTopicMappings.TOPICS:
    globals()[f'product_{_topic.lower()}_sentiment_analysis'] = create_sentiment_analysis_dag(_topic)