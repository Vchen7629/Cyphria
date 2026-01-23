from typing import Any
from src.db.queries import upsert_llm_summaries
import psycopg

def test_insert_single_product_summary(
    db_connection: psycopg.Connection, 
    single_product_summary: dict[str, Any]
) -> None:
    """Inserting product summary for a product that doesnt exist in the db should work"""
    upsert_success = upsert_llm_summaries(
        db_conn=db_connection, 
        product_name="rtx 4090", 
        tldr="tldr :)", 
        time_window="all_time",
        model_used="chatgpt-5.1"
    )

    assert upsert_success == True

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT tldr FROM product_summaries")
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == "tldr :)"

def test_upsert_single_product_summary(
    db_connection: psycopg.Connection, 
    single_product_summary: dict[str, Any]
) -> None:
    """Inserting product summary for the same product name will update the tldr and model used"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_summaries (
                product_name, tldr, time_window, model_used, generated_at
            ) VALUES (
                %(product_name)s, %(tldr)s, %(time_window)s, %(model_used)s, NOW()
            )
        """, single_product_summary)

    upsert_success = upsert_llm_summaries(
        db_conn=db_connection, 
        product_name="rtx 4090", 
        tldr="new tldr :)", 
        time_window="all_time",
        model_used="chatgpt-5.1"
    )

    assert upsert_success == True

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT tldr FROM product_summaries")
        result = cursor.fetchone()

        assert result is not None
        assert result[0] == "new tldr :)"

def test_different_time_windows(
    db_connection: psycopg.Connection, 
    single_product_summary: dict[str, Any]
) -> None:
    """Inserting product summary for the same product name but different time window will not upsert"""
    with db_connection.cursor() as cursor:
        cursor.execute("""
            INSERT INTO product_summaries (
                product_name, tldr, time_window, model_used, generated_at
            ) VALUES (
                %(product_name)s, %(tldr)s, %(time_window)s, %(model_used)s, NOW()
            )
        """, single_product_summary)

    upsert_success = upsert_llm_summaries(
        db_conn=db_connection, 
        product_name="rtx 4090", 
        tldr="new tldr :)", 
        time_window="90d",
        model_used="chatgpt-5.1"
    )

    assert upsert_success == True

    with db_connection.cursor() as cursor:
        cursor.execute("SELECT tldr, time_window FROM product_summaries")
        result = cursor.fetchall()

        assert result is not None
        assert result[0][0] == "rtx 4090 tldr"
        assert result[0][1] == "all_time"
        assert result[1][0] == "new tldr :)"
        assert result[1][1] == "90d"



