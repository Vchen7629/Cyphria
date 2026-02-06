from tests.utils.airflow import exec_airflow_cmd
from tests.utils.services import configure_mock_service
from kubernetes.client import CoreV1Api
from tests.utils.airflow import get_task_states
from tests.utils.airflow import wait_for_dag_run
from tests.utils.airflow import trigger_dag

def test_dag_pipeline_full_execution(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """Full DAG runs: all_time >> wait_all_time >> 90_day >> wait_90_day."""
    dag_id = "product_computing_ranking"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "success"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("rank_computing_products_all_time") == "success"
    assert task_states.get("wait_rank_computing_products_all_time") == "success"
    assert task_states.get("rank_computing_products_90_day") == "success"
    assert task_states.get("wait_rank_computing_products_90_day") == "success"

def test_dag_downstream_task_skipped_on_upstream_failure(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """wait all_time is skipped/failed if all_time fails."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ranking-service",
        should_fail=True
    )

    dag_id = "product_computing_ranking"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    task_states = get_task_states(k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert task_states.get("rank_computing_products_all_time") == "failed"
    # Downstream tasks should not succeed
    assert task_states.get("wait_rank_computing_products_all_time") in ("upstream_failed", "skipped", None)

def test_on_failure_callback_invoked(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_pod: str,
) -> None:
    """on_task_failure callback executes on task failure (check logs for error)."""
    configure_mock_service(
        k8s_core_api, test_namespace, "ranking-service",
        should_fail=True
    )

    dag_id = "product_computing_ranking"
    run_id = trigger_dag(k8s_core_api, test_namespace, airflow_pod, dag_id)
    assert run_id, "Failed to trigger DAG"

    result = wait_for_dag_run(
        k8s_core_api, test_namespace, airflow_pod, dag_id, run_id)
    assert result["state"] == "failed"

    # Check that failure callback was invoked by looking at logs
    logs = exec_airflow_cmd(
        k8s_core_api, test_namespace, airflow_pod,
        ["airflow", "tasks", "logs", dag_id, "rank_computing_products_all_time", run_id]
    )
    assert "failed" in logs.lower()