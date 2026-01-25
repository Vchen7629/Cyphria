import pytest
from typing import Any
from datetime import datetime
from datetime import timezone
from src.db_utils.queries import fetch_unprocessed_comments
import psycopg

def test_fetch_single_comment(db_connection: psycopg.Connection, single_comment: dict[str, Any]) -> None:
    """Fetching a single comment from the database should return it."""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, single_comment)

    result = fetch_unprocessed_comments(db_connection, product_topic='GPU' ,batch_size=1)

    assert len(result) == 1
    assert result[0].comment_id == 'test_comment_1'
    assert result[0].comment_body == 'This is a test comment about RTX 4090'
    assert result[0].detected_products == ['rtx 4090']
    assert result[0].created_utc == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 

def test_fetch_no_unprocessed_comments(db_connection: psycopg.Connection, single_comment: dict[str, Any]) -> None:
    """Already processed comments should not be fetched"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, TRUE
            )
        """, single_comment)

    result = fetch_unprocessed_comments(db_connection, product_topic='nvidia', batch_size=1)

    assert len(result) == 0
    assert result == []

def test_fetch_empty_database(db_connection: psycopg.Connection) -> None:
    """Fetching from an empty database should return empty list"""
    result = fetch_unprocessed_comments(db_connection, product_topic='Any', batch_size=100)

    assert len(result) == 0
    assert result == []

