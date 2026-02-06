from src.dags.product_topic_sentiment_analysis import create_sentiment_analysis_dag
from src.config.settings import Settings

settings = Settings()

def test_dag_loads_with_correct_configs() -> None:
    """Dag should load with expected values"""
    dag = create_sentiment_analysis_dag('Computing', ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])
    assert dag.dag_id == 'product_computing_sentiment_analysis'
    assert dag.schedule == '0 0 * * *'
    assert dag.start_date == settings.START_DATE
    assert dag.params == {
        'category': 'Computing',
        'topics': ['topic1', 'topic2'],
        'subreddits': ['subreddit1', 'subreddit2']
    }
    assert dag.catchup is False
    assert sorted(dag.tags) == sorted(['sentiment_analysis', 'computing'])
    assert dag.max_active_runs == settings.MAX_ACTIVE_RUNS

def test_loads_dag_tasks() -> None:
    """Product category sentiment analysis dag should load 4 tasks"""
    dag = create_sentiment_analysis_dag('Computing', ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])

    assert dag is not None
    assert len(dag.tasks) == 4 # should be ingest, sentiment analysis, and 2 wait tasks

def test_correct_dag_tasks() -> None:
    """Product category sentiment analysis dag should load the 2 expected tasks"""
    dag = create_sentiment_analysis_dag('Computing', ['topic1', 'topic2'], ['subreddit1', 'subreddit2'])

    expected_tasks = sorted([                                                                               
      "ingest_computing_comments",                                                                        
      "analyze_computing_product_sentiments",
      "wait_ingest_computing_comments",                                                                        
      "wait_analyze_computing_product_sentiments",                                                             
    ])                                                                                                      
                                                                                                            
    actual_tasks = sorted(task.task_id for task in dag.tasks)
    
    assert actual_tasks == expected_tasks

def test_nonexistant_category() -> None:
    """Passing a category that doesnt exist should make the schedule None"""
    dag = create_sentiment_analysis_dag("GPU", ["topic1", "topic2"], ["subreddit1", "subreddit2"])
    
    assert dag.schedule == None
