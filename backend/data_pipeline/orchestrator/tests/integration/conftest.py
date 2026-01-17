from kubernetes.client import V1Container
from kubernetes.client import V1PodSpec
from kubernetes.client import V1Pod
from kubernetes.client import V1ContainerPort
from kubernetes.client import V1ConfigMap
from kubernetes.client import V1Volume
from kubernetes.client import V1VolumeMount
from kubernetes.client import V1ConfigMapVolumeSource
from kubernetes.client import V1EnvVar
from kubernetes.client.exceptions import ApiException
from kubernetes.client import V1ObjectMeta
from kubernetes.client import V1Namespace
from kubernetes.client import AppsV1Api
from kubernetes.client import CoreV1Api
from testcontainers.k3s import K3SContainer
from kubernetes import client, config
from pathlib import Path
from tests.utils.mock_service import create_mock_service_pod
from tests.utils.mock_service import create_mock_service_script
from tests.utils.mock_service import configure_mock_service
from tests.utils.pod_lifecycle import wait_for_pod_ready
from tests.utils.pod_lifecycle import create_service_for_pod
from typing import Generator
import pytest
import yaml
import time

TEST_NAMESPACE = "airflow-integration-test"
DAGS_PATH = Path(__file__).parent.parent.parent / "src" / "dags"
MOCK_SERVICE_IMAGE = "python:3.13-alpine"
SRC_PATH = Path(__file__).parent.parent.parent / "src"

@pytest.fixture(scope="session")
def k3s_cluster() -> Generator[K3SContainer, None, None]:
    """Spin up k3s cluster for testing"""
    with K3SContainer(image="rancher/k3s:v1.31.6-k3s1", enable_cgroup_mount=False) as k3s:
        kubeconfig = k3s.config_yaml()
        config.load_kube_config_from_dict(yaml.safe_load(kubeconfig))
        yield k3s
    
@pytest.fixture(scope="session")
def k8s_core_api(k3s_cluster: K3SContainer) -> CoreV1Api:
    """Return Kubernetes CoreV1Api client."""
    return client.CoreV1Api()

@pytest.fixture(scope="session")
def k8s_apps_api(k3s_cluster: K3SContainer) -> AppsV1Api:
    """Return Kubernetes AppsV1Api client."""
    return client.AppsV1Api()

@pytest.fixture(scope="session")
def test_namespace(k8s_core_api: CoreV1Api) -> Generator[str, None, None]:
    """Create and cleanup test namespace"""
    namespace = V1Namespace(metadata=V1ObjectMeta(name=TEST_NAMESPACE))

    try:
        k8s_core_api.create_namespace(body=namespace)
    except ApiException as e:
        if e.status != 409: # Ignore if it already exists
            raise
    
    yield TEST_NAMESPACE

    # cleanup code
    try:
        k8s_core_api.delete_namespace(name=TEST_NAMESPACE)
    except ApiException:
        pass # ignore any cleanup errors

@pytest.fixture(scope="session")
def mock_service_configmap(k8s_core_api: CoreV1Api, test_namespace: str) -> Generator[str, None, None]:
    """Create ConfigMap with mock service script"""
    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name="mock-service-script"),
        data={"server.py": create_mock_service_script()}
    )

    try:
        k8s_core_api.create_namespaced_config_map(
            namespace=test_namespace, body=configmap
        )
    except ApiException as e:
        if e.status != 409:
            raise

    yield "mock-service-script"

@pytest.fixture(scope="session")
def mock_services(k8s_core_api: CoreV1Api, test_namespace: str, mock_service_configmap: str) -> Generator[dict[str, int], None, None]:
    """Deploy mock services for ingestion, sentiment, llm-summary, ranking"""
    services = {
        "ingestion-service": 8000,
        "sentiment-analysis-service": 8000,
        "llm-summary-service": 8000,
        "ranking-service": 8000
    }

    for svc_name, port in services.items():
        try:
            create_mock_service_pod(
                k8s_core_api,
                test_namespace,
                svc_name,
                mock_service_configmap,
            )
            create_service_for_pod(k8s_core_api, test_namespace, svc_name, port)
        except ApiException as e:
            if e.status != 409:
                raise
    
    for svc_name in services:
        assert wait_for_pod_ready(k8s_core_api, test_namespace, svc_name), f"Pod {svc_name} failed to start"

    yield services

@pytest.fixture(scope="session")
def airflow_dags_configmap(k8s_core_api: CoreV1Api, test_namespace: str) -> Generator[str, None, None]:
    """Create ConfigMap with DAG files."""
    dag_files = {".airflowignore": ".*\n__pycache__\n"}
    for dag_file in DAGS_PATH.glob("*.py"):
        dag_files[dag_file.name] = dag_file.read_text()

    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name="airflow-dags"),
        data=dag_files,
    )
    try:
        k8s_core_api.create_namespaced_config_map(
            namespace=test_namespace, body=configmap
        )
    except ApiException as e:
        if e.status != 409:
            raise

    yield "airflow-dags"

@pytest.fixture(scope="session")
def airflow_config_configmap(k8s_core_api: CoreV1Api, test_namespace: str) -> Generator[str, None, None]:
    """Create ConfigMap with src/config modules."""
    config_path = SRC_PATH / "config"
    config_files = {"__init__.py": ""}
    for config_file in config_path.glob("*.py"):
        config_files[config_file.name] = config_file.read_text()

    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name="airflow-config"),
        data=config_files,
    )
    try:
        k8s_core_api.create_namespaced_config_map(
            namespace=test_namespace, body=configmap
        )
    except ApiException as e:
        if e.status != 409:
            raise

    yield "airflow-config"

