from src.config.settings import Settings
from src.dags.product_topic_ranking import create_ranking_dag

settings = Settings()

def test_dag_loads_with_correct_configs() -> None:
    """Dag should load with expected values"""
    dag = create_ranking_dag("Computing", ["topic1", "topic2"])
    
    assert dag.dag_id == "product_computing_ranking"
    assert dag.schedule == '20 0 * * *'
    assert dag.start_date == settings.START_DATE
    assert dag.params == {
        'category': 'Computing',
        'topics': ["topic1", "topic2"]
    }
    assert dag.catchup is False
    assert sorted(dag.tags) == sorted(['ranking', 'computing'])
    assert dag.max_active_runs == settings.MAX_ACTIVE_RUNS

def test_loads_dag_tasks() -> None:
    """Product category ranking dag should load 4 tasks"""
    dag = create_ranking_dag("Computing", ["topic1", "topic2"])

    assert dag is not None
    assert len(dag.tasks) == 4 # should be 90d and all_time and two wait tasks

def test_correct_dag_tasks() -> None:
    """Product category ranking dag should load the 4 expected tasks"""
    dag = create_ranking_dag("Computing", ["topic1", "topic2"])

    expected_tasks = sorted([                                                                               
        "rank_computing_products_all_time",
        "wait_rank_computing_products_all_time",                                                                        
        "rank_computing_products_90_day",
        "wait_rank_computing_products_90_day",                                                                                                              
    ])                                                                                                      
                                                                                                            
    actual_tasks = sorted(task.task_id for task in dag.tasks)
    
    assert actual_tasks == expected_tasks

def test_nonexistant_category() -> None:
    """Passing a category that doesnt exist should make the schedule None"""
    dag = create_ranking_dag("GPU", ["topic1", "topic2"])
    
    assert dag.schedule == None
