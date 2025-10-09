import java.time.Instant;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.Test;

import cyphria.sentimentinput.config.RawPost;
import cyphria.sentimentinput.middleware.JsonSerdes;

public class JsonSerdesTest {
    @Test // Happy Path Test
    public void testSerializeDeserialize() {
        Instant now = Instant.now();
        var rawPost = new RawPost(
            "post123", 
            "Hello World",
            "subreddit",
            now
        );

        var serde = new JsonSerdes<>(RawPost.class);

        // Serialize 
        byte[] bytes = serde.serializer().serialize("raw-data", rawPost);
        assertNotNull(bytes); // Testing to see if the bytes exist after serialize
        assertTrue(bytes.length > 0);

        // Deserialize
        RawPost deserialized = serde.deserializer().deserialize("raw-data", bytes);
        assertNotNull(deserialized);

        // Assert serialize and deserialize result in same text
        assertEquals(rawPost.post_id(), deserialized.post_id());
        assertEquals(rawPost.body(), deserialized.body());
        assertEquals(rawPost.subreddit(), deserialized.subreddit());
        assertEquals(rawPost.timestamp(), deserialized.timestamp());
    }

    @Test // Edge Case: Null fields
    public void testNullHandling() {
        var serde = new JsonSerdes<>(RawPost.class);

        // Null input to serializer
        byte[] bytes = serde.serializer().serialize("raw-data", null);
        assertNull(bytes); // you can decide if you want null or empty array

        // Null input to deserializer
        RawPost deserialized = serde.deserializer().deserialize("raw-data", null);
        assertNull(deserialized);

        // Empty byte array
        deserialized = serde.deserializer().deserialize("raw-data", new byte[0]);
        assertNull(deserialized);
    }
}
