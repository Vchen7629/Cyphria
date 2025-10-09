package cyphria.sentimentinput.config;

import java.time.Instant;

// Defining types for rawposy
public record RawPost(
    String post_id,
    String body,
    String subreddit,
    Instant timestamp
){}


