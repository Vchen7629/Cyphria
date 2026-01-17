from kubernetes.client import V1ConfigMapVolumeSource
from kubernetes.client import V1EnvVar
from kubernetes.client import V1ContainerPort
from kubernetes.client import V1VolumeMount
from kubernetes.client import V1Container
from kubernetes.client import V1PodSpec
from kubernetes.client import V1ObjectMeta
from kubernetes.client import V1Pod
from kubernetes.client import CoreV1Api
from kubernetes.client import V1Volume
from kubernetes.client.exceptions import ApiException
from kubernetes.stream import stream
from tests.utils.pod_lifecycle import wait_for_pod_ready
import textwrap
import time
import json

MOCK_SERVICE_IMAGE = "python:3.13-alpine"

def create_mock_service_script() -> str:
    """Python script for mock HTTP service with runtime configuration."""
    return textwrap.dedent("""
        import os
        import json
        import time
        from http.server import HTTPServer, BaseHTTPRequestHandler

        config = {
            "response_status": os.environ.get("RESPONSE_STATUS", "completed"),
            "response_delay": float(os.environ.get("RESPONSE_DELAY", "0")),
            "should_fail": os.environ.get("SHOULD_FAIL", "false").lower() == "true",
        }

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, format, *args):
                pass

            def do_POST(self):
                if self.path == "/_config":
                    content_length = int(self.headers.get("Content-Length", 0))
                    body = self.rfile.read(content_length).decode()
                    config.update(json.loads(body))
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"status": "ok"}')
                    return

                if config["response_delay"] > 0:
                    time.sleep(config["response_delay"])

                if config["should_fail"]:
                    self.send_response(500)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Internal Server Error"}).encode())
                    return

                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"status": config["response_status"]}).encode())

            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"health": "ok"}).encode())

        if __name__ == "__main__":
            server = HTTPServer(("0.0.0.0", 8000), Handler)
            print("Mock service running on port 8000")
            server.serve_forever()
    """).strip()

def create_mock_service_pod(
    api: CoreV1Api,
    namespace: str,
    name: str,
    configmap_name: str,
    response_status: str = "completed",
    response_delay: float = 0,
    should_fail: bool = False
) -> V1Pod:
    """Create a mock service pod"""
    pod = V1Pod(
        metadata=V1ObjectMeta(name=name, labels={"app": name}),
        spec=V1PodSpec(
            containers=[
                V1Container(
                    name="mock-service",
                    image=MOCK_SERVICE_IMAGE,
                    command=["python", "/scripts/server.py"],
                    ports=[V1ContainerPort(container_port=8000)],
                    volume_mounts=[
                        V1VolumeMount(name="script", mount_path="/scripts")
                    ],
                    env=[
                        V1EnvVar(name="RESPONSE_STATUS", value=response_status),
                        V1EnvVar(name="RESPONSE_DELAY", value=str(response_delay)),
                        V1EnvVar(name="SHOULD_FAIL", value=str(should_fail).lower())
                    ],
                )
            ],
            volumes=[
                V1Volume(
                    name="script",
                    config_map=V1ConfigMapVolumeSource(name=configmap_name)
                )
            ],
        ),
    )
    return api.create_namespaced_pod(namespace=namespace, body=pod)

def configure_mock_service(
    api: CoreV1Api,
    namespace: str,
    pod_name: str,
    response_status: str = "completed",
    response_delay: float = 0,
    should_fail: bool = False,
) -> None:
    """Configure mock service behavior via HTTP endpoint (no pod restart needed)."""
    config = json.dumps({
        "response_status": response_status,
        "response_delay": response_delay,
        "should_fail": should_fail,
    })
    # Use Python's urllib since it's available in the alpine image
    cmd = [
        "python", "-c",
        f"import urllib.request; "
        f"urllib.request.urlopen(urllib.request.Request("
        f"'http://localhost:8000/_config', "
        f"data=b'{config}', "
        f"headers={{'Content-Type': 'application/json'}}))"
    ]
    stream(
        api.connect_get_namespaced_pod_exec,
        name=pod_name,
        namespace=namespace,
        command=cmd,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
    )

def replace_mock_service(
    api: CoreV1Api,
    namespace: str,
    name: str,
    configmap_name: str,
    response_status: str = "completed",
    response_delay: float = 0,
    should_fail: bool = False,
) -> None:
    """Delete and recreate a mock service with new configuration."""
    # Delete the pod if it exists
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

    create_mock_service_pod(
        api, namespace, name, configmap_name,
        response_status=response_status,
        response_delay=response_delay,
        should_fail=should_fail,
    )
    assert wait_for_pod_ready(api, namespace, name, timeout=60)