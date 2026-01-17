from airflow.providers.http.operators.http import HttpOperator
from src.dags.product_category_ranking import create_ranking_dag
from src.config.settings import Settings
from src.config.category_mappings import CategoryMappings
import json 

settings = Settings()

def test_ranking_all_time_task_correct_configs() -> None:
    """Test that ranking task for all time is created correctly with the correct configs"""
    dag = create_ranking_dag("GPU")

    ranking_task = dag.get_task("rank_gpu_products_all_time")

    assert isinstance(ranking_task, HttpOperator)
    assert ranking_task.task_id == "rank_gpu_products_all_time"
    assert ranking_task.endpoint == "/worker/run"
    assert ranking_task.method == "POST"
    assert ranking_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({
        'category': "GPU",
        'time_windows': "all_time",
        "bayesian_params": "30"
    })
    assert ranking_task.data == expected_api_params

    assert ranking_task.log_response is True
    assert ranking_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert ranking_task.retries == settings.NUM_RETRIES
    assert ranking_task.retry_delay == settings.RETRY_DELAY
    assert ranking_task.retry_exponential_backoff is True
    assert ranking_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_ranking_90_day_task_correct_configs() -> None:
    """Test that ranking task for 90 days is created correctly with the correct configs"""
    dag = create_ranking_dag("GPU")

    ranking_task = dag.get_task("rank_gpu_products_90_day")

    assert isinstance(ranking_task, HttpOperator)
    assert ranking_task.task_id == "rank_gpu_products_90_day"
    assert ranking_task.endpoint == "/worker/run"
    assert ranking_task.method == "POST"
    assert ranking_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({
        'category': "GPU",
        'time_windows': "90d",
        "bayesian_params": "30"
    })
    assert ranking_task.data == expected_api_params

    assert ranking_task.log_response is True
    assert ranking_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert ranking_task.retries == settings.NUM_RETRIES
    assert ranking_task.retry_delay == settings.RETRY_DELAY
    assert ranking_task.retry_exponential_backoff is True
    assert ranking_task.max_retry_delay == settings.MAX_RETRY_DELAY
