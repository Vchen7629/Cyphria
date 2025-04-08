#!/bin/bash
set -e

for spec in \
  "_connect-configs:1:1:compact" \
  "_connect-offsets:25:1:compact" \
  "_connect-status:5:1:compact" \
  "raw-data:8:1:delete" \
  "processed_data:8:1:delete" \
  "reddit-data:8:1:delete" \
  "sentiment-analysis:8:1:delete" \
  "test:4:1:delete" \
  "test-dlq:4:1:delete \
do
  IFS=":" read -r topic partitions rf cleanup <<< "$spec"
  /opt/bitnami/kafka/bin/kafka-topics.sh \
    --create \
    --bootstrap-server localhost:9092 \
    --topic "$topic" \
    --partitions "$partitions" \
    --replication-factor "$rf" \
    --config "cleanup.policy=$cleanup"
done
