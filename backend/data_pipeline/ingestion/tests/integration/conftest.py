import pytest
import time
from testcontainers.kafka import KafkaContainer

# Creating Pytest Fixture to create Kafka Session 
# for all integration tests
@pytest.fixture(scope="session")
def kafka_service():
    with KafkaContainer("confluentinc/cp-kafka:7.6.0") as kafka:
        time.sleep(20)
        bootstrap_server = kafka.get_bootstrap_server()
        print(f"[TEST] Kafka ready at {bootstrap_server}")
        yield bootstrap_server
