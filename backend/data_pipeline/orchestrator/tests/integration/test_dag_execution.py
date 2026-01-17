from kubernetes.client import CoreV1Api
from tests.utils.mock_service import configure_mock_service
from tests.utils.mock_service import replace_mock_service
from tests.utils.pod_lifecycle import delete_pod
from tests.utils.airflow import trigger_dag
from tests.utils.airflow import wait_for_dag_run
from tests.utils.airflow import get_task_states
from tests.utils.airflow import exec_airflow_cmd

def test_dag_task_success_completed(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
    mock_services: dict,
) -> None:
    """Task should succeed when service returns {"status": "completed"}."""
    dag_id = "product_gpu_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "success", f"Expected success, got {result}"

def test_dag_task_success_cancelled(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Task succeeds when service returns {"status": "cancelled"}."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        response_status="cancelled"
    )

    dag_id = "product_laptop_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "success"

def test_dag_pipeline_full_execution(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Full DAG runs: ingest >> [sentiment, llm_summary]."""
    dag_id = "product_gpu_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "success"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("ingest_gpu_comments") == "success"
    assert task_states.get("analyze_gpu_product_sentiments") == "success"
    assert task_states.get("generate_gpu_product_summaries") == "success"

def test_dag_ranking_parallel_execution(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Ranking DAG should run both time windows in parallel."""
    dag_id = "product_gpu_ranking"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "success"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("rank_gpu_products_all_time") == "success"
    assert task_states.get("rank_gpu_products_90_day") == "success"

def test_dag_task_fails_on_500_error(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Task task should fail when service returns HTTP 500."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        should_fail=True
    )

    dag_id = "product_headphone_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

def test_dag_task_fails_on_invalid_status(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Task should fail when status not in ["completed", "cancelled"]."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        response_status="invalid_status"
    )

    dag_id = "product_laptop_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

def test_dag_task_fails_on_pod_not_ready(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
    mock_service_configmap: str,
) -> None:
    """Task should fail when the service pod is not ready (connection refused)."""
    # Delete the pod entirely, service still exists but has no endpoints
    delete_pod(k8s_core_api, test_namespace, "ingestion-service")

    dag_id = "product_laptop_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    # Restore service pod
    replace_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        mock_service_configmap, response_status="completed"
    )

def test_dag_task_fails_on_timeout(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Task should fail when the service response exceeds the execution_timeout."""
    # Response delay set to longer than task timeout (conftest sets it to 10s)
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        response_delay=12  # 12s > 10s
    )

    dag_id = "product_laptop_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

def test_dag_downstream_tasks_skipped_on_upstream_failure(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Sentiment/llm_summary tasks are skipped/failed if ingest fails."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        should_fail=True
    )

    dag_id = "product_gpu_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("ingest_gpu_comments") == "failed"
    # Downstream tasks should not succeed
    assert task_states.get("analyze_gpu_product_sentiments") in ("upstream_failed", "skipped", None)
    assert task_states.get("generate_gpu_product_summaries") in ("upstream_failed", "skipped", None)

def test_dag_parallel_tasks_independent(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Sentiment and llm_summary run independently after ingest succeeds."""
    # Make sentiment fail but llm_summary succeed
    configure_mock_service(
        k8s_core_api, test_namespace, "sentiment-analysis-service",
        should_fail=True
    )

    dag_id = "product_laptop_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    # DAG fails because one task failed
    assert result["state"] == "failed"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("ingest_laptop_comments") == "success"
    assert task_states.get("analyze_laptop_product_sentiments") == "failed"
    # llm_summary should still succeed since it's independent
    assert task_states.get("generate_laptop_product_summaries") == "success"

def test_on_failure_callback_invoked(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """on_task_failure callback executes on task failure (check logs for error)."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ingestion-service",
        should_fail=True
    )

    dag_id = "product_headphone_pipeline"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    # Check that failure callback was invoked by looking at logs
    logs = exec_airflow_cmd(
        k8s_core_api, test_namespace, airflow_pod,
        ["airflow", "tasks", "logs", dag_id, "ingest_headphone_comments", run_id]
    )
    assert "failed" in logs.lower()

