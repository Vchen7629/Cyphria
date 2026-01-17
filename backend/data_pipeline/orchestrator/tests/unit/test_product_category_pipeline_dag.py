from src.dags.product_category_pipelines import create_pipeline_dag
from src.config.settings import Settings

settings = Settings()

def test_dag_loads_with_correct_configs() -> None:
    """Dag should load with expected values"""
    dag = create_pipeline_dag('GPU')
    assert dag.dag_id == 'product_gpu_pipeline'
    assert dag.schedule == '0 0 * * *'
    assert dag.start_date == settings.START_DATE
    assert dag.catchup is False
    assert sorted(dag.tags) == sorted(['pipeline', 'gpu'])
    assert dag.max_active_runs == settings.MAX_ACTIVE_RUNS

def test_loads_dag_tasks() -> None:
    """Product category pipeline dag should load 3 tasks"""
    dag = create_pipeline_dag('GPU')

    assert dag is not None
    assert len(dag.tasks) == 3 # should be ingest, sentiment, llm

def test_correct_dag_tasks() -> None:
    """Product category pipeline dag should load the 3 expected tasks"""
    dag = create_pipeline_dag('GPU')

    expected_tasks = sorted([                                                                               
      "ingest_gpu_comments",                                                                        
      "analyze_gpu_product_sentiments",                                                             
      "generate_gpu_product_summaries"                                                              
    ])                                                                                                      
                                                                                                            
    actual_tasks = sorted(task.task_id for task in dag.tasks)
    
    assert actual_tasks == expected_tasks