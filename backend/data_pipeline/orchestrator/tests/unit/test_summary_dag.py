from src.dags.product_summary import create_llm_summary_dag
from src.config.settings import Settings

settings = Settings()

def test_dag_loads_with_correct_configs() -> None:
    """Dag should load with expected values"""
    dag = create_llm_summary_dag()

    assert dag.dag_id == 'product_summary'
    assert dag.schedule == '0 0 1 * *'
    assert dag.start_date == settings.START_DATE
    assert dag.catchup is False
    assert dag.tags == {'summary'}
    assert dag.max_active_runs == settings.MAX_ACTIVE_RUNS

def test_loads_dag_tasks() -> None:
    """product summary dag should load 1 task"""
    dag = create_llm_summary_dag()

    assert dag is not None
    assert len(dag.tasks) == 2 # should be llm summary all time and 90 day

def test_correct_dag_tasks() -> None:
    """product summary dag should load 1 task"""
    dag = create_llm_summary_dag()

    expected_tasks = sorted([                                                                               
      "generate_product_summaries_all_time",                                                                        
      "generate_product_summaries_90_day",                                                             
    ])                                                                                                      
                                                                                                            
    actual_tasks = sorted(task.task_id for task in dag.tasks)
    
    assert actual_tasks == expected_tasks