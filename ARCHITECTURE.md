# Cyphria Architecture Document

**Version:** 2.0 (Post-Research)
**Last Updated:** 2026-01-12
**Status:** Finalized after production best practices research

---

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Key Architectural Decisions](#key-architectural-decisions)
3. [System Components](#system-components)
4. [Data Flow](#data-flow)
5. [Database Schema](#database-schema)
6. [Airflow DAG Design](#airflow-dag-design)
7. [Scaling Considerations](#scaling-considerations)
8. [Rationale & Research](#rationale--research)

---

## Architecture Overview

**Architecture Pattern:** Medallion Architecture with Batch ETL
**Orchestration:** Apache Airflow
**Storage:** PostgreSQL + TimescaleDB
**Processing:** Python (batch) + Spark (historical backfill)

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│ Data Sources                                                │
├─────────────────────────────────────────────────────────────┤
│  • Reddit API (PRAW) - Daily micro-batches                  │
│  • arctic_shift torrents - Historical backfill             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Apache Airflow - Orchestration Layer                       │
├─────────────────────────────────────────────────────────────┤
│  • Schedule ingestion (every 4 hours per category)         │
│  • Coordinate parallel processing (sentiment + LLM)        │
│  • Manage historical backfill (Spark jobs)                 │
│  • Calculate daily rankings                                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL + TimescaleDB - Data Lake (Medallion Layers)    │
├─────────────────────────────────────────────────────────────┤
│  Bronze:  raw_comments (full text, metadata)               │
│  Silver:  product_sentiment (ABSA scores)                  │
│           product_summaries (LLM-generated TLDR)           │
│  Gold:    product_rankings (aggregated scores, grades)     │
│           product_featured_comments (curated display)      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Insights API (FastAPI)                                      │
├─────────────────────────────────────────────────────────────┤
│  • GET /products/{category}/rankings                        │
│  • GET /products/{id}/details                               │
│  • GET /products/search?q=...                               │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend (React)                                            │
├─────────────────────────────────────────────────────────────┤
│  • Product rankings with grades (A+, A-, B+, etc.)         │
│  • TLDR summaries & highlights                              │
│  • Featured Reddit comments                                 │
│  • Inspired by: dharm.is/computing/laptops                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Architectural Decisions

### 1. ❌ Kafka Removed (After Evaluation)

**Initial consideration:** Use Kafka for fan-out pattern to multiple consumers (sentiment + LLM)

**Decision:** Use database staging instead

**Rationale:**
- **Batch processing, not streaming:** Micro-batches every 4 hours ≠ continuous streams
- **Low throughput:** 10k comments/day = ~3 comments/second average (trivial for PostgreSQL)
- **Sequential is acceptable:** Total processing time ~25 minutes per batch (sentiment: 17 min, LLM: 5 min)
- **Operational overhead:** Kafka adds Zookeeper, brokers, monitoring complexity
- **Industry practice:** Production teams use database staging for batch ETL (see research below)

**What we learned:**
> "When dealing with large volumes of data, it's more efficient to process data in batches in parallel... ETL and ELT data pipelines are the most common use case for Apache Airflow, with **90% of respondents using Airflow for ETL/ELT**." - [Apache Airflow Survey 2023](https://www.astronomer.io/blog/etl-in-airflow-comprehensive-guide-efficient-data-pipelines/)

### 2. ✅ Database Staging Layer Justified

**Initial concern:** "Extra" reads/writes to raw_comments table seem inefficient

**Decision:** Keep raw_comments as Bronze layer (industry best practice)

**Rationale:**
- **Medallion Architecture:** Bronze (raw) → Silver (cleaned) → Gold (aggregated) is the standard pattern
- **Debuggable:** Can inspect data at each stage
- **Reprocessable:** Can rerun sentiment/LLM without re-fetching from Reddit
- **Auditable:** Immutable record of source data
- **Product requirements:** Need comment text for displaying actual Reddit quotes to users
- **Performance is fine:**
  - Write 10k comments: ~5MB write (~0.5 seconds)
  - Read for sentiment: ~5MB read (~0.3 seconds)
  - Read for LLM: ~5MB read (~0.3 seconds, cached)
  - **Total: ~1 second per batch** (negligible)

**What we learned:**
> "For workflows, you should break up the steps into bite-size tasks so **each step stores the intermediate results in a stage**, so you can easily re-run from a specific task and debug what the output was." - [Astronomer Airflow Best Practices](https://docs.astronomer.io/learn/airflow-passing-data-between-tasks)

### 3. ✅ Airflow Parallel Execution

**Pattern:** Multiple tasks read from `raw_comments` simultaneously

```python
# DAG: processing_pipeline
sentiment_task = PythonOperator(...)  # Reads raw_comments
llm_task = PythonOperator(...)        # Also reads raw_comments

[sentiment_task, llm_task]  # Execute in parallel
```

**Benefits:**
- Both tasks run concurrently (Airflow handles scheduling)
- PostgreSQL MVCC allows concurrent reads without locks
- No contention (both are SELECT queries)
- Total time = max(sentiment_time, llm_time) instead of sum

### 4. ✅ Micro-Batch Scheduling Strategy

**Pattern:** Staggered category processing every 4 hours

```
00:00 - GPU category (r/nvidia, r/amd, r/buildapc)
04:00 - Laptop category (r/laptops, r/thinkpad)
08:00 - Headphone category (r/headphones, r/audiophile)
12:00 - Monitor category (r/monitors)
16:00 - Keyboard category (r/mechanicalkeyboards)
20:00 - Mouse category (r/mousereview)
```

**Benefits:**
- Spreads Reddit API load across 24 hours (avoids rate limits)
- Each category processes independently
- Easy to add new categories (just add new time slot)
- Matches product vision (multiple categories: GPUs, laptops, headphones, etc.)

---

## System Components

### 1. Data Ingestion Service

**Technology:** Python + PRAW (Reddit API wrapper)

**Responsibilities:**
- Fetch posts from Reddit (24-48 hour delay strategy)
- Fetch all comments from posts
- Detect product mentions (category-specific detectors)
- Normalize product names (e.g., "4090" → "NVIDIA RTX 4090")
- Filter low-quality comments (length, score, bots)
- Write to `raw_comments` table

**Orchestration:** Airflow DAG per category (e.g., `daily_ingestion_gpu`)

**Schedule:** Every 4 hours per category (staggered)

### 2. Sentiment Analysis Service

**Technology:** Python + HuggingFace Transformers (DeBERTa ABSA model)

**Responsibilities:**
- Read unprocessed comments from `raw_comments`
- Extract (comment, product) pairs
- Run Aspect-Based Sentiment Analysis
- Classify sentiment (positive/negative/neutral)
- Write to `product_sentiment` table
- Mark comments as processed

**Orchestration:** Airflow task triggered after ingestion completes

**Processing:** Batched inference (64 pairs per batch for efficiency)

### 3. LLM Summarization Service

**Technology:** Python + OpenAI API (GPT-4o-mini)

**Responsibilities:**
- Read comments per product from `raw_comments` + `product_sentiment`
- Select top comments (mix of positive/negative, sorted by upvotes)
- Generate TLDR (one-sentence summary)
- Generate highlights (4-5 bullet points)
- Extract pros/cons
- Write to `product_summaries` table

**Orchestration:** Airflow DAG runs daily at 1 AM

**Cost:** ~$0.001 per product = $1.50/month for 50 products

### 4. Ranking Calculator Service

**Technology:** Python + NumPy

**Responsibilities:**
- Aggregate sentiment scores per product
- Calculate Bayesian weighted scores (IMDB Top 250 formula)
- Assign letter grades (A+, A, A-, B+, etc.)
- Calculate approval percentages
- Assign badges (Top Pick, Most Discussed, Limited Data)
- Write to `product_rankings` table

**Orchestration:** Airflow DAG runs daily at 2 AM

**Windows:** 30d, 90d, all_time

### 5. Historical Backfill Service

**Technology:** Apache Spark + PySpark

**Responsibilities:**
- Read arctic_shift parquet files (multi-GB per month)
- Filter for relevant subreddits
- Detect products (distributed processing)
- Run sentiment analysis (PySpark UDF)
- Write to `raw_comments` and `product_sentiment` tables

**Orchestration:** Airflow DAG (manual trigger, one-time)

**Data Source:** [arctic_shift GitHub torrents](https://github.com/ArthurHeitmann/arctic_shift)

### 6. Insights API

**Technology:** FastAPI + PostgreSQL

**Endpoints:**
- `GET /api/v1/categories` - List all categories
- `GET /api/v1/categories/{category}/products` - Ranked products
- `GET /api/v1/products/{id}` - Product details with TLDR, highlights, featured comments
- `GET /api/v1/products/search?q={query}` - Search products

**Data Sources:** Reads from `product_rankings`, `product_summaries`, `product_featured_comments`

### 7. Frontend

**Technology:** React 19 + Redux

**Features:**
- Product category browser
- Ranked product lists with grades (A+, A-, etc.)
- Product detail pages with TLDR, highlights, Reddit comments
- Search functionality
- Inspired by: [dharm.is/computing/laptops](https://dharm.is/computing/laptops)

---

## Data Flow

### Daily Ingestion Flow (Per Category)

```
1. Airflow triggers: daily_ingestion_gpu (every 4 hours)
   └─ Task: fetch_gpu_comments
      ├─ PRAW: Fetch posts from r/nvidia, r/amd, r/buildapc
      ├─ PRAW: Fetch comments from posts (24-48h old)
      ├─ Filter: Quality checks (length, score, bots)
      ├─ Detect: GPUDetector.detect(comment_body)
      ├─ Normalize: GPUNameNormalizer.normalize(detected_gpus)
      └─ Write: INSERT INTO raw_comments (comment_id, comment_body,
                detected_products, subreddit, score, created_utc, category)

2. Airflow triggers: processing_pipeline (30 min after ingestion)
   ├─ Task: analyze_sentiment (runs in parallel)
   │  ├─ Read: SELECT * FROM raw_comments WHERE sentiment_processed = FALSE
   │  ├─ Process: ABSA model on (comment, product) pairs
   │  ├─ Write: INSERT INTO product_sentiment (comment_id, product_name,
   │  │         sentiment_score, sentiment_label, ...)
   │  └─ Update: UPDATE raw_comments SET sentiment_processed = TRUE
   │
   └─ Task: generate_summaries (runs in parallel)
      ├─ Read: SELECT comment_body FROM raw_comments WHERE product_name = ...
      ├─ Process: GPT-4o-mini generates TLDR + highlights
      └─ Write: INSERT INTO product_summaries (product_name, tldr,
                highlights, pros, cons, ...)

3. Airflow triggers: daily_ranking (daily at 2 AM)
   └─ Task: calculate_rankings
      ├─ Read: SELECT * FROM product_sentiment GROUP BY product_name
      ├─ Process: Bayesian scoring, grading, badge assignment
      └─ Write: INSERT INTO product_rankings (product_name, rank, grade,
                bayesian_score, approval_percentage, ...)

4. Airflow triggers: select_featured_comments (after ranking)
   └─ Task: curate_comments
      ├─ Read: Top comments per product (mix of sentiments, high upvotes)
      └─ Write: INSERT INTO product_featured_comments (product_name,
                comment_id, display_order, sentiment_label, ...)
```

### Historical Backfill Flow (One-Time)

```
1. Download arctic_shift torrents (parquet files per month)
   └─ Storage: /data/arctic_shift/comments/2024-01/*.parquet

2. Airflow triggers: backfill_historical_data (manual)
   └─ SparkSubmitOperator: process_arctic_shift.py
      ├─ Spark: Read parquet files (distributed across executors)
      ├─ Filter: subreddit IN ('nvidia', 'amd', 'buildapc', ...)
      ├─ Detect: UDF applies GPUDetector to each comment
      ├─ Sentiment: UDF applies ABSA model (distributed)
      └─ Write: JDBC bulk insert to raw_comments + product_sentiment
                (Spark handles batching automatically)

3. Ranking recalculation includes historical data
   └─ all_time window now spans 1-2 years instead of 30-90 days
```

---

## Database Schema

### Medallion Architecture Layers

```
Bronze Layer (Raw Data):
├─ raw_comments           # Full comment text + metadata

Silver Layer (Transformed):
├─ product_sentiment      # Sentiment scores per product mention
└─ product_summaries      # LLM-generated TLDR/highlights

Gold Layer (Aggregated):
├─ product_rankings       # Ranked products with grades
├─ product_featured_comments  # Curated display comments
└─ products               # Product catalog metadata
```

### Schema Details

```sql
-- ============================================================
-- BRONZE LAYER: Raw Data Storage
-- ============================================================

CREATE TABLE raw_comments (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(50) UNIQUE NOT NULL,
    post_id VARCHAR(50) NOT NULL,

    -- Comment content
    comment_body TEXT NOT NULL,
    detected_products TEXT[] NOT NULL,  -- Normalized product names

    -- Metadata
    subreddit VARCHAR(100) NOT NULL,
    author VARCHAR(100),
    score INT DEFAULT 0,  -- Reddit upvotes
    created_utc TIMESTAMPTZ NOT NULL,
    category VARCHAR(50) NOT NULL,  -- "GPU", "Laptop", etc.

    -- Processing tracking
    ingested_at TIMESTAMPTZ DEFAULT NOW(),
    sentiment_processed BOOLEAN DEFAULT FALSE,

    CONSTRAINT chk_detected_products CHECK (array_length(detected_products, 1) > 0)
);

CREATE INDEX idx_raw_comments_comment_id ON raw_comments(comment_id);
CREATE INDEX idx_raw_comments_products ON raw_comments USING GIN(detected_products);
CREATE INDEX idx_raw_comments_category ON raw_comments(category, created_utc DESC);
CREATE INDEX idx_raw_comments_sentiment_pending ON raw_comments(sentiment_processed)
    WHERE sentiment_processed = FALSE;

-- ============================================================
-- SILVER LAYER: Transformed Data
-- ============================================================

CREATE TABLE product_sentiment (
    id SERIAL PRIMARY KEY,
    comment_id VARCHAR(50) NOT NULL REFERENCES raw_comments(comment_id),
    product_name TEXT NOT NULL,

    sentiment_score FLOAT NOT NULL CHECK (sentiment_score BETWEEN -1 AND 1),
    sentiment_label VARCHAR(20) NOT NULL,  -- "positive", "negative", "neutral"

    -- Denormalized metadata for fast queries
    subreddit VARCHAR(100) NOT NULL,
    comment_score INT DEFAULT 0,
    created_utc TIMESTAMPTZ NOT NULL,

    analyzed_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_product_sentiment_product ON product_sentiment(product_name, created_utc DESC);
CREATE INDEX idx_product_sentiment_score ON product_sentiment(product_name, sentiment_score DESC);

CREATE TABLE product_summaries (
    id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,

    -- LLM-generated content
    tldr TEXT NOT NULL,  -- One-sentence summary
    highlights TEXT[] NOT NULL,  -- 4-5 bullet points
    pros TEXT[],
    cons TEXT[],

    -- Generation metadata
    generated_from_comment_count INT NOT NULL,
    generated_at TIMESTAMPTZ DEFAULT NOW(),
    model_used VARCHAR(100),  -- "gpt-4o-mini"
    time_window VARCHAR(20),  -- "30d", "90d", "all_time"

    UNIQUE(product_name, time_window)
);

CREATE INDEX idx_product_summaries_product ON product_summaries(product_name);

-- ============================================================
-- GOLD LAYER: Aggregated Analytics
-- ============================================================

CREATE TABLE product_rankings (
    id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    time_window VARCHAR(20) NOT NULL,  -- "30d", "90d", "all_time"

    -- Ranking
    rank INTEGER NOT NULL,
    grade VARCHAR(5),  -- "A+", "A", "A-", "B+", etc.

    -- Scores
    bayesian_score DOUBLE PRECISION NOT NULL,
    avg_sentiment DOUBLE PRECISION NOT NULL,
    approval_percentage INT,  -- 86% (like dharm.is)

    -- Metrics
    mention_count INTEGER NOT NULL,
    positive_count INTEGER,
    negative_count INTEGER,
    neutral_count INTEGER,

    -- Badges
    is_top_pick BOOLEAN DEFAULT FALSE,         -- Rank #1
    is_most_discussed BOOLEAN DEFAULT FALSE,   -- Highest mention count
    has_limited_data BOOLEAN DEFAULT FALSE,    -- < 10 mentions

    -- Metadata
    calculation_date DATE NOT NULL,
    updated_at TIMESTAMPTZ DEFAULT NOW(),

    UNIQUE(category, time_window, rank, calculation_date)
);

CREATE INDEX idx_rankings_category_rank ON product_rankings(category, time_window, rank);
CREATE INDEX idx_rankings_product ON product_rankings(product_name, time_window);

CREATE TABLE product_featured_comments (
    id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    comment_id VARCHAR(50) NOT NULL REFERENCES raw_comments(comment_id),

    display_order INT NOT NULL,  -- 1, 2, 3 for top 3
    sentiment_label VARCHAR(20) NOT NULL,
    comment_score INT NOT NULL,

    selected_at TIMESTAMPTZ DEFAULT NOW(),
    time_window VARCHAR(20),

    UNIQUE(product_name, time_window, display_order)
);

CREATE INDEX idx_featured_comments_product ON product_featured_comments(product_name, time_window);

CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL UNIQUE,
    category VARCHAR(50) NOT NULL,
    brand VARCHAR(100),
    model VARCHAR(100),

    -- Pricing
    msrp DECIMAL(10, 2),
    current_price DECIMAL(10, 2),
    price_tier VARCHAR(10),  -- "$", "$$", "$$$"
    price_source TEXT,
    price_updated_at TIMESTAMPTZ,

    -- Metadata
    release_date DATE,
    image_url TEXT,
    specs JSONB,

    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_name ON products(product_name);
```

---

## Airflow DAG Design

### DAG 1: Category Ingestion (Per Category)

```python
# dags/daily_ingestion_gpu.py
with DAG(
    'daily_ingestion_gpu',
    schedule_interval='0 */4 * * *',  # Every 4 hours
    catchup=False,
    tags=['ingestion', 'gpu']
) as dag:

    fetch_task = PythonOperator(
        task_id='fetch_gpu_comments',
        python_callable=fetch_and_store_comments,
        op_kwargs={
            'category': 'GPU',
            'subreddits': ['nvidia', 'amd', 'buildapc', 'hardware']
        }
    )
```

### DAG 2: Parallel Processing

```python
# dags/processing_pipeline.py
with DAG(
    'processing_pipeline',
    schedule_interval='30 */4 * * *',  # 30 min after ingestion
    catchup=False,
    tags=['processing']
) as dag:

    wait_for_ingestion = ExternalTaskSensor(
        task_id='wait_for_ingestion',
        external_dag_id='daily_ingestion_gpu',
        external_task_id='fetch_gpu_comments'
    )

    sentiment_task = PythonOperator(
        task_id='analyze_sentiment',
        python_callable=analyze_unprocessed_comments
    )

    llm_task = PythonOperator(
        task_id='generate_summaries',
        python_callable=generate_product_summaries
    )

    wait_for_ingestion >> [sentiment_task, llm_task]  # Parallel execution
```

### DAG 3: Daily Ranking

```python
# dags/daily_ranking.py
with DAG(
    'daily_ranking',
    schedule_interval='0 2 * * *',  # Daily at 2 AM
    catchup=False,
    tags=['ranking']
) as dag:

    rank_30d = PythonOperator(
        task_id='calculate_30d_rankings',
        python_callable=calculate_rankings,
        op_kwargs={'time_window': '30 days'}
    )

    rank_90d = PythonOperator(
        task_id='calculate_90d_rankings',
        python_callable=calculate_rankings,
        op_kwargs={'time_window': '90 days'}
    )

    select_comments = PythonOperator(
        task_id='select_featured_comments',
        python_callable=curate_featured_comments
    )

    [rank_30d, rank_90d] >> select_comments
```

### DAG 4: Historical Backfill

```python
# dags/backfill_historical_data.py
with DAG(
    'backfill_historical_data',
    schedule_interval=None,  # Manual trigger only
    catchup=False,
    tags=['backfill', 'spark']
) as dag:

    process_arctic_shift = SparkSubmitOperator(
        task_id='process_arctic_shift',
        application='/opt/spark/jobs/process_arctic_shift.py',
        conf={
            'spark.executor.memory': '4g',
            'spark.driver.memory': '2g'
        }
    )

    recalculate_rankings = PythonOperator(
        task_id='recalculate_all_rankings',
        python_callable=calculate_rankings,
        op_kwargs={'time_window': 'all_time'}
    )

    process_arctic_shift >> recalculate_rankings
```

---

## Scaling Considerations

### Current Scale (MVP)
- **Comments:** 10k/day = 3.65M/year (~2GB/year)
- **Products:** ~50 per category × 5 categories = 250 products
- **Ingestion:** Every 4 hours per category (6 batches/day)
- **Processing:** ~25 minutes per batch (sentiment + LLM)

### Future Scale (Production)
- **Comments:** 100k/day = 36.5M/year (~20GB/year)
- **Products:** ~500 per category × 10 categories = 5,000 products
- **Ingestion:** Every 2 hours (12 batches/day)

### Scaling Strategy

**When to scale up (>100k comments/day):**

1. **Database:**
   - Add read replicas for API queries
   - Partition `product_sentiment` by month (TimescaleDB automatic)
   - Add connection pooling (PgBouncer)

2. **Airflow:**
   - Increase parallelism settings
   - Add Celery executor with multiple workers
   - Scale horizontally (more worker nodes)

3. **Sentiment Analysis:**
   - Batch size tuning (currently 64, increase to 128-256)
   - GPU acceleration (run ABSA on GPU)
   - Model quantization (reduce memory footprint)

4. **LLM:**
   - Batch API calls (OpenAI supports batching)
   - Cache summaries (only regenerate weekly)
   - Use cheaper models (GPT-3.5-turbo or self-hosted Llama)

**When to consider Kafka (>500k comments/day):**
- At this scale, Kafka's throughput benefits outweigh operational overhead
- Multiple downstream consumers become necessary
- Real-time processing becomes valuable

---

## Rationale & Research

### Industry Best Practices Research

**Sources consulted:**
1. [Astronomer: Pass data between tasks](https://docs.astronomer.io/learn/airflow-passing-data-between-tasks)
2. [Data Pipeline Design Patterns - GeeksforGeeks](https://www.geeksforgeeks.org/system-design/data-pipeline-design-patterns-system-design/)
3. [Optimizing Azure Data Factory Pipelines](https://medium.com/@charaneswari04/optimizing-azure-data-factory-pipelines-10-performance-tuning-tricks-that-actually-work-4bb42e54323a)
4. [Building ETL pipeline with Airflow + Spotify](https://medium.com/apache-airflow/building-etl-pipeline-with-airflow-spotify-d1bccb2f4d13)
5. [Reddit Data Pipeline - GitHub](https://github.com/VivekaAryan/Reddit-Data-Pipeline)
6. [Airflow ETL Guide - Astronomer](https://www.astronomer.io/blog/etl-in-airflow-comprehensive-guide-efficient-data-pipelines/)

### Key Findings

**1. Intermediate storage is standard practice:**
> "For workflows, you should break up the steps into bite-size tasks so each step stores the intermediate results in a stage, so you can easily re-run from a specific task and debug what the output was at a particular step."

**2. Database staging is efficient:**
> "Introduce a staging layer by writing data to a fast intermediate store and then loading it to the final sink in bulk. This is especially important for cloud data warehouses."

**3. Airflow dominates ETL workloads:**
> "90% of respondents in the 2023 Apache Airflow survey use Airflow for ETL/ELT to power analytics use cases."

**4. Batch processing for scheduled workloads:**
> "Batch ETL is ideal for daily reports, syncing CRM to warehouse, or reconciling transactions... when a few hours delay is acceptable."

**5. Production examples:**
- Spotify: Daily ETL with Airflow (batch processing, not streaming)
- Reddit pipelines: Extract → S3 staging → Transform → Load pattern
- Netflix, Airbnb: Use Airflow for batch orchestration at scale

### Why This Architecture Is Production-Grade

✅ **Medallion Architecture** - Industry standard (Bronze → Silver → Gold)
✅ **Idempotent operations** - Can safely rerun any stage
✅ **Debuggable** - Inspect data at each layer
✅ **Testable** - Each stage can be unit tested
✅ **Auditable** - Immutable raw data preserved
✅ **Scalable** - Can handle 10x growth without redesign
✅ **Cost-effective** - No over-engineered components
✅ **Maintainable** - Simple enough for one engineer to manage

---

## Technology Stack Summary

| Component | Technology | Justification |
|-----------|-----------|---------------|
| Orchestration | Apache Airflow | Industry standard for batch ETL (90% adoption) |
| Database | PostgreSQL + TimescaleDB | Handles time-series data, scales to millions of rows |
| Ingestion | Python + PRAW | Official Reddit API wrapper, stable |
| Sentiment | HuggingFace DeBERTa | SOTA ABSA model, production-ready |
| Summarization | OpenAI GPT-4o-mini | Cost-effective ($1.50/month), high quality |
| Historical Processing | Apache Spark | Only tool that can handle multi-GB parquet files |
| API | FastAPI | Fast, async, type-safe |
| Frontend | React 19 | Modern, component-based |

---

## Migration Plan

### Phase 1: Remove Kafka, Add Database Staging ✅
1. Create database schema (6 tables)
2. Refactor `worker.py` to write to PostgreSQL instead of Kafka
3. Remove Kafka producers/consumers
4. Test end-to-end pipeline

### Phase 2: Integrate Airflow
1. Set up Airflow (Docker Compose)
2. Convert workers to Airflow DAGs
3. Add task dependencies and sensors
4. Test scheduling and parallelism

### Phase 3: Add LLM Features
1. Implement summarization DAG (GPT-4o-mini)
2. Implement featured comments selection
3. Update API endpoints
4. Frontend integration

### Phase 4: Historical Backfill
1. Download arctic_shift torrents (1-2 years)
2. Write Spark jobs for distributed processing
3. Backfill raw_comments and product_sentiment
4. Recalculate rankings with historical data

---

## Conclusion

**This architecture is:**
- ✅ Appropriate for the workload (batch processing, 10k comments/day)
- ✅ Based on production best practices (Medallion, Airflow-first)
- ✅ Scalable to 10x growth (100k comments/day)
- ✅ Simple enough to maintain (no over-engineering)
- ✅ Learning-focused (master Airflow, Spark, ETL patterns)

**We consciously chose NOT to use Kafka because:**
- ❌ Overkill for batch processing (4-hour intervals)
- ❌ Doesn't improve performance at our scale
- ❌ Adds operational complexity (Zookeeper, brokers, monitoring)
- ❌ Not needed for sequential processing (total pipeline: 25 min)

**The "extra" database read/write is:**
- ✅ Standard practice in production ETL
- ✅ Negligible performance impact (~1 second per batch)
- ✅ Justified by product requirements (display Reddit comments)
- ✅ Essential for debuggability and reprocessing

---

**Document Reviewers:**
- [ ] Architecture approved by: _____________
- [ ] Database schema reviewed by: _____________
- [ ] Scaling strategy validated by: _____________

**Next Steps:**
1. Implement database schema migrations
2. Refactor ingestion service for PostgreSQL
3. Set up Airflow development environment
4. Begin Phase 1 implementation
