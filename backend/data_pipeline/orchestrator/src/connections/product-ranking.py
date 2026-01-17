from airflow.sdk import Connection
from src.config.settings import Settings

settings = Settings()

product_ranking_service_conn = Connection(
    conn_id="product_ranking_service",
    conn_type="http",
    host="product_ranking_service.data-pipeline.svc.cluster.local",
    port=settings.RANKING_SVC_PORT,
    description="Connection for the Airflow DAG to connect to the product ranking FastAPI service",
)