from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker
from tests.integration.conftest import FastAPITestClient
import pytest

@pytest.mark.asyncio
async def test_time_window_90_day(fastapi_client: FastAPITestClient, seed_raw_comments: None) -> None:
    """top_comments endpoint should return comments with 90 day time window ordered by score."""
    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    # Should return 3 comments (within 90d and sentiment_processed=true)
    assert len(comments) == 3

    # Should be ordered by score descending
    assert comments[0]["score"] == 150
    assert comments[1]["score"] == 100
    assert comments[2]["score"] == 75

@pytest.mark.asyncio
async def test_time_window_all_time(fastapi_client: FastAPITestClient, seed_raw_comments: None) -> None:
    """top_comments endpoint with all_time should include older comments."""
    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 4

    # Should be ordered by score descending - comment_4 has highest score (200)
    assert comments[0]["score"] == 200

@pytest.mark.asyncio
async def test_product_name_case_insensitive(fastapi_client: FastAPITestClient, seed_raw_comments: None) -> None:
    """top_comments endpoint sql query should be case insensitive for both product name"""
    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "NVIDIA RTX 4090", "time_window": "all_time"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 4

    # Should be ordered by score descending - comment_4 has highest score (200)
    assert comments[0]["score"] == 200

@pytest.mark.asyncio
async def test_no_comments(fastapi_client: FastAPITestClient) -> None:
    """top_comments should return empty list for product with no comments."""
    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "intel arc a770", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["top_comments"] == []

@pytest.mark.asyncio
async def test_product_name_not_found(fastapi_client: FastAPITestClient, seed_raw_comments: None) -> None:
    """top_comments endpoint should return empty list for unknown product."""
    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nonexistent product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["top_comments"] == []


@pytest.mark.asyncio
async def test_missing_params(fastapi_client: FastAPITestClient) -> None:
    """top_comments endpoint should return 422 when required params are missing."""
    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"time_window": "90d"}
    )
    assert response.status_code == 422

    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nvidia rtx 4090"}
    )
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_invalid_time_window(fastapi_client: FastAPITestClient, seed_raw_comments: None) -> None:
    """top_comments should return 422 if time_window is something other than all_time or 90d."""
    response_30d = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "30d"}
    )

    assert response_30d.status_code == 422

    response_7d = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "7d"}
    )

    assert response_7d.status_code == 422

    response_random_string = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "nvidia rtx 4090", "time_window": "asdasd"}
    )

    assert response_random_string.status_code == 422

