"""
Airflow DAG for fetching comments, doing sentiment analysis and generate product summaries
For all the product categories
"""
import json
from airflow.sdk import DAG
from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from src.config.settings import Settings
from src.utils.on_task_failure import on_task_failure

settings = Settings()

def create_llm_summary_dag() -> DAG:
    """
    Create a llm summary DAG .

    Returns:
        a dag that have the task to do llm summary for all products
    """
    dag = DAG(
        dag_id=f"product_summary",
        schedule="0 0 1 * *", # Runs every month on the midnight of the first day
        start_date=settings.START_DATE,
        catchup=False,
        tags=['summary'],
        max_active_runs=settings.MAX_ACTIVE_RUNS,
        doc_md="""
        ## Summary DAG
        Gets top 25 comments for all products from database and summarizes them using a LLM

        **Schedule:** Monthly
        """
    ) 
    
    with dag:
        llm_summary_all_time = HttpOperator(
            task_id='generate_product_summaries_all_time',
            http_conn_id='llm_summary_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'time_windows': "all_time"}),
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
            task_id="wait_generate_product_summaries_all_time",
            http_conn_id="llm_summary_service",
            endpoint="/status",
            response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
            poke_interval=settings.STATUS_POLL_INTERVAL,
            timeout=settings.EXECUTION_TIMEOUT,
            mode="reschedule", # Free up worker slot between pokes
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY
        ) 

        llm_summary_90_day = HttpOperator(
            task_id=f'generate_product_summaries_90_day',
            http_conn_id='llm_summary_service',
            endpoint='/run',
            method='POST',
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'time_windows': "90d"}),
            response_check=lambda response: response.json()['status'] in ['completed', 'cancelled'],
            log_response=True,
            execution_timeout=settings.EXECUTION_TIMEOUT,
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY,
            retry_exponential_backoff=True,
            max_retry_delay=settings.MAX_RETRY_DELAY
        )

        # Wait for 90 day task to finish by polling /status endpoint until its done
        wait_90_day = HttpSensor(
            task_id="wait_generate_product_summaries_90_day",
            http_conn_id="llm_summary_service",
            endpoint="/status",
            response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
            poke_interval=settings.STATUS_POLL_INTERVAL,
            timeout=settings.EXECUTION_TIMEOUT,
            mode="reschedule", # Free up worker slot between pokes
            on_failure_callback=on_task_failure,
            retries=settings.NUM_RETRIES,
            retry_delay=settings.RETRY_DELAY
        )

        llm_summary_all_time >> wait_all_time >> llm_summary_90_day >> wait_90_day
        
    return dag

globals()[f'product_summary'] = create_llm_summary_dag()