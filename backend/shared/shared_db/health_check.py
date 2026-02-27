from shared_core.logger import StructuredLogger
from psycopg_pool import ConnectionPool

def check_db_health(db_pool: ConnectionPool, logger: StructuredLogger, event_type: str) -> None:
    """
    Verify database is reachable, closes the pool and 
    raises on failure so lifespan can abort startup cleanly
    """
    try:
        with db_pool.connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            logger.info(event_type=event_type, message="Database health check passed")
    except Exception as e:
        logger.error(
            event_type=event_type, message=f"Database health check failed: {e}"
        )
        db_pool.close()
        raise