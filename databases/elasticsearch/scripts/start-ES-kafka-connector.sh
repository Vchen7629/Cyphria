source ../.env

curl --location 'http://localhost:8083/connectors' \
    --header 'Content-Type: application/json' \
    --data '{
        "name": "elasticsearch-sink-connector",
        "config": {
            "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
            "topics": "reddit-data",
            "connection.url": "http://elasticsearch:9200",
            "connection.username": "'$KAFKA_CONNECT_ACCOUNT_USERNAME'",
            "connection.password":  "'$KAFKA_CONNECT_ACCOUNT_PASSWORD'",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "false",
            "schema.ignore": "true",
            "auto.create.indices.enable": "false",
            "key.ignore": "true",
            "errors.tolerance": "all",
            "errors.deadletterqueue.topic.name": "test-dlq",
            "errors.deadletterqueue.context.headers.enable": "true",
            "errors.deadletterqueue.topic.replication.factor": "1"
        }
    }'
