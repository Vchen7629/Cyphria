package cyphria.sentimentinput; 

import org.apache.kafka.streams.KafkaStreams;
import org.apache.kafka.streams.StreamsBuilder;

import cyphria.sentimentinput.config.StreamsConfigFactory;
import cyphria.sentimentinput.middleware.MessageJoiner;


public class Worker{
    public static void main(String[] args) {
        var builder = new StreamsBuilder();

        // Building Join Topology
        MessageJoiner.buildTopology(builder);

        // Load Configs
        var props = StreamsConfigFactory.build(
            "localhost:9092", // Cluster Ip
            "/tmp/kafka-streams/sentiment-join" // State file directory
        );

        // Start Kafka Streams Worker
        KafkaStreams streams = new KafkaStreams(builder.build(), props);

        // Handling Graceful shutdowns
        Runtime.getRuntime().addShutdownHook(new Thread(streams::close));

        streams.start();
    }
}