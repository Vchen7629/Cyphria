from typing import Any
from typing import Callable
import pytest
import json
from src.core.types import QueueMessage
from src.components.batch import batch
from queue import Queue

@pytest.fixture
def queue_message_factory() -> Callable[[str, str, list[str]], QueueMessage]:
    """
    Factory fixture for created QueueMessage instances with proper structure

    Returns:
        A factory function that creates QueueMessage objects
    """
    def _create_message(
        post_id: str,
        comment_body: str,
        detected_products: list[str],
        topic: str = "test-topic",
        partition: int = 0,
        offset: int = 0,
        subreddit: str = "popular",
        timestamp: str = "2026-01-11 00:51:17+00:00",
        score: int = 26,
        author: str = "me"
    ) -> QueueMessage:
        post_body = json.dumps({
            "comment_body": comment_body,
            "detected_products": detected_products
        })

        return QueueMessage(
            topic=topic,
            partition=partition,
            offset=offset,
            postID=post_id,
            postBody=post_body,
            subreddit=subreddit,
            timestamp=timestamp,
            score=score,
            author=author
        )

    return _create_message

def test_single_post_with_single_product(queue_message_factory: Any) -> None:
    """One post with one product """
    queue: Queue[QueueMessage] = Queue()

    msg = queue_message_factory(
        post_id="post1",
        comment_body="Great GPU the RTX 4090 is",
        detected_products=["RTX 4090"]
    )
    queue.put(msg)

    # Get one batch
    batch_gen = batch(queue, batch_size=1, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    assert len(post_id_mappings) == 1
    assert post_id_mappings[0][0:3] == ("post1", 0, 1)
    assert len(all_product_pairs) == 1
    assert all_product_pairs[0] == ("Great GPU the RTX 4090 is", "RTX 4090")
    assert len(curr_batch) == 1

def test_single_post_multiple_products(queue_message_factory: Any) -> None:
    queue: Queue[QueueMessage] = Queue()

    msg = queue_message_factory(
        post_id="post1",
        comment_body="RTX 4090 is faster than the RX 7900 XTX",
        detected_products=["RTX 4090", "RX 7900 XTX"]
    )
    queue.put(msg)

    batch_gen = batch(queue, batch_size=1, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    assert len(post_id_mappings) == 1
    assert post_id_mappings[0][0:3] == ("post1", 0, 2) # 2 products
    assert len(all_product_pairs) == 2
    assert all_product_pairs[0] == ("RTX 4090 is faster than the RX 7900 XTX", "RTX 4090")
    assert all_product_pairs[1] == ("RTX 4090 is faster than the RX 7900 XTX", "RX 7900 XTX")

def test_multiple_posts_single_product_each(queue_message_factory: Any) -> None:
    """Multiple posts, each with one product"""
    queue: Queue[QueueMessage] = Queue()

    queue.put(queue_message_factory("post1", "Great GPU", ["RTX 4090"]))
    queue.put(queue_message_factory("post2", "Love it", ["PS5"]))
    queue.put(queue_message_factory("post3", "Amazing", ["iPhone 15"]))

    batch_gen = batch(queue, batch_size=3, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    assert len(post_id_mappings) == 3
    assert post_id_mappings[0][0:3] == ("post1", 0, 1)
    assert post_id_mappings[1][0:3] == ("post2", 1, 2)
    assert post_id_mappings[2][0:3] == ("post3", 2, 3)
    assert all_product_pairs[0] == ("Great GPU", "RTX 4090")
    assert all_product_pairs[1] == ("Love it", "PS5")
    assert all_product_pairs[2] == ("Amazing", "iPhone 15")
    assert len(all_product_pairs) == 3

def test_multiple_posts_varying_products(queue_message_factory: Any) -> None:
    """Multiple posts with diff numbers of products"""
    queue: Queue[QueueMessage] = Queue()

    queue.put(queue_message_factory("post1", "RTX 4090 vs RX 7900", ["RTX 4090", "RX 7900 XTX"]))
    queue.put(queue_message_factory("post2", "PS5 is great", ["PS5"]))
    queue.put(queue_message_factory("post3", "iPhone 15, Galaxy S24, and Pixel 8", ["iPhone 15", "Galaxy S24", "Pixel 8"]))

    batch_gen = batch(queue, batch_size=3, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    assert len(post_id_mappings) == 3
    assert post_id_mappings[0][0:3] == ("post1", 0, 2)   # 2 products: indices 0-1
    assert post_id_mappings[1][0:3] == ("post2", 2, 3)   # 1 product: index 2
    assert post_id_mappings[2][0:3] == ("post3", 3, 6)   # 3 products: indices 3-5
    assert len(all_product_pairs) == 6
    assert all_product_pairs[0] == ("RTX 4090 vs RX 7900", "RTX 4090")                    # post1
    assert all_product_pairs[1] == ("RTX 4090 vs RX 7900", "RX 7900 XTX")                 # post1
    assert all_product_pairs[2] == ("PS5 is great", "PS5")                                # post2
    assert all_product_pairs[3] == ("iPhone 15, Galaxy S24, and Pixel 8", "iPhone 15")    # post3
    assert all_product_pairs[4] == ("iPhone 15, Galaxy S24, and Pixel 8", "Galaxy S24")   # post3
    assert all_product_pairs[5] == ("iPhone 15, Galaxy S24, and Pixel 8", "Pixel 8")      # post3

def test_post_with_no_products(queue_message_factory: Any) -> None:
    """Post with empty detected_products list"""
    queue: Queue[QueueMessage] = Queue()

    msg = queue_message_factory(
        post_id="post1",
        comment_body="Just a random comment",
        detected_products=[]
    )
    queue.put(msg)

    batch_gen = batch(queue, batch_size=1, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    assert len(post_id_mappings) == 1
    assert post_id_mappings[0][0:3] == ("post1", 0, 0)  # No products: start_idx == end_idx
    assert len(all_product_pairs) == 0
    assert len(curr_batch) == 1

def test_mixed_some_with_products_some_without(queue_message_factory: Any) -> None:
    """Mixed batch, some with products, some without"""
    queue: Queue[QueueMessage] = Queue()

    queue.put(queue_message_factory("post1", "Great GPU", ["RTX 4090"]))
    queue.put(queue_message_factory("post2", "Random comment", []))
    queue.put(queue_message_factory("post3", "Love these", ["PS5", "Xbox"]))
    queue.put(queue_message_factory("post4", "Another random", []))
    queue.put(queue_message_factory("post5", "Good phone", ["iPhone 15"]))

    batch_gen = batch(queue, batch_size=5, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    assert len(post_id_mappings) == 5
    assert post_id_mappings[0][0:3] == ("post1", 0, 1)   # 1 product
    assert post_id_mappings[1][0:3] == ("post2", 1, 1)   # 0 products (empty)
    assert post_id_mappings[2][0:3] == ("post3", 1, 3)   # 2 products
    assert post_id_mappings[3][0:3] == ("post4", 3, 3)   # 0 products (empty)
    assert post_id_mappings[4][0:3] == ("post5", 3, 4)   # 1 product
    assert len(all_product_pairs) == 4
    assert all_product_pairs[0] == ("Great GPU", "RTX 4090")
    assert all_product_pairs[1] == ("Love these", "PS5")
    assert all_product_pairs[2] == ("Love these", "Xbox")
    assert all_product_pairs[3] == ("Good phone", "iPhone 15")

def test_simulate_result_mapping_prod(queue_message_factory: Any) -> None:
    """Simulate the full pipeline, verify we can map sentiment results back to post_ids"""
    queue: Queue[QueueMessage] = Queue()

    queue.put(queue_message_factory("abc123", "RTX 4090 and RX 7900", ["RTX 4090", "RX 7900 XTX"]))
    queue.put(queue_message_factory("def456", "PS5 is amazing", ["PS5"]))
    queue.put(queue_message_factory("ghi789", "No products here", []))
    queue.put(queue_message_factory("jkl012", "iPhone wins", ["iPhone 15"]))

    batch_gen = batch(queue, batch_size=4, max_wait=0.1)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    # Simulate sentiment analysis results (in same order as all_product_pairs)
    simulated_sentiment_results = [
        ("RTX 4090", 0.85),      # Index 0 - from post abc123
        ("RX 7900 XTX", -0.2),   # Index 1 - from post abc123
        ("PS5", 0.95),           # Index 2 - from post def456
        ("iPhone 15", 0.7)       # Index 3 - from post jkl012
    ]

    # Map sentiment results back to post_ids
    results_by_post = {}
    for post_id, start_idx, end_idx, metadata in post_id_mappings:
        # Extract sentiment results for this post using the index range
        post_sentiments = simulated_sentiment_results[start_idx:end_idx]
        results_by_post[post_id] = post_sentiments

    assert len(results_by_post["abc123"]) == 2
    assert results_by_post["abc123"][0] == ("RTX 4090", 0.85)
    assert results_by_post["abc123"][1] == ("RX 7900 XTX", -0.2)

    assert len(results_by_post["def456"]) == 1
    assert results_by_post["def456"][0] == ("PS5", 0.95)

    assert len(results_by_post["ghi789"]) == 0

    assert len(results_by_post["jkl012"]) == 1
    assert results_by_post["jkl012"][0] == ("iPhone 15", 0.7)

def test_large_batch_stress_test(queue_message_factory: Any) -> None:
    """Large batch with varying products to stress-test index calc"""
    queue: Queue[QueueMessage] = Queue()

    # Create 20 posts with varying product counts
    for i in range(20):
        num_products = i % 4  # 0, 1, 2, 3 products alternating
        products = [f"Product{i}_{j}" for j in range(num_products)]
        queue.put(queue_message_factory(f"post{i}", f"text{i}", products))

    batch_gen = batch(queue, batch_size=20, max_wait=2.0)
    post_id_mappings, all_product_pairs, curr_batch = next(batch_gen)

    # Calculate expected total: sum of (i % 4) for i in range(20)
    expected_total = sum(i % 4 for i in range(20))

    assert len(post_id_mappings) == 20, f"Expected 20 posts, got {len(post_id_mappings)}"
    assert len(curr_batch) == 20, f"Expected 20 in batch, got {len(curr_batch)}"
    assert len(all_product_pairs) == expected_total, f"Expected {expected_total} products, got {len(all_product_pairs)}"

    # Verify no overlapping index ranges
    for i in range(len(post_id_mappings) - 1):
        _, _, end_idx, metadata = post_id_mappings[i]
        _, next_start_idx, _, metadata = post_id_mappings[i + 1]
        assert end_idx == next_start_idx, "Index ranges should be continuous"

    assert post_id_mappings[0][0:3] == ("post0", 0, 0)   # 0 products
    assert post_id_mappings[1][0:3] == ("post1", 0, 1)   # 1 product
    assert post_id_mappings[2][0:3] == ("post2", 1, 3)   # 2 products
    assert post_id_mappings[3][0:3] == ("post3", 3, 6)   # 3 products