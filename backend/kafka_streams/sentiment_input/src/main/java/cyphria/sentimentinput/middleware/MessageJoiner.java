package cyphria.sentimentinput.middleware;

import org.apache.kafka.common.serialization.Serdes;
import org.apache.kafka.streams.StreamsBuilder;
import org.apache.kafka.streams.kstream.Consumed;
import org.apache.kafka.streams.kstream.KTable;
import org.apache.kafka.streams.kstream.Produced;

import cyphria.sentimentinput.config.Keywords;
import cyphria.sentimentinput.config.RawPost;
import cyphria.sentimentinput.config.SentimentInputs;

public class MessageJoiner {
    public static void buildTopology(StreamsBuilder builder) {
        // Json Serializer/Deserializer (JsonSerde)
        var rawSerde = new JsonSerdes<>(RawPost.class);
        var kwSerde = new JsonSerdes<>(Keywords.class);
        var sentimentSerde = new JsonSerdes<>(SentimentInputs.class);
        StructuredLogger log = new StructuredLogger(MessageJoiner.class, "pod-1");


        // State Table for raw post messages
        KTable<String, RawPost> rawTable = builder.table(
            "raw-data", // Input Topic name
            Consumed.with(Serdes.String(), rawSerde) // C
        );

        // State Table for keywords messages
        KTable<String, Keywords> keywordsTable = builder.table(
            "test", // Input Topic name
            Consumed.with(Serdes.String(), kwSerde) // C
        );

        // Join the two tables on their key (post_id)
        KTable<String, SentimentInputs> joined = keywordsTable.join(
            rawTable, 
            (keywords, raw) -> {
                try {
                    return new SentimentInputs(
                        raw.post_id(), 
                        raw.body(), 
                        keywords.keywords()
                    );
                } catch (Exception e) {
                    log.error(
                        "Kafka-stream", 
                        "Error Joining Keywords and Raw Posts"
                    );
                    return null; // Continue on failure
                }
            }
        );

        // Send results to output topic
        joined.toStream().to(
            "sentiment-analysis", // target topic name
            Produced.with(Serdes.String(), sentimentSerde)
        );
    }
}
