package cyphria.sentimentinput.config;

import java.util.Properties;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsConfig;
import org.apache.kafka.streams.processor.WallclockTimestampExtractor;

public class StreamsConfigFactory {
    public static Properties build(String server_ip, String folder) {
        Properties props = new Properties();

        // Basic Identifiers
        props.put(StreamsConfig.APPLICATION_ID_CONFIG, "sentiment-join-service");
        props.put(StreamsConfig.BOOTSTRAP_SERVERS_CONFIG, server_ip);

        // SerDe Defaults
        props.put(StreamsConfig.DEFAULT_KEY_SERDE_CLASS_CONFIG, Serdes.String().getClass());
        props.put(StreamsConfig.DEFAULT_VALUE_SERDE_CLASS_CONFIG, Serdes.String().getClass());

        // Processing guarantees
        props.put(StreamsConfig.PROCESSING_GUARANTEE_CONFIG, StreamsConfig.EXACTLY_ONCE_V2);

        // Performance
        props.put(StreamsConfig.CACHE_MAX_BYTES_BUFFERING_CONFIG, 10 * 1024 * 1024L); // 10 MB
        props.put(StreamsConfig.COMMIT_INTERVAL_MS_CONFIG, 1000); // 1 second commit interval

        // Timestamp extractor
        props.put(StreamsConfig.DEFAULT_TIMESTAMP_EXTRACTOR_CLASS_CONFIG, WallclockTimestampExtractor.class);

        // Threading 
        props.put(StreamsConfig.NUM_STREAM_THREADS_CONFIG, 2);

        // State directory
        props.put(StreamsConfig.STATE_DIR_CONFIG, folder);

        // Retries 
        props.put("retries", 5); // producer retries
        props.put("retry.backoff.ms", 100L); // delay between retries
        props.put("delivery.timeout.ms", 120000); // delivery timeout 2 min
        props.put("max.in.flight.requests.per.connection", 1); // ensure order with EOS
        props.put("acks", "all"); // ensure broker confirms replication

        // Error handling (optional)
        props.put("default.deserialization.exception.handler", 
                  "org.apache.kafka.streams.errors.LogAndContinueExceptionHandler");

        return props;
    }   
}
