import json
from airflow.sdk import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from src.config.settings import Settings
from src.config.topic_mappings import ProductTopicMappings
from src.utils.on_task_failure import on_task_failure

settings = Settings()


def create_ranking_dag(product_topic: str) -> DAG:
    """
    Create a ranking DAG for a specific product_topic.
    
    Args:
        product_topic: the product topic we are ranking

    Returns:
        a dag that have tasks that fetch and rank products for the specific topic
    """
    dag = DAG(
        dag_id=f"product_{product_topic.lower()}_ranking",
        schedule=ProductTopicMappings.RANKING_SCHEDULES.get(product_topic),
        start_date=settings.START_DATE,
        catchup=False,
        tags=['ranking', product_topic.lower()],
        max_active_runs=settings.MAX_ACTIVE_RUNS,
        doc_md="""
        ## Ranking DAG
        Reads from product_sentiment table for a product_topic and creates ranking
        related metadata like:

        1. Assigning a letter grade (S, A+, A, etc)
        2. Calculate the Bayesian rated score for each product
        3. Assign the ranks (1-indexed) for all products in the product_topic based on the score
        4. Add tags like is_top_rated, is_most_discussed, and has_limited_data

        for both a 90day and all_time time window and writes to the product_ranking table

        **Schedule:** Daily at xx:30
        """
    )

    with dag:
        product_ranking_all_time = HttpOperator(
            task_id=f'rank_{product_topic.lower()}_products_all_time',
            http_conn_id="product_ranking_service",
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'product_topic': product_topic,
                'time_windows': "all_time",
                'bayesian_params': "30"
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
        wait_all_time = HttpSensor(
            task_id=f"wait_rank_{product_topic.lower()}_products_all_time",
            http_conn_id="product_ranking_service",
            endpoint="/status",
            response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
            poke_interval=settings.STATUS_POLL_INTERVAL,
            timeout=settings.WAIT_TIMEOUT,
            mode="reschedule", # Free up worker slot between pokes
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY
        ) 

        product_ranking_90_days = HttpOperator(
            task_id=f'rank_{product_topic.lower()}_products_90_day',
            http_conn_id="product_ranking_service",
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({
                'product_topic': product_topic,
                'time_windows': "90d",
                'bayesian_params': "30"
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

        # Wait for 90_day task to finish by polling /status endpoint until its done
        # Lets airflow know if it failed or not
        wait_90_day = HttpSensor(
            task_id=f"wait_rank_{product_topic.lower()}_products_90_day",
            http_conn_id="product_ranking_service",
            endpoint="/status",
            response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
            poke_interval=settings.STATUS_POLL_INTERVAL,
            timeout=settings.WAIT_TIMEOUT,
            mode="reschedule", # Free up worker slot between pokes
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY
        )

        product_ranking_all_time >> wait_all_time >> product_ranking_90_days >> wait_90_day

    return dag


# Create DAGs at module level so Airflow can discover them
for _topic in ProductTopicMappings.TOPICS:
    globals()[f'product_{_topic.lower()}_ranking'] = create_ranking_dag(_topic)