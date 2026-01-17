from airflow.sdk import Connection
from src.config.settings import Settings

settings = Settings()

sentiment_analysis_service_conn = Connection(
    conn_id="sentiment_analysis_service",
    conn_type="http",
    host="sentiment_analysis_service.data-pipeline.svc.cluster.local",
    port=settings.SENTIMENT_ANALYSIS_SVC_PORT,
    description="Connection for the Airflow DAG to connect to the sentiment analysis FastAPI service",
)