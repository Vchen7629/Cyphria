from kubernetes.client import CoreV1Api
from tests.utils.services import configure_mock_service
from tests.utils.services import replace_mock_service
from tests.utils.kubernetes import delete_pod
from tests.utils.airflow import trigger_dag
from tests.utils.airflow import wait_for_dag_run
from tests.utils.airflow import exec_airflow_cmd

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

    dag_id = "product_computing_sentiment_analysis"
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

    dag_id = "product_computing_sentiment_analysis"
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

    dag_id = "product_computing_sentiment_analysis"
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

    dag_id = "product_computing_sentiment_analysis"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

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

    dag_id = "product_computing_sentiment_analysis"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    # Check that failure callback was invoked by looking at logs
    logs = exec_airflow_cmd(
        k8s_core_api, test_namespace, airflow_pod,
        ["airflow", "tasks", "logs", dag_id, "ingest_computing_comments", run_id]
    )
    assert "failed" in logs.lower()

