from airflow.providers.http.sensors.http import HttpSensor
from airflow.providers.http.operators.http import HttpOperator
from src.dags.product_topic_sentiment_analysis import create_sentiment_analysis_dag
from src.config.settings import Settings
import json 

settings = Settings()

def test_ingestion_task_correct_configs() -> None:
    """Test that ingestion task is created correctly with the correct configs"""
    # since we're iterating through a list of categories, use the last category
    dag = create_sentiment_analysis_dag("GPU", ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])
    ingest_task = dag.get_task("ingest_gpu_comments")

    assert isinstance(ingest_task, HttpOperator)
    assert ingest_task.task_id == "ingest_gpu_comments"
    assert ingest_task.endpoint == "/run"
    assert ingest_task.method == "POST"
    assert ingest_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({
        'topic_list': ['topic1', 'topic2'],
        'subreddit_list': ["subreddit1", "subreddit2"]
    })
    assert ingest_task.data == expected_api_params

    assert ingest_task.log_response is True
    assert ingest_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert ingest_task.retries == settings.NUM_RETRIES
    assert ingest_task.retry_delay == settings.RETRY_DELAY
    assert ingest_task.retry_exponential_backoff is True
    assert ingest_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_wait_all_time_task_correct_configs() -> None:
    """Test that wait task for all time is created correctly with the correct configs"""
    dag = create_sentiment_analysis_dag("GPU", ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])

    wait_task = dag.get_task("wait_ingest_gpu_comments")

    assert isinstance(wait_task, HttpSensor)
    assert wait_task.task_id == "wait_ingest_gpu_comments"
    assert wait_task.endpoint == "/status"
    assert wait_task.method == "GET"
    assert wait_task.timeout == settings.WAIT_TIMEOUT
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retry_delay == settings.RETRY_DELAY

def test_sentiment_analysis_task_correct_configs() -> None:
    """Test that sentiment_analysis task is created correctly with the correct configs"""
    dag = create_sentiment_analysis_dag("GPU", ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])    
    sentiment_analysis_task = dag.get_task("analyze_gpu_product_sentiments")

    assert isinstance(sentiment_analysis_task, HttpOperator)
    assert sentiment_analysis_task.task_id == "analyze_gpu_product_sentiments"
    assert sentiment_analysis_task.endpoint == "/run"
    assert sentiment_analysis_task.method == "POST"
    assert sentiment_analysis_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({'topic_list': ['topic1', 'topic2']})
    assert sentiment_analysis_task.data == expected_api_params

    assert sentiment_analysis_task.log_response is True
    assert sentiment_analysis_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert sentiment_analysis_task.retries == settings.NUM_RETRIES
    assert sentiment_analysis_task.retry_delay == settings.RETRY_DELAY
    assert sentiment_analysis_task.retry_exponential_backoff is True
    assert sentiment_analysis_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_wait_90_day_task_correct_configs() -> None:
    """Test that wait task for 90_day is created correctly with the correct configs"""
    dag = create_sentiment_analysis_dag("GPU", ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])

    wait_task = dag.get_task("wait_analyze_gpu_product_sentiments")

    assert isinstance(wait_task, HttpSensor)
    assert wait_task.task_id == "wait_analyze_gpu_product_sentiments"
    assert wait_task.endpoint == "/status"
    assert wait_task.method == "GET"
    assert wait_task.timeout == settings.WAIT_TIMEOUT
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retry_delay == settings.RETRY_DELAY


def test_sentiment_task_dependencies() -> None:
    """Test that sentiment task depends on ingest task"""
    dag = create_sentiment_analysis_dag("GPU", ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])

    ingest_task = dag.get_task("ingest_gpu_comments")
    wait_ingest = dag.get_task("wait_ingest_gpu_comments")
    # wait ingest depends on ingest being done
    assert wait_ingest in ingest_task.downstream_list
    sentiment_task = dag.get_task("analyze_gpu_product_sentiments")
    # sentiment depends on wait ingest being done
    assert sentiment_task in wait_ingest.downstream_list

    wait_sentiment = dag.get_task("wait_analyze_gpu_product_sentiments")
    # wait sentiment depends on sentiment being done
    assert wait_sentiment in sentiment_task.downstream_list