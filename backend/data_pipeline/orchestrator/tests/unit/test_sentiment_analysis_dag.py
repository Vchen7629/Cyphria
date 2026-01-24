from src.dags.product_topic_sentiment_analysis import create_sentiment_analysis_dag
from src.config.settings import Settings

settings = Settings()

def test_dag_loads_with_correct_configs() -> None:
    """Dag should load with expected values"""
    dag = create_sentiment_analysis_dag('GPU')
    assert dag.dag_id == 'product_gpu_sentiment_analysis'
    assert dag.schedule == '0 0 * * *'
    assert dag.start_date == settings.START_DATE
    assert dag.catchup is False
    assert sorted(dag.tags) == sorted(['sentiment_analysis', 'gpu'])
    assert dag.max_active_runs == settings.MAX_ACTIVE_RUNS

def test_loads_dag_tasks() -> None:
    """Product category sentiment analysis dag should load 4 tasks"""
    dag = create_sentiment_analysis_dag('GPU')

    assert dag is not None
    assert len(dag.tasks) == 4 # should be ingest, sentiment analysis, and 2 wait tasks

def test_correct_dag_tasks() -> None:
    """Product category sentiment analysis dag should load the 2 expected tasks"""
    dag = create_sentiment_analysis_dag('GPU')

    expected_tasks = sorted([                                                                               
      "ingest_gpu_comments",                                                                        
      "analyze_gpu_product_sentiments",
      "wait_ingest_gpu_comments",                                                                        
      "wait_analyze_gpu_product_sentiments",                                                             
    ])                                                                                                      
                                                                                                            
    actual_tasks = sorted(task.task_id for task in dag.tasks)
    
    assert actual_tasks == expected_tasks