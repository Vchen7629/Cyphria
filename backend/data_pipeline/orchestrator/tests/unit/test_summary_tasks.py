import json
from airflow.providers.http.operators.http import HttpOperator
from src.dags.product_summary import create_llm_summary_dag
from src.config.settings import Settings

settings = Settings()

def test_llm_summary_task_all_time_correct_configs() -> None:
    """Test that llm summary task all time is created correctly with the correct configs"""
    dag = create_llm_summary_dag()
    llm_summary_task = dag.get_task("generate_product_summaries_all_time")

    assert isinstance(llm_summary_task, HttpOperator)
    assert llm_summary_task.task_id == "generate_product_summaries_all_time"
    assert llm_summary_task.endpoint == "/run"
    assert llm_summary_task.method == "POST"
    assert llm_summary_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({'time_windows': "all_time"})
    assert llm_summary_task.data == expected_api_params
    assert llm_summary_task.log_response is True
    assert llm_summary_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert llm_summary_task.retries == settings.NUM_RETRIES
    assert llm_summary_task.retry_delay == settings.RETRY_DELAY
    assert llm_summary_task.retry_exponential_backoff is True
    assert llm_summary_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_llm_summary_task_90_day_correct_configs() -> None:
    """Test that llm summary task 90 day is created correctly with the correct configs"""
    dag = create_llm_summary_dag()
    llm_summary_task = dag.get_task("generate_product_summaries_90_day")

    assert isinstance(llm_summary_task, HttpOperator)
    assert llm_summary_task.task_id == "generate_product_summaries_90_day"
    assert llm_summary_task.endpoint == "/run"
    assert llm_summary_task.method == "POST"
    assert llm_summary_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({'time_windows': "90d"})
    assert llm_summary_task.data == expected_api_params
    assert llm_summary_task.log_response is True
    assert llm_summary_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert llm_summary_task.retries == settings.NUM_RETRIES
    assert llm_summary_task.retry_delay == settings.RETRY_DELAY
    assert llm_summary_task.retry_exponential_backoff is True
    assert llm_summary_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_task_dependencies() -> None:
    """Test that 90d task depends on all_time task"""
    dag = create_llm_summary_dag()

    all_time_task = dag.get_task("generate_product_summaries_all_time")
    ninety_day_task = dag.get_task("generate_product_summaries_90_day")

    assert ninety_day_task in all_time_task.downstream_list
