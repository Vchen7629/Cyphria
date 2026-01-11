from confluent_kafka import TopicPartition  # type: ignore
from ..middleware.kafka_consumer import KafkaConsumer
from ..middleware.logger import StructuredLogger
from ..configs.custom_types import QueueMessage
from typing import Dict, Tuple


# Helper function for commiting offsets from data sources with
# partition safer
def offset_helper(
    batch: list[QueueMessage], consumer: KafkaConsumer, logger: StructuredLogger
) -> None:
    partition_offsets: Dict[Tuple[str, int], int] = {}

    for msg in batch:
        key = (msg["topic"], msg["partition"])
        offset: int = msg["offset"]

        # Only track the latest offset (integer)
        prev_offset: int = partition_offsets.get(key, -1)

        # check the offset to see if latest is larger and save if so
        if offset > prev_offset:
            partition_offsets[key] = offset

    # Build list of TopicPartition objects to commit
    offsets_to_commit = [
        TopicPartition(topic, partition, offset + 1)
        for (topic, partition), offset in partition_offsets.items()
    ]

    # commit the offsets to the broker
    try:
        consumer.commit(offsets=offsets_to_commit, asynchronous=False)
    except Exception as e:
        logger.error(event_type="Kafka", message=f"Offset commit failed: {e}")
