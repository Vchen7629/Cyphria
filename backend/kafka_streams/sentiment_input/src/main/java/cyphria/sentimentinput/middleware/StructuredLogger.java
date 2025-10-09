package cyphria.sentimentinput.middleware;

import java.time.Instant;
import java.util.Map;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

import com.fasterxml.jackson.databind.ObjectMapper;

// Logger Class
public class StructuredLogger {
    private static final ObjectMapper mapper = new ObjectMapper();
    private final Logger logger;
    private final String pod;

    // Instance for other classes to get logger from
    public StructuredLogger(Class<?> clazz, String pod) {
        this.logger = LoggerFactory.getLogger(clazz);
        this.pod = pod;
    }

    private String buildLog(String level, String eventType, String message, Map<String, Object> extra) {
        try {
            var log = Map.<String, Object>of(
                "timestamp", Instant.now().toString(),
                "level", level,
                "service", "Sentiment-Kafka-Stream-Worker",
                "pod", pod,
                "event_type", eventType,
                "message", message
            );
            // If extra args are provided
            if (extra != null && !extra.isEmpty()) {
                var merged = new java.util.HashMap<>(log);
                merged.putAll(extra);
                return mapper.writeValueAsString(merged);
            // If no extra args are provided
            } else {
                return mapper.writeValueAsString(log);
            }
        } catch (Exception e) {
            return "{\"error\": \"Failed to serialize log\"}";
        }
    }

    // Overloaded Methods to allow for no extra args provided
    public void info(String eventType, String message) {
        logger.info(buildLog("INFO", eventType, message, null));
    }

    public void error(String eventType, String message) {
        logger.info(buildLog("ERROR", eventType, message, null));
    }

    public void debug(String eventType, String message) {
        logger.info(buildLog("DEBUG", eventType, message, null));
    }

    // Methods with extra included
    public void info(String eventType, String message, Map<String, Object> extra) {
        logger.info(buildLog("INFO", eventType, message, extra));
    }

    public void error(String eventType, String message, Map<String, Object> extra) {
        logger.info(buildLog("ERROR", eventType, message, extra));
    }

    public void debug(String eventType, String message, Map<String, Object> extra) {
        logger.info(buildLog("DEBUG", eventType, message, extra));
    }
}
