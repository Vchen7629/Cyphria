# This is settings for configuring kafka producer
KAFKA_SETTINGS = {
    "bootstrap_servers": ["localhost:9092"],
    "acks": "all",
    "retries": 3,
    "request_timeout_ms": 15000,
    "max_block_ms": 30000,
}
