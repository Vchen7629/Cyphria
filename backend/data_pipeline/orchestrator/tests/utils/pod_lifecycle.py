from kubernetes.client import V1ServicePort
from kubernetes.client import V1ServiceSpec
from kubernetes.client import V1ObjectMeta
from kubernetes.client import V1Service
from kubernetes.client import CoreV1Api
from kubernetes.client.exceptions import ApiException
import time

def wait_for_pod_ready(api: CoreV1Api, namespace: str, pod_name: str, timeout: int = 180) -> bool:
    """Wait for the pod to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            pod = api.read_namespaced_pod(name=pod_name, namespace=namespace)
            if pod.status.phase == "Running" and pod.status.container_statuses:
                if all(cs.ready for cs in pod.status.container_statuses):
                    return True
        except ApiException:
            pass
        time.sleep(2)
    return False

def create_service_for_pod(api: CoreV1Api, namespace: str, name: str, port: int = 8000) -> V1Service:
    """Create kubernetes service for the pod"""
    service = V1Service(
        metadata=V1ObjectMeta(name=name),
        spec=V1ServiceSpec(
            selector={"app": name},
            ports=[V1ServicePort(port=port, target_port=8000)]
        ),
    )
    return api.create_namespaced_service(namespace=namespace, body=service)

def delete_pod(api: CoreV1Api, namespace: str, name: str) -> None:
    """Delete a kubernetes pod without recreating it."""
    try:
        api.delete_namespaced_pod(name=name, namespace=namespace)
    except ApiException as e:
        if e.status != 404:
            raise

    # Wait for pod to be fully deleted
    for _ in range(60):
        try:
            api.read_namespaced_pod(name=name, namespace=namespace)
            time.sleep(1)
        except ApiException as e:
            if e.status == 404:
                break
            raise