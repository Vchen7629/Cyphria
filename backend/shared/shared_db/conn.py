from shared_core.logger import StructuredLogger
from psycopg_pool import ConnectionPool

def create_verified_connection_pool(
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    logger: StructuredLogger,
    service_name: str,
    min_size: int = 1, 
    max_size: int = 10
) -> ConnectionPool:
    """
    Create a PG connection pool using env variables and 
    verifies its available

    Args:
        min_size: Minimum connections in pool
        max_size: Maximum connections in pool

    Returns:
        ConnectionPool instance

    Raises:
        Exception and closes db_pool if db isnt reachable
    """
    
    conninfo = (
        f"host={db_host} "
        f"port={db_port} "
        f"dbname={db_name} "
        f"user={db_user} "
        f"password={db_password} "
    )
    event_type: str = f"{service_name} startup"

    logger.info(event_type=event_type, message="Creating database connection pool")
    db_pool = ConnectionPool(conninfo=conninfo, min_size=min_size, max_size=max_size, open=True)

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

    return db_pool
