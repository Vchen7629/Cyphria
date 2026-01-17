from airflow.sdk import Connection
from src.config.settings import Settings

settings = Settings()

data_ingestion_service_conn = Connection(
    conn_id="ingestion_service",
    conn_type="http",
    host="ingestion-service.data-pipeline.svc.cluster.local",
    port=settings.DATA_INGESTION_SVC_PORT,
    description="Connection for the Airflow DAG to connect to the ingestion FastAPI service",
)