@pytest.fixture(scope="session")
def airflow_utils_configmap(k8s_core_api: CoreV1Api, test_namespace: str) -> Generator[str, None, None]:
    """Create ConfigMap with src/utils modules."""
    utils_path = SRC_PATH / "utils"
    utils_files = {"__init__.py": ""}
    for utils_file in utils_path.glob("*.py"):
        utils_files[utils_file.name] = utils_file.read_text()

    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name="airflow-utils"),
        data=utils_files,
    )
    try:
        k8s_core_api.create_namespaced_config_map(
            namespace=test_namespace, body=configmap
        )
    except ApiException as e:
        if e.status != 409:
            raise

    yield "airflow-utils"

@pytest.fixture(scope="session")
def airflow_src_init_configmap(k8s_core_api: CoreV1Api, test_namespace: str) -> Generator[str, None, None]:
    """Create ConfigMap with src/__init__.py."""
    configmap = V1ConfigMap(
        metadata=V1ObjectMeta(name="airflow-src-init"),
        data={"__init__.py": ""},
    )
    try:
        k8s_core_api.create_namespaced_config_map(
            namespace=test_namespace, body=configmap
        )
    except ApiException as e:
        if e.status != 409:
            raise

    yield "airflow-src-init"

@pytest.fixture(scope="session")
def airflow_pod(
    k8s_core_api: CoreV1Api,
    test_namespace: str,
    airflow_dags_configmap: str,
    airflow_config_configmap: str,
    airflow_utils_configmap: str,
    airflow_src_init_configmap: str,
    mock_services: dict[str, int],
) -> Generator[str, None, None]:
    """Deploy Airflow standalone pod for testing."""
    pod = V1Pod(
        metadata=V1ObjectMeta(name="airflow", labels={"app": "airflow"}),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="airflow",
                    image="apache/airflow:3.0.1-python3.12",
                    command=["sh", "-c", "pip install pydantic-settings && airflow standalone"],
                    ports=[V1ContainerPort(container_port=8080)],
                    volume_mounts=[
                        V1VolumeMount(name="dags", mount_path="/opt/airflow/dags"),
                        V1VolumeMount(name="src-init", mount_path="/opt/airflow/dags/src"),
                        V1VolumeMount(name="config", mount_path="/opt/airflow/dags/src/config"),
                        V1VolumeMount(name="utils", mount_path="/opt/airflow/dags/src/utils"),
                    ],
                    env=[
                        V1EnvVar(name="EXECUTION_TIMEOUT", value="10s"),
                        V1EnvVar(name="AIRFLOW__CORE__LOAD_EXAMPLES", value="False"),
                        V1EnvVar(name="NUM_RETRIES", value="0"),
                        V1EnvVar(
                            name="AIRFLOW_CONN_INGESTION_SERVICE",
                            value=f"http://ingestion-service.{test_namespace}.svc.cluster.local:8000",
                        ),
                        V1EnvVar(
                            name="AIRFLOW_CONN_SENTIMENT_ANALYSIS_SERVICE",
                            value=f"http://sentiment-analysis-service.{test_namespace}.svc.cluster.local:8000",
                        ),
                        V1EnvVar(
                            name="AIRFLOW_CONN_LLM_SUMMARY_SERVICE",
                            value=f"http://llm-summary-service.{test_namespace}.svc.cluster.local:8000",
                        ),
                        V1EnvVar(
                            name="AIRFLOW_CONN_PRODUCT_RANKING_SERVICE",
                            value=f"http://ranking-service.{test_namespace}.svc.cluster.local:8000",
                        ),
                    ],
                )
            ],
            volumes=[
                V1Volume(
                    name="dags",
                    config_map=V1ConfigMapVolumeSource(name=airflow_dags_configmap),
                ),
                V1Volume(
                    name="src-init",
                    config_map=V1ConfigMapVolumeSource(name=airflow_src_init_configmap),
                ),
                V1Volume(
                    name="config",
                    config_map=V1ConfigMapVolumeSource(name=airflow_config_configmap),
                ),
                V1Volume(
                    name="utils",
                    config_map=V1ConfigMapVolumeSource(name=airflow_utils_configmap),
                ),
            ],
        ),
    )

    try:
        k8s_core_api.create_namespaced_pod(namespace=test_namespace, body=pod)
    except ApiException as e:
        if e.status != 409:
            raise

    try:
        create_service_for_pod(k8s_core_api, test_namespace, "airflow", port=8080)
    except ApiException as e:
        if e.status != 409:
            raise

    assert wait_for_pod_ready(k8s_core_api, test_namespace, "airflow", timeout=180), "Airflow pod failed to start"

    # Wait for Airflow to initialize
    time.sleep(10)

    yield "airflow"

@pytest.fixture(autouse=True)
def reset_mock_services(k8s_core_api: CoreV1Api, test_namespace: str):
    """Reset all mock services to default state after each test"""
    MOCK_SERVICE_NAMES = ["ingestion-service", "sentiment-analysis-service", "llm-summary-service", "ranking-service"]

    yield
    for svc_name in MOCK_SERVICE_NAMES:
        try:
            configure_mock_service(k8s_core_api, test_namespace, svc_name)
        except Exception:
            pass