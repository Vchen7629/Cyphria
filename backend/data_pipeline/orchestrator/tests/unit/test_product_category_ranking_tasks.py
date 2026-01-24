from airflow.providers.http.operators.http import HttpOperator
from airflow.providers.http.sensors.http import HttpSensor
from src.dags.product_category_ranking import create_ranking_dag
from src.config.settings import Settings
import json 

settings = Settings()

def test_ranking_all_time_task_correct_configs() -> None:
    """Test that ranking task for all time is created correctly with the correct configs"""
    dag = create_ranking_dag("GPU")

    ranking_task = dag.get_task("rank_gpu_products_all_time")

    assert isinstance(ranking_task, HttpOperator)
    assert ranking_task.task_id == "rank_gpu_products_all_time"
    assert ranking_task.endpoint == "/run"
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

def test_wait_all_time_task_correct_configs() -> None:
    """Test that wait task for all time is created correctly with the correct configs"""
    dag = create_ranking_dag("GPU")

    wait_task = dag.get_task("wait_rank_gpu_products_all_time")

    assert isinstance(wait_task, HttpSensor)
    assert wait_task.task_id == "wait_rank_gpu_products_all_time"
    assert wait_task.endpoint == "/status"
    assert wait_task.method == "GET"
    assert wait_task.timeout == settings.WAIT_TIMEOUT
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retry_delay == settings.RETRY_DELAY

def test_ranking_90_day_task_correct_configs() -> None:
    """Test that ranking task for 90 days is created correctly with the correct configs"""
    dag = create_ranking_dag("GPU")

    ranking_task = dag.get_task("rank_gpu_products_90_day")

    assert isinstance(ranking_task, HttpOperator)
    assert ranking_task.task_id == "rank_gpu_products_90_day"
    assert ranking_task.endpoint == "/run"
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
    assert ranking_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_wait_90_day_task_correct_configs() -> None:
    """Test that wait task for 90 day is created correctly with the correct configs"""
    dag = create_ranking_dag("GPU")

    wait_task = dag.get_task("wait_rank_gpu_products_90_day")

    assert isinstance(wait_task, HttpSensor)
    assert wait_task.task_id == "wait_rank_gpu_products_90_day"
    assert wait_task.endpoint == "/status"
    assert wait_task.method == "GET"
    assert wait_task.timeout == settings.WAIT_TIMEOUT
    assert wait_task.retries == settings.NUM_RETRIES
    assert wait_task.retry_delay == settings.RETRY_DELAY

def test_task_dependencies() -> None:
    """Test that dag dependencies are correct"""
    dag = create_ranking_dag("GPU")

    all_time_task = dag.get_task("rank_gpu_products_all_time")
    wait_all_time = dag.get_task("wait_rank_gpu_products_all_time")
    # wait all_time depends on all_time being done
    assert wait_all_time in all_time_task.downstream_list

    ninety_day_task = dag.get_task("rank_gpu_products_90_day")
    # ninety day only starts once wait all_time is done
    assert ninety_day_task in wait_all_time.downstream_list

    wait_ninety_day = dag.get_task("wait_rank_gpu_products_90_day")
    # wait ninety day depends on 90 day being done
    assert wait_ninety_day in ninety_day_task.downstream_list
