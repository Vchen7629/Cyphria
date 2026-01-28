# Database Tables & Indexes

## raw_comments

### Recommended Indexes

```sql
-- GIN index for array containment queries on detected_products
CREATE INDEX idx_raw_comments_detected_products ON raw_comments USING GIN(detected_products);

-- Partial index for sentiment_processed (only indexes true values)
CREATE INDEX idx_raw_comments_sentiment ON raw_comments(sentiment_processed) WHERE sentiment_processed = true;

-- B-tree index for time-based filtering
CREATE INDEX idx_raw_comments_created ON raw_comments(created_utc);
```

### Notes

- The GIN index on `detected_products` is critical for queries using `= ANY(detected_products)` on large tables
- The partial index on `sentiment_processed` is smaller and faster since we only query for `true` values
- Consider a composite index if queries always combine these filters

## product_rankings

### Recommended Indexes


#### product name
```sql
-- Enable pg_trgm extension for fuzzy text search (run once)
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- GIN trigram index for fast ILIKE searches on product names
CREATE INDEX idx_product_name_trgm ON product_rankings USING gin (product_name gin_trgm_ops);

-- Composite index for cursor-based pagination
CREATE INDEX idx_product_search_cursor ON product_rankings (product_name, id);
```
#### product_topic
```sql
CREATE INDEX idx_product_topic ON product_rankings (product_topic);
```


### Notes

- The trigram GIN index enables fast `ILIKE '%search%'` queries for product name matching
- The composite index supports efficient cursor-based pagination, avoiding expensive `OFFSET` operations
- Consider implementing autocomplete using prefix matching (`ILIKE 'search%'`) which can also leverage these indexes
