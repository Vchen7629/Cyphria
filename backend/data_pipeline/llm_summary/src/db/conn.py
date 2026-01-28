from psycopg_pool import ConnectionPool
from src.core.settings_config import Settings


def create_connection_pool(min_size: int = 1, max_size: int = 10) -> ConnectionPool:
    """
    Create a PG connection pool using env variables

    Args:
        min_size: Minimum connections in pool
        max_size: Maximum connections in pool

    Returns:
        ConnectionPool instance
    """
    settings = Settings()

    conninfo = (
        f"host={settings.DB_HOST} "
        f"port={settings.DB_PORT} "
        f"dbname={settings.DB_NAME} "
        f"user={settings.DB_USER} "
        f"password={settings.DB_PASS} "
    )

    return ConnectionPool(conninfo=conninfo, min_size=min_size, max_size=max_size, open=True)
