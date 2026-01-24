from tests.utils.services import configure_mock_service
from kubernetes.client import CoreV1Api
from tests.utils.airflow import trigger_dag
from tests.utils.airflow import wait_for_dag_run
from tests.utils.airflow import get_task_states

def test_sentiment_analysis_dag_pipeline_full_execution(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Full DAG runs: ingest >> wait ingest >> sentiment >> wait sentiment"""
    dag_id = "product_gpu_sentiment_analysis"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "success"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("ingest_gpu_comments") == "success"
    assert task_states.get("wait_ingest_gpu_comments") == "success"
    assert task_states.get("analyze_gpu_product_sentiments") == "success"
    assert task_states.get("wait_analyze_gpu_product_sentiments") == "success"

def test_downstream_tasks_skipped_on_upstream_failure(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """wait ingest should be skipped/failed if ingest fails."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        should_fail=True
    )

    dag_id = "product_gpu_sentiment_analysis"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("ingest_gpu_comments") == "failed"
    # Downstream tasks should not succeed
    assert task_states.get("wait_ingest_gpu_comments") in ("upstream_failed", "skipped", None)