@pytest.mark.asyncio
async def test_comments_all_unprocessed(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """top_comments should return empty list when all comments have sentiment_processed=false."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO raw_comments
                (comment_id, post_id, comment_body, detected_products, subreddit,
                 author, score, created_utc, category, sentiment_processed)
            VALUES
                ('unproc_1', 'post_1', 'Comment 1', ARRAY['amd rx 7800 xt'], 'amd', 'user1', 100, NOW() - INTERVAL '10 days', 'GPU', false),
                ('unproc_2', 'post_2', 'Comment 2', ARRAY['amd rx 7800 xt'], 'amd', 'user2', 80, NOW() - INTERVAL '20 days', 'GPU', false)
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "amd rx 7800 xt", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["top_comments"] == []


@pytest.mark.asyncio
async def test_comments_identical_scores(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """top_comments should handle comments with identical scores."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO raw_comments
                (comment_id, post_id, comment_body, detected_products, subreddit,
                 author, score, created_utc, category, sentiment_processed)
            VALUES
                ('tie_1', 'post_1', 'First comment', ARRAY['test product'], 'test', 'user1', 100, NOW() - INTERVAL '10 days', 'GPU', true),
                ('tie_2', 'post_2', 'Second comment', ARRAY['test product'], 'test', 'user2', 100, NOW() - INTERVAL '20 days', 'GPU', true),
                ('tie_3', 'post_3', 'Third comment', ARRAY['test product'], 'test', 'user3', 100, NOW() - INTERVAL '30 days', 'GPU', true)
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "test product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 3
    # All should have score 100
    assert all(c["score"] == 100 for c in comments)

@pytest.mark.asyncio
async def test_more_than_five_comments_returns_only_five(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """top_comments should return only top 5 when there are more than 5 comments."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO raw_comments
                (comment_id, post_id, comment_body, detected_products, subreddit,
                 author, score, created_utc, category, sentiment_processed)
            VALUES
                ('seven_1', 'post_1', 'Comment 1', ARRAY['seven product'], 'test', 'user1', 70, NOW() - INTERVAL '10 days', 'GPU', true),
                ('seven_2', 'post_2', 'Comment 2', ARRAY['seven product'], 'test', 'user2', 60, NOW() - INTERVAL '20 days', 'GPU', true),
                ('seven_3', 'post_3', 'Comment 3', ARRAY['seven product'], 'test', 'user3', 50, NOW() - INTERVAL '30 days', 'GPU', true),
                ('seven_4', 'post_4', 'Comment 4', ARRAY['seven product'], 'test', 'user4', 40, NOW() - INTERVAL '40 days', 'GPU', true),
                ('seven_5', 'post_5', 'Comment 5', ARRAY['seven product'], 'test', 'user5', 30, NOW() - INTERVAL '50 days', 'GPU', true),
                ('seven_6', 'post_6', 'Comment 6', ARRAY['seven product'], 'test', 'user6', 20, NOW() - INTERVAL '60 days', 'GPU', true),
                ('seven_7', 'post_7', 'Comment 7', ARRAY['seven product'], 'test', 'user7', 10, NOW() - INTERVAL '70 days', 'GPU', true)
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "seven product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 5
    # Should be ordered by score descending
    assert comments[0]["score"] == 70
    assert comments[4]["score"] == 30
    # Comments with scores 20 and 10 should be excluded
    scores = [c["score"] for c in comments]
    assert 20 not in scores
    assert 10 not in scores


@pytest.mark.asyncio
async def test_time_window_90_day_boundary(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """top_comments should include comments within 90 days but exclude older."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO raw_comments
                (comment_id, post_id, comment_body, detected_products, subreddit,
                 author, score, created_utc, category, sentiment_processed)
            VALUES
                ('boundary_inside', 'post_1', 'Well inside 90 days', ARRAY['boundary product'], 'test', 'user1', 80, NOW() - INTERVAL '89 days', 'GPU', true),
                ('boundary_edge', 'post_2', 'Just inside 90 days', ARRAY['boundary product'], 'test', 'user2', 100, NOW() - INTERVAL '89 days 23 hours 59 minutes', 'GPU', true),
                ('boundary_outside', 'post_3', 'Just outside 90 days', ARRAY['boundary product'], 'test', 'user3', 60, NOW() - INTERVAL '90 days 1 hour', 'GPU', true)
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "boundary product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    # Should include comments inside 90 days, exclude outside
    assert len(comments) == 2
    scores = [c["score"] for c in comments]
    assert 100 in scores  # just inside 90 days - included
    assert 80 in scores   # before 90 days - included
    assert 60 not in scores  # after 90 days - excluded

@pytest.mark.asyncio
async def test_comments_negative_and_zero_scores(
    fastapi_client: FastAPITestClient,
    test_async_session: async_sessionmaker[AsyncSession],
    clean_tables: None
) -> None:
    """top_comments should include and correctly order negative and zero score comments."""
    async with test_async_session() as session:
        await session.execute(text("""
            INSERT INTO raw_comments
                (comment_id, post_id, comment_body, detected_products, subreddit,
                 author, score, created_utc, category, sentiment_processed)
            VALUES
                ('neg_1', 'post_1', 'Positive score', ARRAY['score product'], 'test', 'user1', 50, NOW() - INTERVAL '10 days', 'GPU', true),
                ('neg_2', 'post_2', 'Zero score', ARRAY['score product'], 'test', 'user2', 0, NOW() - INTERVAL '20 days', 'GPU', true),
                ('neg_3', 'post_3', 'Negative score', ARRAY['score product'], 'test', 'user3', -10, NOW() - INTERVAL '30 days', 'GPU', true),
                ('neg_4', 'post_4', 'Very negative', ARRAY['score product'], 'test', 'user4', -50, NOW() - INTERVAL '40 days', 'GPU', true)
        """))
        await session.commit()

    response = await fastapi_client.client.get(
        "/api/v1/product/top_comments",
        params={"product_name": "score product", "time_window": "90d"}
    )

    assert response.status_code == 200
    data = response.json()
    comments = data["top_comments"]

    assert len(comments) == 4
    # Should be ordered by score descending
    assert comments[0]["score"] == 50
    assert comments[1]["score"] == 0
    assert comments[2]["score"] == -10
    assert comments[3]["score"] == -50