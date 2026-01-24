from typing import Generator
from kubernetes import client
from kubernetes import config
from kubernetes.client import AppsV1Api
from kubernetes.client import CoreV1Api
from kubernetes.client import V1Namespace
from kubernetes.client import V1ObjectMeta
from kubernetes.client.exceptions import ApiException
from testcontainers.k3s import K3SContainer
import yaml
import pytest

TEST_NAMESPACE = "airflow-integration-test"

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
