from typing import Generator
from kubernetes.client import CoreV1Api
from kubernetes.client import V1ConfigMap
from kubernetes.client import V1ObjectMeta
from kubernetes.client.exceptions import ApiException
from tests.utils.services import configure_mock_service
from tests.utils.services import create_mock_service_pod
from tests.utils.services import create_mock_service_script
from tests.utils.kubernetes import wait_for_pod_ready
from tests.utils.kubernetes import create_service_for_pod
import pytest

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