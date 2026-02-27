from psycopg_pool import ConnectionPool

def create_connection_pool(
    db_host: str,
    db_port: int,
    db_name: str,
    db_user: str,
    db_password: str,
    min_size: int = 1, 
    max_size: int = 10
) -> ConnectionPool:
    """
    Create a PG connection pool using env variables

    Args:
        min_size: Minimum connections in pool
        max_size: Maximum connections in pool

    Returns:
        ConnectionPool instance
    """
    
    conninfo = (
        f"host={db_host} "
        f"port={db_port} "
        f"dbname={db_name} "
        f"user={db_user} "
        f"password={db_password} "
    )

    return ConnectionPool(conninfo=conninfo, min_size=min_size, max_size=max_size, open=True)