def test_fetch_respects_batch_size(db_connection: psycopg.Connection) -> None:
    """Batch size limit should be respected when more comments exist"""
    comments = [
        {
            'comment_id': f'comment_{i}',
            'post_id': f'post_{i}',
            'comment_body': 'This is a test comment about RTX 4090',
            'detected_products': ['rtx 4090'],
            'subreddit': 'nvidia',
            'author': 'test_user',
            'score': i,
            'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            'product_topic': 'GPU',
        }
        for i in range(10)
    ]
    
    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed
                ) VALUES (
                    %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                    %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
                )
            """, comment)
    
    db_connection.commit()

    result = fetch_unprocessed_comments(db_connection, product_topic='GPU', batch_size=5)

    assert len(result) == 5

def test_fetch_orders_by_created_utc_asc(db_connection: psycopg.Connection) -> None:
    """Comments should be fetching in chronological order (oldest first)"""
    comments = [
        {
            'comment_id': 'newest',
            'created_utc': datetime(2024, 1, 3, 0, 0, 0, tzinfo=timezone.utc),
        },
        {
            'comment_id': 'oldest',
            'created_utc': datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc),
        },
        {
            'comment_id': 'middle',
            'created_utc': datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc),
        }
    ]

    with db_connection.cursor() as cursor:
        for comment in comments:
            cursor.execute("""
                INSERT INTO raw_comments (
                    comment_id, post_id, comment_body, detected_products, subreddit,
                    author, score, created_utc, product_topic, sentiment_processed
                ) VALUES (
                    %(comment_id)s, 'post', 'body', ARRAY['product'], 'subreddit', 
                    'author', 1, %(created_utc)s, 'cat', FALSE
                )
            """, comment)
    
    db_connection.commit()

    result = fetch_unprocessed_comments(db_connection, product_topic='cat', batch_size=10)

    assert len(result) == 3
    assert result[0].comment_id == 'oldest'
    assert result[1].comment_id == 'middle'
    assert result[2].comment_id == 'newest'

def test_fetch_mixed_processed_unprocessed(db_connection: psycopg.Connection) -> None:
    """Only the unprocessed comments should be fetched when we have a mix of processed and unprocessed"""
    comments = [
        {'comment_id': 'unprocessed_1', 'sentiment_processed': False},
        {'comment_id': 'processed_1', 'sentiment_processed': True},
        {'comment_id': 'unprocessed_2', 'sentiment_processed': False},
        {'comment_id': 'processed_2', 'sentiment_processed': True}
    ]

    with db_connection.cursor() as cursor:
        for i, comment in enumerate(comments):
            cursor.execute("""                                                                        
                INSERT INTO raw_comments (                                                            
                    comment_id, post_id, comment_body, detected_products,                             
                    subreddit, author, score, created_utc, product_topic, sentiment_processed              
                ) VALUES (                                                                            
                    %(comment_id)s, 'post', 'body', ARRAY['product'],                                 
                    'sub', 'author', 1, %(created_utc)s, 'cat', %(sentiment_processed)s               
                )                                                                                     
            """, {                                                                                    
                'comment_id': comment['comment_id'],                                                  
                'sentiment_processed': comment['sentiment_processed'],                                
                'created_utc': datetime(2024, 1, 1, 12, i, 0, tzinfo=timezone.utc),                   
            })    

    db_connection.commit()      

    result = fetch_unprocessed_comments(db_connection, product_topic='cat', batch_size=10)

    assert len(result) == 2
    comment_ids = {r.comment_id for r in result}
    assert comment_ids == {'unprocessed_1', 'unprocessed_2'}

def test_fetch_empty_detected_products(db_connection: psycopg.Connection) -> None:
    """Comments with empty detected_products array should be handled properly"""
    comment = {
        'comment_id': 'no_products',
        'post_id': 'post_1',
        'comment_body': 'abcdefg',
        'detected_products': [], # type: ignore
        'subreddit': 'test',
        'author': 'user',
        'score': 5,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'product_topic': 'general'
    }

    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, comment)

    db_connection.commit()

    result = fetch_unprocessed_comments(db_connection, product_topic='general', batch_size=10)

    assert len(result) == 1
    assert result[0].comment_id == 'no_products'
    assert result[0].detected_products == []

def test_fetch_multiple_products(db_connection: psycopg.Connection) -> None:
    """Comments with multiple detected products should be returned"""
    comment = {
        'comment_id': 'multi_products',
        'post_id': 'post_1',
        'comment_body': 'abcdefg',
        'detected_products': ['rtx 4090', 'rtx 4080', 'rx 7900 xtx'],
        'subreddit': 'test',
        'author': 'user',
        'score': 5,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'product_topic': 'general'
    }

    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, comment)

    db_connection.commit()

    result = fetch_unprocessed_comments(db_connection, product_topic='general', batch_size=10)

    assert len(result) == 1
    assert result[0].comment_id == 'multi_products'
    assert len(result[0].detected_products) == 3
    assert set(result[0].detected_products) == {'rtx 4090', 'rtx 4080', 'rx 7900 xtx'}

def test_fetch_special_characters_in_comment_body(db_connection: psycopg.Connection) -> None:
    """Test handling of special characters, and unicode in comment body"""
    comment = {
        'comment_id': 'special chars',
        'post_id': 'post_1',
        'comment_body': 'RTX 4090 is fire! Best GPU ever \nMultiline\nWith émojis and ünïcödé',
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user',
        'score': 50,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'product_topic': 'GPU'
    }

    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, comment)

    db_connection.commit()

    result = fetch_unprocessed_comments(db_connection, product_topic='GPU', batch_size=10)

    assert len(result) == 1
    assert result[0].comment_id == 'special chars'
    assert 'émojis' in result[0].comment_body
    assert 'ünïcödé' in result[0].comment_body

def test_fetch_very_long_comment_body(db_connection: psycopg.Connection) -> None:
    """Long comment bodies should not cause issues"""
    long_text = "This is a very long comment. " * 1000
    comment = {
        'comment_id': 'long comment',
        'post_id': 'post_1',
        'comment_body': long_text + " RTX 4090 is mentioned here.",
        'detected_products': ['rtx 4090'],
        'subreddit': 'nvidia',
        'author': 'user',
        'score': 50,
        'created_utc': datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
        'product_topic': 'GPU'
    }

    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, comment)

    db_connection.commit()

    result = fetch_unprocessed_comments(db_connection, product_topic='GPU', batch_size=10)

    assert len(result) == 1
    assert result[0].comment_id == 'long comment'
    assert len(result[0].comment_body) > 29000
    assert 'RTX 4090 is mentioned here.' in result[0].comment_body

def test_fetch_wrong_product_topic(db_connection: psycopg.Connection, single_comment: dict[str, Any]) -> None:
    """Fetching a product_topic that doesnt exist shouldnt return anything"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, single_comment)

    result = fetch_unprocessed_comments(db_connection, product_topic="thisdoesntexist", batch_size=10)

    assert len(result) == 0
    assert result == []

@pytest.mark.parametrize(argnames="product_topic", argvalues=["gPu", "  gpu  "])
def test_valid_product_topic_params(
    product_topic: str,
    db_connection: psycopg.Connection, 
    single_comment: dict[str, Any]
) -> None:
    """Valid product topic params (case insensitive and whitespace) should still match"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO raw_comments (
                comment_id, post_id, comment_body, detected_products, subreddit,
                author, score, created_utc, product_topic, sentiment_processed
            ) VALUES (
                %(comment_id)s, %(post_id)s, %(comment_body)s, %(detected_products)s, %(subreddit)s, 
                %(author)s, %(score)s, %(created_utc)s, %(product_topic)s, FALSE
            )
        """, single_comment)

    result = fetch_unprocessed_comments(db_connection, product_topic, batch_size=10)

    assert len(result) == 1
    assert result[0].comment_id == 'test_comment_1'
    assert result[0].comment_body == 'This is a test comment about RTX 4090'
    assert result[0].detected_products == ['rtx 4090']
    assert result[0].created_utc == datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc) 
