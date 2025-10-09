import java.time.Instant;
import java.util.List;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.TopologyTestDriver;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.junit.jupiter.api.Assertions.fail;
import org.junit.jupiter.api.Test;

import cyphria.sentimentinput.config.Keywords;
import cyphria.sentimentinput.config.RawPost;
import cyphria.sentimentinput.config.SentimentInputs;
import cyphria.sentimentinput.config.StreamsConfigFactory;
import cyphria.sentimentinput.middleware.JsonSerdes;
import cyphria.sentimentinput.middleware.MessageJoiner;

public class MessageJoinTest {
    @Test // Happy Path: Expected Behavior
    public void testMessageJoin() {
        StreamsBuilder builder = new StreamsBuilder();
        MessageJoiner.buildTopology(builder);

        try (TopologyTestDriver driver = new TopologyTestDriver(
            builder.build(),
            StreamsConfigFactory.build("dummy:1234", "/tmp/kafka-test")
        )) {
            // Setup Mock Topics
            var rawTopic = driver.createInputTopic(
                "raw-data",
                Serdes.String().serializer(),
                new JsonSerdes<>(RawPost.class).serializer()
            );
            var kwTopic = driver.createInputTopic(
                "test",
                Serdes.String().serializer(),
                new JsonSerdes<>(Keywords.class).serializer()
            );
            var outTopic = driver.createOutputTopic(
                "sentiment-analysis",
                Serdes.String().deserializer(),
                new JsonSerdes<>(SentimentInputs.class).deserializer()
            );
            
            // Send Messages
            rawTopic.pipeInput("post1", new RawPost("post1", "Hello", "Sub", Instant.now()));
            kwTopic.pipeInput("post1", new Keywords("post1", List.of("Java", "Scala", "Python")));

            // Read Output
            var result = outTopic.readKeyValue();
            assertEquals("post1", result.key);
            assertEquals("Hello", result.value.body());
            assertEquals(List.of("Java", "Scala", "Python"), result.value.keywords());
        }
    }

    @Test // None Matching Key Edge Case
    public void testNonMatchingKeys() {
        StreamsBuilder builder = new StreamsBuilder();
        MessageJoiner.buildTopology(builder);

        try (TopologyTestDriver driver = new TopologyTestDriver(
            builder.build(),
            StreamsConfigFactory.build("dummy:1234", "/tmp/kafka-test")
        )) {
            // Setup Mock Topics
            var rawTopic = driver.createInputTopic(
                "raw-data",
                Serdes.String().serializer(),
                new JsonSerdes<>(RawPost.class).serializer()
            );
            var kwTopic = driver.createInputTopic(
                "test",
                Serdes.String().serializer(),
                new JsonSerdes<>(Keywords.class).serializer()
            );
            var outTopic = driver.createOutputTopic(
                "sentiment-analysis",
                Serdes.String().deserializer(),
                new JsonSerdes<>(SentimentInputs.class).deserializer()
            );
            
            // Send Messages
            rawTopic.pipeInput("post1", new RawPost("post1", "Hello", "Sub", Instant.now()));
            kwTopic.pipeInput("post2", new Keywords("post2", List.of("Java", "Scala", "Python")));

            // Fail condition
            if (!outTopic.isEmpty()) {
                var result = outTopic.readKeyValue();
                fail("Expected no output, but got: " + result);
            }

            // Read Output
            assertTrue(outTopic.isEmpty(), "Output topic should be empty for non-matching keys");
        }
    }
}
