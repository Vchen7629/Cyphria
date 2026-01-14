from src.db_utils.queries import fetch_unprocessed_comments
from typing import Any
import pytest
import psycopg
from psycopg_pool import ConnectionPool

def test_connection_pool_creation(db_pool: ConnectionPool) -> None:
    """Connection pool should be created successfully and can acquire connections."""
    with db_pool.connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            assert result == (1,)

def test_connection_failure_handling() -> None:
    """Connection failures with invalid connection string should be handled."""
    invalid_conninfo = "host=invalid_host port=9999 dbname=invalid user=invalid password=invalid"

    with pytest.raises(psycopg.OperationalError):
        conn = psycopg.connect(invalid_conninfo, connect_timeout=1)
        conn.close()

def test_pool_multiple_connections(db_pool: ConnectionPool) -> None:
    """Connection pool should handle multiple concurrent connections."""
    connections = []

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

def test_lost_connection_during_operation(db_connection: psycopg.Connection, single_comment: dict[str, Any]) -> None:
    """Losing connection during a database operation should raise Operational Error"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products,
                subreddit, author, score, created_utc, category, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(category)s, FALSE
            )
        """, single_comment)

    db_connection.commit()

    # simulate connection loss
    db_connection.close()

    with pytest.raises(psycopg.OperationalError):
        fetch_unprocessed_comments(db_connection, category='GPU', batch_size=10)

