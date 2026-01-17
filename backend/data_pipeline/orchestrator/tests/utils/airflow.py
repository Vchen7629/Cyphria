from kubernetes.client import CoreV1Api
from kubernetes.stream import stream
import time
import ast

def exec_airflow_cmd(api: CoreV1Api, namespace: str, pod: str, cmd: list[str]) -> str:
    """Execute airflow CLI command in the airflow pod."""
    return stream(
        api.connect_get_namespaced_pod_exec,
        name=pod,
        namespace=namespace,
        command=cmd,
        stderr=True,
        stdin=False,
        stdout=True,
        tty=False,
    )

def trigger_dag(api: CoreV1Api, namespace: str, pod: str, dag_id: str) -> str:
    """Trigger a DAG run and return the run_id."""
    # Wait for DAG to be loaded since scheduler needs time to parse
    for _ in range(6):
        resp = exec_airflow_cmd(api, namespace, pod, ["airflow", "dags", "list"])
        if dag_id in resp:
            break
        time.sleep(3)

    # Unpause DAG since DAGs are paused by default to trigger the dag
    exec_airflow_cmd(api, namespace, pod, ["airflow", "dags", "unpause", dag_id])

    resp = exec_airflow_cmd(
        api, namespace, pod,
        ["airflow", "dags", "trigger", dag_id, "--output", "json"]
    )
    try:
        data = ast.literal_eval(resp)
        return data[0]["dag_run_id"] if isinstance(data, list) else data["dag_run_id"]
    except (ValueError, SyntaxError, KeyError):
        if "dag_run_id=" in resp:
            return resp.split("dag_run_id=")[-1].split()[0]
        raise RuntimeError(f"Failed to trigger DAG '{dag_id}'. Response: {resp}")

def wait_for_dag_run(
    api: CoreV1Api,
    namespace: str,
    pod: str,
    dag_id: str,
    run_id: str,
    timeout: int = 180,
) -> dict:
    """Wait for DAG run to complete and return final state."""
    start = time.time()
    last_state = ""
    while time.time() - start < timeout:
        resp = exec_airflow_cmd(
            api, namespace, pod,
            ["airflow", "dags", "state", dag_id, run_id]
        )
        last_state = resp.strip().split()[-1]
        if last_state in ("success", "failed"):
            return {"state": last_state}
        time.sleep(2)
    return {"state": "timeout", "last_state": last_state}

def get_task_states(
    api: CoreV1Api, namespace: str, pod: str, dag_id: str, run_id: str
) -> dict[str, str]:
    """Get states of all tasks in a DAG run."""
    resp = exec_airflow_cmd(
        api, namespace, pod,
        ["airflow", "tasks", "states-for-dag-run", dag_id, run_id, "--output", "json"]
    )
    try:
        tasks = ast.literal_eval(resp)
        return {t["task_id"]: t["state"] for t in tasks}
    except (ValueError, SyntaxError, KeyError):
        return {}