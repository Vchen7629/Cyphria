from airflow.sdk import Connection
from src.config.settings import Settings

settings = Settings()

llm_summary_service_conn = Connection(
    conn_id="llm_summary_service",
    conn_type="http",
    host="llm_summary_service.data-pipeline.svc.cluster.local",
    port=settings.LLM_SUMMARY_SVC_PORT,
    description="Connection for the Airflow DAG to connect to the llm summarization FastAPI service",
)