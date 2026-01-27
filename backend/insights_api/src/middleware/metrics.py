from prometheus_client import Histogram
from prometheus_fastapi_instrumentator import Instrumentator

db_query_duration = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type", "query_name", "table"],
    # time frame in seconds
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5),
)

cache_operation_duration = Histogram(
    "cache_operation_duration_seconds",
    "How long it took for cache operation in seconds",
    ["operation", "hit"],
    buckets=(0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25),  # cache is faster
)

instrumentator = Instrumentator(
    should_group_status_codes=False,  # Don't group 2xx, 3xx, 4xx
    should_ignore_untemplated=True,  # Ignore non-existant routes
    should_respect_env_var=True,
    should_instrument_requests_inprogress=False,  # Skip in-progress requests
    excluded_handlers=["/metrics"],  # dont track metrics endpoint
)
