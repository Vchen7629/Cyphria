package cyphria.sentimentinput.middleware;

import org.apache.kafka.common.serialization.Deserializer;
import org.apache.kafka.common.serialization.Serde;
import org.apache.kafka.common.serialization.Serializer;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.datatype.jsr310.JavaTimeModule;

public class JsonSerdes<T> implements Serde<T> {
    private final ObjectMapper mapper = new ObjectMapper()
        .registerModule(new JavaTimeModule());

    private final Class<T> targetClass;

    public JsonSerdes(Class<T> targetClass) {
        this.targetClass = targetClass;
    }

    @Override
    public Serializer<T> serializer() {
        return (topic, data) -> {
            if (data == null) return null;
            try {
                return mapper.writeValueAsBytes(data);
            } catch (Exception e) {
                throw new RuntimeException("Error serializing JSON", e);
            }
        };
    }

    @Override
    public Deserializer<T> deserializer() {
        return (topic, bytes) -> {
            try {
                if (bytes == null || bytes.length == 0) return null;
                return mapper.readValue(bytes, targetClass);
            } catch (Exception e) {
                throw new RuntimeException("Error deserializing JSON", e);
            }
        };
    }
}