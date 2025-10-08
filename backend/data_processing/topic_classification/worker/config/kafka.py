# This is settings for configuring kafka producer
KAFKA_SETTINGS_PRODUCER = {
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

# This is settings for configuring kafka consumer
KAFKA_SETTINGS_CONSUMER = {
    # cluster
    "bootstrap.servers": "localhost:9092",

    # consumer group (Identifier for this service so horizontal scaling works properly)
    "group.id": "keyword-extraction-service",

    # Start position if no committed offset exists
    "auto.offset.reset": "earliest",

    # Reliability / Fault tolerance
    "enable.auto.commit": True, 
    "enable.partition.eof": False,

    # Timeouts (Heartbeat)
    "session.timeout.ms": 10000, # how long broker waits before kicking consumer out
    "heartbeat.interval.ms": 1000, # how often to ping broker
    
    # Monitoring
    "statistics.interval.ms": 60000,   # emit stats every 60s
    "log.connection.close": False # for cleaner logs
} 

