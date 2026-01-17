from src.dags.product_category_ranking import create_ranking_dag
from src.config.settings import Settings

settings = Settings()

def test_dag_loads_with_correct_configs() -> None:
    """Dag should load with expected values"""
    dag = create_ranking_dag("GPU")
    
    assert dag.dag_id == "product_gpu_ranking"
    assert dag.schedule == '30 0 * * *'
    assert dag.start_date == settings.START_DATE
    assert dag.catchup is False
    assert sorted(dag.tags) == sorted(['ranking', 'gpu'])
    assert dag.max_active_runs == settings.MAX_ACTIVE_RUNS

def test_loads_dag_tasks() -> None:
    """Product category ranking dag should load 2 tasks"""
    dag = create_ranking_dag("GPU")

    assert dag is not None
    assert len(dag.tasks) == 2 # should be 90d and all_time

def test_correct_dag_tasks() -> None:
    """Product category ranking dag should load the 2 expected tasks"""
    dag = create_ranking_dag("GPU")

    expected_tasks = sorted([                                                                               
      "rank_gpu_products_all_time",                                                                        
      "rank_gpu_products_90_day",                                                             
    ])                                                                                                      
                                                                                                            
    actual_tasks = sorted(task.task_id for task in dag.tasks)
    
    assert actual_tasks == expected_tasks