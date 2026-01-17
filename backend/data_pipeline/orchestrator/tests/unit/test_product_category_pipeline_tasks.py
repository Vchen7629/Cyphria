from airflow.providers.http.operators.http import HttpOperator
from src.dags.product_category_pipelines import create_pipeline_dag
from src.config.settings import Settings
from src.config.category_mappings import CategoryMappings
import json 

settings = Settings()

def test_ingestion_task_correct_configs() -> None:
    """Test that ingestion task is created correctly with the correct configs"""
    # since we're iterating through a list of categories, use the last category
    dag = create_pipeline_dag("GPU")
    ingest_task = dag.get_task("ingest_gpu_comments")

    assert isinstance(ingest_task, HttpOperator)
    assert ingest_task.task_id == "ingest_gpu_comments"
    assert ingest_task.endpoint == "/worker/run"
    assert ingest_task.method == "POST"
    assert ingest_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({
        'category': "GPU",
        'subreddits': CategoryMappings.CATEGORY_SUBREDDITS.get(
            "GPU", 
            ["nvidia", "radeon", "amd", "IntelArc", "buildapc", "gamingpc", "pcbuild", "hardware"]
        )
    })
    assert ingest_task.data == expected_api_params

    assert ingest_task.log_response is True
    assert ingest_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert ingest_task.retries == settings.NUM_RETRIES
    assert ingest_task.retry_delay == settings.RETRY_DELAY
    assert ingest_task.retry_exponential_backoff is True
    assert ingest_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_sentiment_analysis_task_correct_configs() -> None:
    """Test that sentiment_analysis task is created correctly with the correct configs"""
    dag = create_pipeline_dag("GPU")    
    sentiment_analysis_task = dag.get_task("analyze_gpu_product_sentiments")

    assert isinstance(sentiment_analysis_task, HttpOperator)
    assert sentiment_analysis_task.task_id == "analyze_gpu_product_sentiments"
    assert sentiment_analysis_task.endpoint == "/worker/run"
    assert sentiment_analysis_task.method == "POST"
    assert sentiment_analysis_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({
        'category': "GPU",
        'polling_interval': "0.5"
    })
    assert sentiment_analysis_task.data == expected_api_params

    assert sentiment_analysis_task.log_response is True
    assert sentiment_analysis_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert sentiment_analysis_task.retries == settings.NUM_RETRIES
    assert sentiment_analysis_task.retry_delay == settings.RETRY_DELAY
    assert sentiment_analysis_task.retry_exponential_backoff is True
    assert sentiment_analysis_task.max_retry_delay == settings.MAX_RETRY_DELAY

def test_llm_summary_task_correct_configs() -> None:
    """Test that llm summary task is created correctly with the correct configs"""
    dag = create_pipeline_dag("GPU")    
    llm_summary_task = dag.get_task("generate_gpu_product_summaries")

    assert isinstance(llm_summary_task, HttpOperator)
    assert llm_summary_task.task_id == "generate_gpu_product_summaries"
    assert llm_summary_task.endpoint == "/worker/run"
    assert llm_summary_task.method == "POST"
    assert llm_summary_task.headers == {"Content-Type": "application/json"}

    expected_api_params = json.dumps({'category': "GPU"})
    assert llm_summary_task.data == expected_api_params

    assert llm_summary_task.log_response is True
    assert llm_summary_task.execution_timeout == settings.EXECUTION_TIMEOUT
    assert llm_summary_task.retries == settings.NUM_RETRIES
    assert llm_summary_task.retry_delay == settings.RETRY_DELAY
    assert llm_summary_task.retry_exponential_backoff is True
    assert llm_summary_task.max_retry_delay == settings.MAX_RETRY_DELAY


def test_sentiment_task_dependencies() -> None:
    """Test that sentiment task depends on ingest task"""
    dag = create_pipeline_dag("GPU")

    ingest_task = dag.get_task("ingest_gpu_comments")
    sentiment_task = dag.get_task("analyze_gpu_product_sentiments")

    assert sentiment_task in ingest_task.downstream_list

def test_llm_summary_task_dependencies() -> None:
    """Test that llm summary task depends on ingest task"""
    dag = create_pipeline_dag("GPU")
    
    ingest_task = dag.get_task("ingest_gpu_comments")
    llm_summary_task = dag.get_task("generate_gpu_product_summaries")

    assert llm_summary_task in ingest_task.downstream_list
