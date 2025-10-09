package cyphria.sentimentinput.config;
import java.util.List;

public record SentimentInputs(
    String post_id,
    String body,
    List<String> keywords
) {}
