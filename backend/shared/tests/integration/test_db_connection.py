from typing import Any
from psycopg_pool import ConnectionPool
import psycopg
import pytest

def test_connection_pool_creation(db_pool: ConnectionPool) -> None:
    """Connection pool should be created successfully and can acquire connections."""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result == (1,)


def test_connection_failure_handling() -> None:
    """Test handling of connection failures with invalid connection string."""
    invalid_conninfo = "host=invalid_host port=9999 dbname=invalid user=invalid password=invalid"

    with pytest.raises(psycopg.OperationalError):
        conn = psycopg.connect(invalid_conninfo, connect_timeout=1)
        conn.close()


def test_pool_multiple_connections(db_pool: ConnectionPool) -> None:
    """Test that connection pool can handle multiple concurrent connections."""
    connections: list[Any] = []

    try:
        # Acquire multiple connections
        for _ in range(3):
            conn = db_pool.getconn()
            connections.append(conn)

            # Test each connection works
            with conn.cursor() as cursor:
                cursor.execute("SELECT 1;")
                result = cursor.fetchone()
                assert result == (1,)
    finally:
        # Return all connections to pool
        for conn in connections:
            db_pool.putconn(conn)

def test_connection_pool_exhaustion(db_pool: ConnectionPool) -> None:
    """
    Trying to get one more connection when connection
    pool is exhausted should timeout
    """
    connections = []
    try:
        for _ in range(5):
            conn = db_pool.getconn(timeout=1)
            connections.append(conn)

        with pytest.raises(Exception):
            db_pool.getconn(timeout=1)
    finally:
        for conn in connections:
            db_pool.putconn(conn)