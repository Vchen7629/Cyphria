import os
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
        f"host={settings.db_host} "
        f"port={settings.db_port} "
        f"dbname={settings.db_name} "
        f"user={settings.db_user} "
        f"password={settings.db_pass} "
    )

    return ConnectionPool(conninfo=conninfo, min_size=min_size, max_size=max_size)     