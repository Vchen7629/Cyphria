from kubernetes.client import CoreV1Api
from kubernetes.stream import stream
import time

def test_airflow_dags_loaded(k8s_core_api: CoreV1Api, test_namespace: str, airflow_pod: str) -> None:
    """DAGs should be loaded from configmap mounts and parsed by Airflow properly."""
    # Poll for DAGs to be loaded - scheduler needs time to parse them
    resp = ""
    max_attempts = 6
    for attempt in range(max_attempts):
        resp = stream(
            k8s_core_api.connect_get_namespaced_pod_exec,
            name=airflow_pod,
            namespace=test_namespace,
            command=["airflow", "dags", "list", "--output", "json"],
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False
        )

        if "product_gpu_pipeline" in resp:
            break

        time.sleep(10)

    expected_dags = [
        "product_gpu_pipeline",
        "product_laptop_pipeline",
        "product_headphone_pipeline",
        "product_gpu_ranking",
        "product_laptop_ranking",
        "product_headphone_ranking"
    ]

    for expected_dag in expected_dags:
        assert expected_dag in resp, f"DAG {expected_dag} not found in loaded DAGs"

    # No example DAGs should be loaded (LOAD_EXAMPLES=False)
    assert "example_" not in resp, "Example DAGs should not be loaded"
