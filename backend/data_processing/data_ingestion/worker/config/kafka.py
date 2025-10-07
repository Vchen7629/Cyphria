# This is settings for configuring kafka producer
KAFKA_SETTINGS = {
    # cluster
    "bootstrap.servers": "localhost:9092",

    # for message reliability
    "acks": "all",
    "retries": 3,
    "enable.idempotence": True, # prevents duplicates
    "max.in.flight.requests.per.connection": 5, # required due to enabled idempotence

    # Timeouts
    "request.timeout.ms": 15000, # per broker request timeout
    "message.timeout.ms": 30000, # max time to try sending before failure

    # Performance (Batching/Throughput)
    "linger.ms": 10, # Wait 10 ms to batch messages
    "batch.size": 32768, # Up to 32 kb per batch
    "compression.type": "lz4", # Compression type (lz4)

    # Monitoring
    "statistics.interval.ms": 60000,   # emit stats every 60s (via producer.stats callback)
    "log.connection.close": False,     # for cleaner logs
}
