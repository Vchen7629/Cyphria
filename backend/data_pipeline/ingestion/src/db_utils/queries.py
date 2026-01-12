from datetime import datetime
from typing import Any
import psycopg

def batch_insert_raw_comments(conn: psycopg.Connection, comments: list[dict[str, Any]]) -> None:
    """
    Batch insert multiple raw comments to the bronze layer for better performance.

    Args:
        conn: psycopg3 database connection
        comments: list of comment dictionaries with keys:
            - comment_id (str)
            - post_id (str)
            - comment_body (str)
            - detected_products (list[str])
            - subreddit (str)
            - author (str)
            - score (int)
            - created_utc (datetime)
            - category (str)

    Example:
        comments = [
            {
                'comment_id': 'abc123',
                'post_id': 'xyz789',
                'comment_body': 'Great GPU!',
                'detected_products': ['NVIDIA RTX 4090'],
                'subreddit': 'nvidia',
                'author': 'user123',
                'score': 42,
                'created_utc': datetime.now(),
                'category': 'GPU'
            }
        ]
        batch_insert_raw_comments(conn, comments)
    """
    if not comments:
        return

    query = """
        INSERT INTO raw_comments (
            comment_id,
            post_id,
            comment_body,
            detected_products,
            subreddit,
            author,
            score,
            created_utc,
            category,
            sentiment_processed
        ) VALUES (
            %(comment_id)s,
            %(post_id)s,
            %(comment_body)s,
            %(detected_products)s,
            %(subreddit)s,
            %(author)s,
            %(score)s,
            %(created_utc)s,
            %(category)s,
            FALSE
        )
        ON CONFLICT (comment_id) DO NOTHING;
    """

    with conn.cursor() as cursor:
        cursor.executemany(query, comments)

    conn.commit()