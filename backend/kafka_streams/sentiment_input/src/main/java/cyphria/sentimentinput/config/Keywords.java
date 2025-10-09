package cyphria.sentimentinput.config;
import java.util.List;

public record Keywords(
    String post_id,
    List<String> keywords
){}
