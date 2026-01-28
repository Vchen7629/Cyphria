d# Cyphria Progress Report

**Last Updated:** 2026-01-26
**Status:** Data Ingestion ✓ | Sentiment Analysis ✓ | Ranking Calculator ✓ | LLM Summary ✓ | Orchestrator ✓ | Insights API ✓ (Enhanced with Valkey Caching) | Frontend ✓

---

## Overview

Successfully pivoted from sentiment analysis dashboard to **product ranking platform** using Reddit sentiment. Using batch ETL architecture with PostgreSQL + Airflow instead of streaming with Kafka.

**Product Vision:** Rank products (GPUs, headphones, monitors, etc.) based on Reddit community sentiment analysis across relevant subreddits, with AI-generated conversational summaries (TLDRs).

**Current Stage:** Backend data pipeline complete (ingestion, sentiment analysis, ranking, LLM summaries, orchestration). Insights API complete with Valkey caching, trending topics, and Prometheus metrics. Frontend UI complete with mock data. Next: Frontend backend integration.

---

## Architecture Changes

### Key Architectural Shift: Kafka → PostgreSQL + Airflo

**Previous Architecture (Deprecated):**
- Streaming pipeline with Kafka topics
- Data flow: Reddit → Kafka `raw-data` topic → Sentiment Service → Kafka `aggregated` topic

**New Architecture (Current):**
- Batch ETL with PostgreSQL + Airflow orchestration
- Medallion Architecture: Bronze (raw_comments) → Silver (product_sentiment) → Gold (product_rankings)
- Data flow: Reddit → PostgreSQL `raw_comments` table → Sentiment Service → PostgreSQL `product_sentiment` table
- See ARCHITECTURE.md for full details

**Rationale:**
- Batch processing better suited for micro-batches every 4 hours (not continuous streaming)
- Low throughput: ~10k comments/day = 3 comments/second (trivial for PostgreSQL)
- Removes operational overhead of Kafka + Zookeeper
- Industry standard: 90% of Airflow users use it for ETL/ELT batch processing
- Database staging allows easy debugging and reprocessing

---

## ✅ Completed: Data Ingestion Service (PostgreSQL Integration)

### What Was Built

**1. Post Fetching with Delay Strategy**
- `fetch_post_delayed()` in `backend/data_pipeline/ingestion/src/utils/fetch_post.py`
- Fetches posts from 24-48 hours ago (ensures comments have accumulated)
- Time-window filtering to get "complete" posts
- Configured for GPU subreddits: nvidia, amd, buildapc, gamingpc, pcbuild, hardware

**2. Comment Fetching**
- `fetch_comments()` in `backend/data_pipeline/ingestion/src/utils/fetch_comments.py`
- Uses `replace_more(limit=None)` to fetch all comments (including nested)
- Flattens comment tree into list
- Error handling for PRAW exceptions

**3. GPU Product Detection**
- `GPUDetector` class in `backend/data_pipeline/ingestion/src/preprocessing/gpu_detector.py`
- **Hybrid detection approach:**
  - Regex patterns for NVIDIA (RTX/GTX), AMD (RX), Intel (Arc)
  - Supports full names: "RTX 4090", "RX 7900 XTX", "Arc A770"
  - Supports bare model numbers: "4090", "1080 Ti" (validated against known models)
  - Filters false positives (random 4-digit numbers) using known model lists
- **Coverage:** NVIDIA 900-5000 series, AMD 5000-9000 series, Intel Arc A/B series
- Returns list of detected GPUs per comment

**4. Product Name Normalization**
- `GPUNameNormalizer` in `backend/data_pipeline/ingestion/src/product_utils/gpu_normalization.py`
- **Regex-based parsing approach:**
  - Normalizes "4090", "rtx 4090", "rtx4090" → "NVIDIA RTX 4090"
  - Normalizes "rx 7900 xtx", "7900 xtx" → "AMD RX 7900 XTX"
  - Proper capitalization: Ti, SUPER, XT, XTX
- **Deduplication:** Removes duplicate aliases before storage

**5. Comment Quality Filtering**
- `is_valid_comment()` in `backend/data_pipeline/ingestion/src/preprocessing/is_valid_comment.py`
- **Filters:**
  - Length: ≥20 characters (removes "lol", "nice", etc.)
  - Score: ≥1 upvote (removes downvoted/ignored comments)
  - Bot detection: Filters bots, moderators, automoderator
  - Deleted/removed comments

**6. Text Preprocessing Pipeline**
- URL removal: `remove_url()`
- Emoji removal: `demojify()`
- Language detection: `detect_english()` (only process English comments)
- Field extraction: `extract_relevant_fields()` (Pydantic `RedditComment` model)

**7. Database Integration (NEW)**
- Connection pooling with `psycopg` (PostgreSQL adapter)
- Batch insert with retry logic: `batch_insert_raw_comments()` in `backend/data_pipeline/ingestion/src/db_utils/queries.py`
- **Retry decorator:** `@retry_with_backoff` handles transient database errors with exponential backoff
- Writes to `raw_comments` table (Bronze layer) with:
  - comment_id, post_id, comment_body, detected_products (array)
  - subreddit, author, score, created_utc, category
  - sentiment_processed flag (default: FALSE)
- **Batch size:** 100 comments per batch for optimal performance
- **Conflict handling:** ON CONFLICT DO NOTHING (prevents duplicates)

**8. Worker Orchestration**
- `Worker` class in `backend/data_pipeline/ingestion/src/worker.py`
- **Pipeline flow:**
  1. Fetch posts from configured subreddits (24-48h delay)
  2. Fetch comments for each post
  3. Filter valid comments (quality checks)
  4. Detect GPU mentions
  5. Normalize product names
  6. Extract & preprocess comment text
  7. **Batch write to PostgreSQL** `raw_comments` table
- Clean separation of concerns (fetch, process, store)

**9. Data Model**
- `RedditComment` Pydantic model:
  - `comment_id`, `comment_body`, `subreddit`
  - `detected_products` (list of normalized GPU names)
  - `timestamp`, `score`, `author`, `post_id`

---

## ✅ Completed: Sentiment Analysis Service (PostgreSQL Migration)

### What Was Built

The sentiment analysis service has been successfully migrated from Kafka to PostgreSQL. The service now polls the database for unprocessed comments, runs ABSA sentiment analysis, and writes results back to PostgreSQL.

**1. Database Utilities**
- `db_utils/conn.py` - PostgreSQL connection pool using `psycopg_pool.ConnectionPool` (1-10 connections)
- `db_utils/queries.py` - Three core database functions:
  - `fetch_unprocessed_comments(conn, category, batch_size)` - Reads from `raw_comments` WHERE `sentiment_processed = FALSE`
  - `batch_insert_product_sentiment(conn, sentiments)` - Writes to `product_sentiment` with ON CONFLICT DO NOTHING
  - `mark_comments_processed(conn, comment_ids)` - Updates `raw_comments` SET `sentiment_processed = TRUE`
- `db_utils/retry.py` - Retry decorator with exponential backoff for transient database errors

**2. Worker Orchestration**
- `worker.py` - `StartService` class with complete lifespan management:
  - Database connection pool initialization with health check
  - ABSA model loading (DeBERTa v3 base)
  - Main polling loop: fetch → process → write → mark processed
  - Graceful shutdown handling (SIGTERM/SIGINT)
  - ThreadPoolExecutor for inference with timeout protection
  - Category-based processing (injected via `PRODUCT_CATEGORY` env var)

**3. Data Models**
- `core/types.py` - Pydantic models for type-safe data handling:
  - `UnprocessedComment`: comment_id, comment_body, detected_products, created_utc
  - `ProductSentiment`: comment_id, product_name, sentiment_score, created_utc

**4. Configuration**
- `core/settings_config.py` - Pydantic Settings for environment variable validation
  - Validates `PRODUCT_CATEGORY` against allowed list: GPU, LAPTOP, HEADPHONE
  - Case-insensitive validation with early failure on invalid category

**5. Structured Logging**
- `core/logger.py` - JSON-based structured logging for cloud/container environments
  - Event type tagging for filtering/querying
  - Pod name support for multi-pod deployments

**6. Processing Pipeline**
- `preprocessing/sentiment_analysis.py` - ABSA model with DeBERTa v3 base
  - Batched inference (64 pairs per batch)
  - Weighted sentiment score: -1*P_neg + 0*P_neu + 1*P_pos (range: -1 to 1)
  - 3-second timeout per batch
- `preprocessing/extract_pairs.py` - Extracts (comment_id, comment_body, product_name, created_utc) tuples

**7. Comprehensive Test Coverage (50+ tests)**

**Integration Tests:**
- `test_db_connection.py` (7 tests) - Pool creation, concurrent connections, exhaustion handling
- `test_fetch_unprocessed_comments.py` (16 tests) - Batch fetching, ordering, category filtering, edge cases
- `test_batch_insert_processed_comments.py` (10 tests) - Insertions, duplicates, transactions, boundary scores
- `test_mark_comments_processed.py` (13 tests) - Marking logic, idempotency, special characters
- `test_worker_run_completion.py` (3 tests) - Worker exits on completion, multi-batch processing
- `test_graceful_shutdown.py` (4 tests) - Shutdown flag, cleanup, no data loss

**Unit Tests:**
- `test_extract_pair.py` (4 tests) - Pair extraction edge cases
- `test_graceful_shutdown.py` (1 test) - Signal handler sets shutdown flag
- `test_retry.py` (6 tests) - Retry logic, exponential backoff, error classification

**Test Infrastructure:**
- Uses `testcontainers` PostgreSQL for isolated integration testing
- Module-scoped containers for performance
- Reusable pytest fixtures for mocked ABSA model and worker creation

### Key Implementation Details

**Transaction Management:**
- Insert sentiment scores AND mark comments processed in single transaction
- Ensures atomicity - no orphaned records on failure

**Idempotency:**
- `ON CONFLICT (comment_id, product_name) DO NOTHING` for safe re-runs
- Only marks comments that were actually `sentiment_processed = FALSE`

**Graceful Shutdown:**
- Signal handler sets `shutdown_requested` flag
- Current batch completes before exit
- Cleanup method closes pool and executor

**Processing Characteristics:**
- Batch fetch: 200 comments per iteration
- ABSA batch size: 64 pairs per inference call
- Processing order: FIFO by `created_utc` (oldest first)

---

## ✅ Completed: Ranking Calculator Service

### What Was Built

The ranking calculator service aggregates sentiment data from the Silver layer and computes product rankings for the Gold layer. It's designed to run daily via Airflow/cron with category and time window injected via environment variables.

**1. Worker Orchestration**
- `worker.py` - `RankingCalculatorWorker` class with complete lifespan management:
  - Database connection pool initialization with health check
  - Single-pass execution: fetch → calculate → write for one category/window
  - Graceful shutdown handling (SIGTERM/SIGINT)
  - Category and time window injected via `PRODUCT_CATEGORY` and `TIME_WINDOWS` env vars

**2. Database Utilities**
- `db_utils/conn.py` - PostgreSQL connection pool using `psycopg_pool.ConnectionPool`
- `db_utils/queries.py` - Two core database functions:
  - `fetch_aggregated_product_scores(conn, category, time_window)` - Aggregates from `product_sentiment` with time filtering
  - `batch_upsert_product_score(conn, scores)` - Writes to `product_rankings` with ON CONFLICT UPDATE
- `db_utils/retry.py` - Retry decorator with exponential backoff for transient database errors

**3. Calculation Utilities**
- `calculation_utils/bayesian.py` - IMDB Top 250 formula for Bayesian weighted scores:
  - Formula: `WR = (v/(v+m)) × R + (m/(v+m)) × C`
  - Prevents manipulation from low-sample products (pulled toward category average)
- `calculation_utils/grading.py` - Grade and rank assignment:
  - `assign_grades()` - Converts Bayesian scores to letter grades (S, A, A-, B, B-, C, C-, D, D-, F, F-)
  - `assign_ranks()` - Uses scipy.rankdata for ranking (highest score = rank 1)
- `calculation_utils/badge.py` - Badge assignment:
  - `assign_is_top_pick()` - True for rank 1
  - `assign_is_most_discussed()` - True for highest mention count
  - `assign_has_limited_data()` - True if below minimum mentions threshold

**4. Data Models**
- `core/types.py` - Pydantic models for type-safe data handling:
  - `SentimentAggregate`: product_name, avg_sentiment, mention_count, positive/negative/neutral counts, approval_percentage
  - `ProductScore`: Full ranking object with rank, grade, bayesian_score, badges, calculation_date

**5. Configuration**
- `core/settings_config.py` - Pydantic Settings for environment variable validation:
  - `product_category`: Validated against allowed list (GPU, LAPTOP, HEADPHONE)
  - `time_windows`: "90d" or "all_time"
  - `bayesian_params`: Minimum mentions threshold for Bayesian calculation
  - `grade_thresholds`: Configurable thresholds for grade boundaries

**6. Comprehensive Test Coverage**

**Unit Tests:**
- `test_bayesian.py` - Bayesian score calculation edge cases
- `test_assign_grades.py` - Grade assignment across all thresholds
- `test_assign_ranks.py` - Ranking with ties and edge cases
- `test_assign_top_pick.py` - Top pick badge assignment
- `test_assign_most_discussed.py` - Most discussed badge with ties
- `test_has_limited_data.py` - Limited data badge threshold

**Integration Tests:**
- `test_db_connection.py` - Pool creation and health checks
- `test_fetch_aggregated_product_scores.py` - Aggregation queries, time filtering, category filtering
- `test_batch_upsert_product_score.py` - Upserts, conflicts, updates
- `test_graceful_shutdown.py` - Shutdown flag, cleanup, resource release

### Key Implementation Details

**Aggregation Query:**
- Groups by `product_name` from `product_sentiment` table
- Calculates: AVG(sentiment_score), COUNT(*), positive/negative/neutral counts
- Filters by category and time window (90d uses `NOW() - INTERVAL`, all_time has no filter)
- Approval percentage: positive_count / total * 100

**Grade Thresholds (Bayesian score range -1 to +1):**
- S: >= 0.95, A: >= 0.9, A-: >= 0.85, B: >= 0.75, B-: >= 0.7
- C: >= 0.45, C-: >= 0.1, D: >= -0.1, D-: >= -0.3, F: >= -0.5, F-: < -0.5

**Upsert Strategy:**
- `ON CONFLICT (product_name, time_window) DO UPDATE` - Updates existing rankings
- Allows daily recalculation without duplicates

**Airflow Integration Design:**
- Worker processes ONE category + ONE time window per run
- Airflow calls worker multiple times with different env var combinations
- Example: GPU/90d, GPU/all_time, LAPTOP/90d, LAPTOP/all_time, etc.

---

## ✅ Completed: LLM Summary Service

### What Was Built

The LLM Summary service generates concise, conversational product summaries (TLDRs) from top Reddit comments using OpenAI's API. Built with FastAPI, background thread execution, and the same async pattern as other services (POST /run + GET /status polling).

**1. FastAPI Architecture with Background Execution**
- FastAPI app with async routes and ThreadPoolExecutor (max_workers=1)
- POST /run endpoint: Triggers summary generation, returns "started" immediately
- GET /status endpoint: Airflow HttpSensor polls until "completed"/"cancelled"/"failed"
- Background thread runs processing to prevent blocking /status polls
- Thread-safe JobState class for tracking progress

**2. Database Utilities**
- `db/conn.py` - PostgreSQL connection pool using psycopg_pool
- `db/queries.py` - Three core query functions:
  - `fetch_unique_products(conn, time_window, min_comments=10)` - Gets products with sufficient comments
  - `fetch_top_comments_for_product(conn, product_name, time_window)` - Returns balanced comments (10 positive, 10 negative, 5 neutral)
  - `upsert_llm_summaries(conn, product_name, tldr, time_window, model_used)` - Stores summaries with ON CONFLICT UPDATE
- `db/retry.py` - Retry decorator with exponential backoff for transient errors

**3. LLM Integration**
- `llm_client/prompts.py` - System prompt and user prompt builder
  - Conversational, enthusiastic tone (uses "legend", "monster", "king", "endgame", "tank")
  - 8-16 words total (1-2 sentences)
  - Mentions most praised aspect and common criticism
  - Examples by category: Audio, Computing, Outdoor, Fitness
- `llm_client/response_parser.py` - TLDR extraction and validation
- `llm_client/retry.py` - LLM API retry logic with exponential backoff

**4. Summary Service Worker**
- `summary_service.py` - LLMSummaryService class with complete pipeline:
  - `_fetch_products_with_comments()` - Fetches all products + top comments
  - `_generate_summary()` - Calls OpenAI API with retry logic
  - `_insert_summary()` - Upserts to product_summaries table
  - `_run_summary_pipeline()` - Orchestrates full pipeline
  - `run_single_cycle()` - Background thread entry point, updates JobState

**5. Job State Management**
- `api/job_state.py` - Thread-safe JobState class:
  - `create_job()` - Initialize new job with time_window
  - `complete_job()` - Mark as COMPLETED/CANCELLED with result
  - `fail_job()` - Mark as FAILED with error message
  - `get_current_job()` - Get current job state
  - `is_running()` - Check if job is in progress

**6. API Routes**
- `api/routes.py` - Four endpoints:
  - POST /run - Triggers summary generation (body: {time_window: "90d"|"all_time"})
  - GET /status - Returns CurrentJob (status, time_window, started_at, completed_at, result, error)
  - GET /health - Database connectivity health check
  - GET /ready - Readiness probe for Kubernetes

**7. Configuration**
- `core/settings_config.py` - Pydantic Settings for environment variables:
  - OPENAI_API_KEY - OpenAI API key
  - LLM_MODEL - Model name (default: "gpt-4o-mini")
  - FASTAPI_PORT - Port for FastAPI server
  - DATABASE_URL - PostgreSQL connection string

**8. Structured Logging**
- `core/logger.py` - JSON-based structured logging
  - Event type tagging for filtering/querying
  - Pod name support for multi-pod deployments

**9. Comprehensive Test Coverage**

**Unit Tests:**
- `test_build_user_prompt.py` - Prompt generation with positive/negative/neutral splits
- `test_format_comments.py` - Comment list formatting
- `test_parse_tldr.py` - TLDR extraction and validation edge cases
- `test_create_job.py` - Job creation validation
- `test_complete_job.py` - Job completion with result
- `test_fail_job.py` - Job failure with error message
- `test_is_running.py` - Running state checks
- `test_signal_handler.py` - Graceful shutdown handling
- `test_run_endpoint.py` - /run endpoint validation
- `test_status_endpoint.py` - /status endpoint polling
- `test_ready_endpoint.py` - Readiness probe
- `test_run_single_cycle.py` - Full cycle execution
- `test_lifespan.py` - App startup/shutdown lifecycle

**Integration Tests:**
- `test_fetch_unique_products.py` - Product fetching with min_comments threshold
- `test_fetch_top_comments_for_product.py` - Balanced comment retrieval
- `test_upsert_llm_summaries.py` - Summary upsert with conflict handling
- `test_db_connection.py` - Connection pool health checks
- `test_cancel_requested.py` - Cancellation flag handling
- `test_health_endpoint.py` - Health check with database

### Key Implementation Details

**Top Comments Query:**
- Window function (ROW_NUMBER) partitioned by sentiment_category (positive/negative/neutral)
- Sentiment thresholds: score > 0.2 (positive), < -0.2 (negative), else neutral
- Takes top 10 positive, top 10 negative, top 5 neutral ordered by Reddit score
- Time window filtering: 90d uses NOW() - INTERVAL, all_time has no filter

**LLM Prompt Engineering:**
- System prompt enforces strict format: 8-16 words, conversational tone, no emojis
- User prompt provides product name + formatted comments (numbered lists)
- Examples provided for different categories to guide tone
- Encourages punchy language: "legend", "monster", "endgame", "just buy it"

**Upsert Strategy:**
- `ON CONFLICT (product_name, time_window) DO UPDATE` - Regenerates summaries on re-run
- Tracks model_used and generated_at timestamp
- Allows monthly regeneration with fresher comments

**Background Thread Pattern:**
- ThreadPoolExecutor prevents blocking FastAPI event loop
- /run returns "started" immediately, processing happens in background
- /status endpoint allows Airflow HttpSensor to poll for completion
- Same pattern used across ingestion, sentiment_analysis, ranking_calculator

**Time Windows:**
- Worker processes ONE time window per run (injected via request body)
- Airflow calls worker twice: once for "all_time", once for "90d"
- Sequential execution in DAG: all_time → wait → 90d → wait

---

## ✅ Completed: Orchestrator Service (Airflow + HTTP Operators + HttpSensor)

### What Was Built

The orchestrator service uses Apache Airflow to coordinate all data pipeline services. It uses **HTTP Operators + HttpSensor** pattern: services run as persistent FastAPI pods with async `/run` endpoints (returns "started" immediately) and `/status` endpoints (polled by HttpSensor until completion).

**1. HTTP Operator + HttpSensor Architecture**
- All services (Ingestion, Sentiment Analysis, LLM Summary, Ranking) run as persistent FastAPI pods
- Airflow uses `HttpOperator` to POST to `/run` endpoints with category/config payloads
- Services return `{status: "started"}` immediately and process in background thread
- `HttpSensor` polls `/status` endpoint until `{status: "completed"|"cancelled"|"failed"}`
- Benefits: No blocking, Airflow worker slots freed during processing, prevents timeout issues

**2. Service Connections**
- `ingestion_service`: `http://ingestion-service.data-pipeline.svc.cluster.local:8000`
- `sentiment_analysis_service`: `http://sentiment-analysis-service.data-pipeline.svc.cluster.local:8000`
- `llm_summary_service`: `http://llm-summary-service.data-pipeline.svc.cluster.local:8000`
- `product_ranking_service`: `http://product-ranking-service.data-pipeline.svc.cluster.local:8000`

**3. Product Category Sentiment Analysis DAGs**
- `product_gpu_sentiment_analysis` - Runs daily (time TBD)
- `product_laptop_sentiment_analysis` - Runs daily (time TBD)
- `product_headphone_sentiment_analysis` - Runs daily (time TBD)

**Task Structure:** `ingest → wait → sentiment_analysis → wait` (sequential with HttpSensor waits)

Each DAG has 4 tasks:
- **Ingest Task:** POST /run to ingestion service with `{category, subreddits: [list]}`
- **Wait Ingest:** HttpSensor polls ingestion /status until completed
- **Sentiment Task:** POST /run to sentiment service with `{category}`
- **Wait Sentiment:** HttpSensor polls sentiment /status until completed

**4. Product Ranking DAGs**
- `product_gpu_ranking` - Runs daily (time TBD)
- `product_laptop_ranking` - Runs daily (time TBD)
- `product_headphone_ranking` - Runs daily (time TBD)

**Task Structure:** `ranking_all_time → wait → ranking_90d → wait` (sequential with HttpSensor waits)

Each ranking DAG has 4 tasks:
- **All-Time Ranking:** POST /run to ranking service with `{category, time_window: "all_time"}`
- **Wait All-Time:** HttpSensor polls ranking /status until completed
- **90-Day Ranking:** POST /run to ranking service with `{category, time_window: "90d"}`
- **Wait 90-Day:** HttpSensor polls ranking /status until completed

**5. Product Summary DAG (NEW)**
- `product_summary` - Runs monthly on 1st at midnight (0 0 1 * *)

**Task Structure:** `llm_summary_all_time → wait → llm_summary_90d → wait` (sequential with HttpSensor waits)

This DAG has 4 tasks:
- **All-Time Summary:** POST /run to LLM summary service with `{time_window: "all_time"}`
- **Wait All-Time:** HttpSensor polls LLM /status until completed
- **90-Day Summary:** POST /run to LLM summary service with `{time_window: "90d"}`
- **Wait 90-Day:** HttpSensor polls LLM /status until completed

**6. Configuration (Pydantic Settings)**
- `PRODUCTION_MODE`: True by default
- `MAX_ACTIVE_RUNS`: 1 (prevents overlapping DAG runs)
- `NUM_RETRIES`: 2 attempts
- `RETRY_DELAY`: 5 minutes with exponential backoff
- `MAX_RETRY_DELAY`: 30 minutes
- `EXECUTION_TIMEOUT`: 1 hour per task
- `STATUS_POLL_INTERVAL`: 30 seconds (HttpSensor poke interval)

**7. Error Handling**
- Exponential backoff retries (up to 30 minutes)
- Execution timeout (1 hour per task)
- On-failure callback for alerting (placeholder for Slack/Discord)
- Response validation:
  - HttpOperator checks for `status == "started"`
  - HttpSensor checks for `status in ["completed", "cancelled", "failed"]`

**8. Comprehensive Test Coverage**

**Unit Tests (16 tests):**
- `test_product_category_pipeline_dag.py` (3 tests) - DAG configuration validation
- `test_product_category_pipeline_tasks.py` (8 tests) - Task configs, payloads, dependencies
- `test_product_category_ranking_dag.py` (3 tests) - Ranking DAG structure
- `test_product_category_ranking_tasks.py` (2 tests) - Ranking task configs

**Integration Tests (13 tests with K3s + testcontainers):**
- DAG loading validation
- Success scenarios (completed/cancelled status)
- Full pipeline execution with task sequencing
- Parallel ranking task execution
- HTTP 500 error handling
- Invalid status response handling
- Connection failure scenarios
- Execution timeout scenarios
- Upstream task failure propagation
- Parallel task independence
- On-failure callback validation

**Test Infrastructure:**
- K3s cluster spawned via testcontainers
- Mock HTTP service with configurable responses (status, delays, errors)
- Namespace isolation with Kubernetes DNS
- ConfigMap-based DAG injection into Airflow pod

### Key Implementation Details

**HTTP Operator + HttpSensor Pattern:**
```python
# Trigger processing (returns "started" immediately)
trigger_task = HttpOperator(
    task_id="ingest_gpu_comments",
    http_conn_id="ingestion_service",
    endpoint="/run",
    method="POST",
    headers={"Content-Type": "application/json"},
    data=json.dumps({"category": "GPU", "subreddits": [...]}),
    response_check=lambda response: response.json()["status"] == "started",
    retries=2,
    retry_delay=timedelta(minutes=5),
    retry_exponential_backoff=True,
    max_retry_delay=timedelta(minutes=30),
    execution_timeout=timedelta(hours=1),
)

# Wait for completion (polls /status endpoint)
wait_task = HttpSensor(
    task_id="wait_ingest_gpu_comments",
    http_conn_id="ingestion_service",
    endpoint="/status",
    response_check=lambda response: response.json()['status'] in ["completed", "cancelled"],
    poke_interval=30,  # Poll every 30 seconds
    timeout=3600,  # 1 hour timeout
    mode="reschedule",  # Free up worker slot between pokes
    retries=2,
    retry_delay=timedelta(minutes=5)
)

trigger_task >> wait_task
```

**Why HTTP Operators + HttpSensor over KubernetesPodOperator:**
- No pod startup latency (services are always running)
- Background thread execution prevents blocking Airflow workers
- HttpSensor frees worker slots between polls (mode="reschedule")
- Prevents timeout issues - services can run for hours without blocking
- Easier debugging (check service logs, not ephemeral pod logs)
- Better resource utilization (shared pods for multiple runs)
- Simpler scaling (just scale the FastAPI deployment)
- Models stay loaded in memory (sentiment/LLM models)

**Background Thread Pattern in All Services:**
- POST /run → ThreadPoolExecutor.submit(service.run_single_cycle, job_state) → return {status: "started"}
- Service processes in background thread, updates JobState
- GET /status → Returns current JobState (status, progress, error if failed)
- Airflow HttpSensor polls /status until status != "running"

---

## ✅ Completed: Insights API (FastAPI + Valkey Caching)

### What Was Built

The Insights API is a production-ready FastAPI REST API that exposes product rankings and sentiment data to the frontend. Built with async/await patterns, SQLAlchemy AsyncIO, Valkey caching layer, Prometheus metrics, and comprehensive test coverage.

**1. API Architecture**
- FastAPI with async routes and dependency injection
- AsyncIO SQLAlchemy with asyncpg driver for PostgreSQL
- **Valkey (Redis-compatible) caching layer** with async connection pool
- Connection pooling: PostgreSQL (pool_size=10, max_overflow=20), Valkey (configurable max_connections)
- Lifespan management: DB health check on startup, graceful pool disposal on shutdown
- **Prometheus metrics** for database queries and cache operations
- Structured JSON logging with event tracking
- Client IP extraction middleware for view tracking

**2. Endpoints Implemented**

**Home Endpoints (`/api/v1/home`):**
- `GET /api/v1/home/trending/product_topics` - Weekly trending topics (top 6)
  - Uses Valkey sorted sets (ZREVRANGE) for real-time trending calculation
  - Weekly auto-reset via time-based cache keys (`trending:topics:2026-W04`)
  - Response: List of topics with view counts

**Topic Endpoints (`/api/v1/topic`):**
- `GET /api/v1/topic/products` - Ranked products for topic with **Valkey caching**
  - Query params: `product_topic` (required), `time_window` ("all_time" | "90d")
  - Cache TTL: 20 minutes (1200s) - aligns with 30-min processing schedule
  - **IP-based view tracking**: Increments trending topic count only for unique IPs per week
  - Response: List of ranked products with grades, scores, badges, TLDRs
- `GET /api/v1/topic/total_products_ranked` - Total products ranked count for topic
  - Query params: `product_topic`
  - Response: Integer count
- `GET /api/v1/topic/total_comments` - Total comments count for topic and time window
  - Query params: `product_topic`, `time_window`
  - Response: Integer count

**Category Endpoints (`/api/v1/category`):**
- `GET /api/v1/category/top_mentioned_products` - Top 6 most mentioned products across all topics in category
  - Query params: `category` (required)
  - Cache TTL: 30 minutes (1800s)
  - Response: List of products with name, grade, mention_count, product_topic, category
- `GET /api/v1/category/total_products_count` - Total product count for category
  - Query params: `category`
  - Response: Integer count
- `GET /api/v1/category/topic_most_mentioned_product` - Top 3 products for specific topic
  - Query params: `product_topic`
  - Response: List of products with name and grade

**Product Endpoints (`/api/v1/product`):**
- `GET /api/v1/product/sentiment_scores` - Sentiment breakdown for a product
  - Query params: `product_name`, `time_window`
  - Response: positive_count, neutral_count, negative_count
- `GET /api/v1/product/top_comments` - Top 5 Reddit comments with **Valkey caching**
  - Query params: `product_name`, `time_window`
  - Cache TTL: 30 minutes (1800s)
  - Response: List of comments with text, Reddit link, score, created_utc
- `GET /api/v1/product/search` - Product search with pagination and **Valkey caching**
  - Query params: `q` (search query), `current_page` (pagination)
  - Cache TTL: 10 minutes (600s)
  - Features: Case-insensitive ILIKE, prefix matches first, SQL injection safe, pagination
  - Response: List of products with pagination metadata (current_page, total_pages)

**3. Valkey Caching Layer**

**Cache Architecture:**
- `db_utils/cache_conn.py` - Valkey async connection pool with configurable max_connections
- `db_utils/cache_commands.py` - Cache utilities:
  - `get_cache_value()` - Fetch from cache, deserialize to Pydantic model, graceful fallback to DB
  - `set_cache_value()` - Write to cache with TTL, optional callback for side effects (e.g., trending increment)
  - `get_weekly_trending_key()` - Generate weekly trending key (`trending:topics:2026-W04`)
  - `increment_trending_topic()` - Increment topic view count in sorted set with IP-based deduplication

**Caching Strategy:**
- **Cache-aside pattern**: Check cache first, fallback to DB, populate cache on miss
- **TTL-based expiry**: Different TTLs for different endpoints (10-30 minutes)
- **Weekly trending reset**: Trending topics auto-reset each week via ISO week-based cache keys
- **IP-based view deduplication**: Prevents refresh spam using `viewed:{topic}:{ip}:{week}` keys with NX flag
- **Graceful degradation**: If cache is unavailable, endpoints fall back to database queries

**Cache Metrics:**
- Prometheus `cache_operation_duration_seconds` histogram
- Labels: `operation` (get/set), `hit` (true/false)
- Buckets: 1ms to 250ms (cache is faster than DB)

**4. Database Layer**

**Connection & Queries:**
- `db_utils/pg_conn.py` - AsyncIO SQLAlchemy engine and session factory
- `db_utils/retry.py` - Retry decorator with exponential backoff for transient errors

**Query Modules:**
- `db_utils/product_queries.py`:
  - `fetch_product_sentiment_scores()` - Sentiment breakdown counts
  - `fetch_top_reddit_comments()` - Top comments ordered by Reddit score
  - `fetch_matching_product_name()` - Paginated search with ILIKE, prefix ordering
- `db_utils/category_queries.py`:
  - `fetch_top_mentioned_products()` - Top 6 products across category topics
  - `fetch_total_products_count()` - Total product count for category
  - `fetch_topic_top_mentioned_products()` - Top 3 products for specific topic
- `db_utils/topic_queries.py`:
  - `fetch_products()` - Ranked products for topic with time window filtering
  - `fetch_total_comments()` - Total comments count for topic
  - `fetch_total_products_ranked()` - Total products ranked for topic

**5. Data Validation (Pydantic Schemas)**
- `schemas/product.py` - RankedProduct, TopMentionedProduct, CategoryTopMentionedProduct
- `schemas/comment.py` - TopComment model (text, link, score, created_utc)
- `schemas/response.py` - Typed API response wrappers (SearchProductResponse, GetRankedProductsResponse, etc.)
- `schemas/queries.py` - Database query result models (FetchProductsResult, FetchTopRedditCommentsResult, etc.)
- `schemas/home.py` - TrendingTopic, TrendingTopicsResponse

**6. Middleware**
- `middleware/metrics.py` - Prometheus instrumentation:
  - `db_query_duration` histogram (0.01s to 2.5s buckets) with labels: query_type, query_name, table
  - `cache_operation_duration` histogram (0.001s to 0.25s buckets) with labels: operation, hit
  - FastAPI request instrumentation (status codes, latency, in-progress requests)
- `middleware/get_client_ip.py` - Extract client IP from X-Forwarded-For header for view tracking
- `middleware/topic_category_mapping.py` - Topic-to-category mapping helper

**7. Comprehensive Test Coverage (60+ tests across 31 test files)**

**Integration Tests (9 files with testcontainers PostgreSQL):**
- `test_get_ranked_products_list.py` - Topic products endpoint, caching, time window filtering
- `test_get_top_comments_endpoint.py` - Top comments, caching, score ordering, sentiment_processed filtering
- `test_get_sentiment_scores_endpoint.py` - Sentiment breakdown, null handling, parameter validation
- `test_get_product_by_name_endpoint.py` - Search, pagination, SQL injection prevention, wildcard escaping
- `test_get_top_mentioned_products_endpoint.py` - Category top products, caching
- `test_get_top_mentioned_products_for_topic_endpoint.py` - Topic top products
- `test_get_total_products_count_endpoint.py` - Category product count
- `test_get_total_products_ranked_endpoint.py` - Topic ranked count
- `test_get_total_comments_endpoint.py` - Topic comment count with time window filtering

**Unit Tests (13 files):**
- `test_get_top_mentioned_product_endpoint.py` - Topic endpoint unit tests
- `test_get_topics_for_category.py` - Category mapping tests
- `test_get_top_mentioned_products_for_topic_endpoint.py` - Topic products unit tests
- `test_lifespan.py` - Startup health check failure, app state initialization, cleanup

### Key Implementation Details

**Valkey Caching Pattern:**
```python
# Check cache first
if cache:
    cached_response = await get_cache_value(cache, cache_key, logger, ResponseModel)
    if cached_response:
        return cached_response

# Cache miss - query database
db_result = await fetch_from_db(...)

# Populate cache with TTL
if cache:
    await set_cache_value(cache, cache_key, api_response, ttl_seconds, logger)
```

**Weekly Trending with IP Deduplication:**
- Trending key format: `trending:topics:2026-W04` (auto-resets each week)
- View tracking: `viewed:{topic}:{client_ip}:{week_number}` with 7-day TTL
- Uses Valkey SET with NX (only set if not exists) to prevent duplicate views
- ZINCRBY on sorted set only if IP hasn't viewed topic this week
- ZREVRANGE to fetch top 6 trending topics

**Security Features:**
- SQL injection prevention via parameterized queries
- SQL wildcard escaping (%, _ treated as literals in search)
- Input validation with FastAPI's Query() and Literal types
- Pattern validation for product names and topics (no leading/trailing whitespace)

**Resilience:**
- Exponential backoff retry decorator for database operations
- Retryable PG errors: serialization_failure, deadlock_detected, connection_failure
- Connection pool health checks (pool_pre_ping=True)
- Graceful cache degradation: If cache unavailable, fall back to database
- Cache operation error handling with logging (doesn't fail requests)

**Time Window Filtering:**
- `all_time`: No date filter
- `90d`: `WHERE created_utc >= NOW() - INTERVAL '90 days'`

**Pagination:**
- Product search supports pagination with `current_page` query param
- Returns `current_page` and `total_pages` in response
- Default page size configurable (e.g., 10 results per page)

**Prometheus Metrics:**
- Database query duration tracking per query type, name, and table
- Cache operation duration tracking with hit/miss labels
- HTTP request metrics (status codes, latency, request count)
- Exposed on `/metrics` endpoint for scraping

---

## 📋 Code Review Findings

### Best Practices Implemented ✓

1. ✅ **Single Responsibility:** Each function does one thing well
2. ✅ **Type Hints:** Comprehensive type annotations throughout
3. ✅ **Error Handling:** Try-except blocks with logging
4. ✅ **Pydantic Models:** Type-safe data validation
5. ✅ **Docstrings:** Clear documentation for all functions
6. ✅ **Separation of Concerns:** Utils, preprocessing, core separated

---

## 🗂️ Current Architecture (PostgreSQL + Airflow)

### Medallion Architecture: Bronze → Silver → Gold

```
┌─────────────────────────────────────────────────────────────┐
│ Data Sources (Reddit API)                                   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Data Ingestion Service (COMPLETED ✓)                        │
├─────────────────────────────────────────────────────────────┤
│ • Fetch posts (24-48h delay) from GPU subreddits           │
│ • Fetch all comments from posts                             │
│ • Filter comments (length, score, bots)                     │
│ • Detect GPU mentions (regex + known models)                │
│ • Normalize product names (in-memory mapping)               │
│ • Preprocess text (URL removal, demojify, language check)   │
│ • Batch write to PostgreSQL raw_comments table              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL: Bronze Layer - raw_comments table               │
├─────────────────────────────────────────────────────────────┤
│ • comment_id, post_id, comment_body                         │
│ • detected_products (TEXT[])                                │
│ • subreddit, author, score, created_utc, category           │
│ • sentiment_processed (BOOLEAN, default: FALSE)             │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Sentiment Analysis Service (COMPLETED ✓)                    │
├─────────────────────────────────────────────────────────────┤
│ • Read unprocessed comments (sentiment_processed = FALSE)   │
│ • Extract product pairs from detected_products array        │
│ • Run ABSA sentiment analysis (DeBERTa model, batched)      │
│ • Write to product_sentiment table                          │
│ • Mark comments as processed (sentiment_processed = TRUE)   │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL: Silver Layer - product_sentiment table          │
├─────────────────────────────────────────────────────────────┤
│ • comment_id, product_name, sentiment_score                 │
│ • sentiment_label (positive/negative/neutral)               │
│ • subreddit, comment_score, created_utc, analyzed_at        │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Ranking Calculator Service (COMPLETED ✓)                    │
├─────────────────────────────────────────────────────────────┤
│ • Run daily at 2 AM UTC (scheduled via Airflow or cron)    │
│ • Aggregate sentiment data from product_sentiment table     │
│ • Calculate Bayesian scores (IMDB Top 250 formula)          │
│ • Assign grades (S, A, A-, B, B-, C, C-, D, D-, F, F-)      │
│ • Assign badges (top_pick, most_discussed, limited_data)    │
│ • Write to product_rankings table (Gold layer)              │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL: Gold Layer - product_rankings table             │
├─────────────────────────────────────────────────────────────┤
│ • product_name, category, time_window, rank, grade          │
│ • bayesian_score, avg_sentiment, approval_percentage        │
│ • mention_count, positive/negative/neutral counts           │
│ • badges (is_top_pick, is_most_discussed, has_limited_data) │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ LLM Summary Service (COMPLETED ✓)                           │
├─────────────────────────────────────────────────────────────┤
│ • Fetch unique products (min 10 comments)                   │
│ • Fetch top 25 comments (10 pos, 10 neg, 5 neutral)         │
│ • Generate conversational TLDRs using OpenAI API            │
│ • 8-16 words, punchy tone ("legend", "monster", "endgame")  │
│ • Write to product_summaries table                          │
│ • Monthly regeneration (ON CONFLICT UPDATE)                 │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL: Gold Layer - product_summaries table            │
├─────────────────────────────────────────────────────────────┤
│ • product_name, tldr, time_window, model_used, generated_at │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Insights API (COMPLETED ✓)                                   │
├─────────────────────────────────────────────────────────────┤
│ • GET /api/v1/category                                      │
│ • GET /api/v1/category/products?category=X&time_window=Y    │
│ • GET /api/v1/product/view_more?product_name=X&time_window=Y│
│ • GET /api/v1/product/top_comments?product_name=X&...       │
│ • GET /api/v1/product/search?q={query}                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ Frontend (TODO)                                             │
└─────────────────────────────────────────────────────────────┘
```

### Airflow Orchestration (COMPLETED ✓)
- **Sentiment Analysis DAGs:** Per-category with ingest → wait → sentiment → wait (daily)
- **Ranking DAGs:** Per-category with all_time → wait → 90d → wait (daily)
- **Summary DAG:** Product summary with all_time → wait → 90d → wait (monthly)
- **HTTP Operators + HttpSensor:** Calls persistent FastAPI pods via /run, polls /status until done
- **Background Thread Pattern:** All services return "started" immediately, process in background
- **Future:** Historical backfill DAG (manual trigger, one-time with Spark)

---

## 📊 Pipeline Flow (PostgreSQL Architecture)

```
┌─────────────────────┐
│ Data Ingestion      │
│ (COMPLETED ✓)       │
│ - Fetch posts/      │
│   comments          │
│ - Filter quality    │
│ - Detect GPUs       │
│ - Normalize names   │
│ - Preprocess text   │
│ - Batch write       │
└──────┬──────────────┘
       │ PostgreSQL Write (Bronze Layer)
       │ raw_comments table
       │ {comment_id, post_id, comment_body, detected_products: ['NVIDIA RTX 4090'],
       │  subreddit, author, score, created_utc, category, sentiment_processed: FALSE}
       ↓
┌─────────────────────┐
│ Sentiment Analysis  │
│ (COMPLETED ✓)       │
│ - Read unprocessed  │
│ - Extract pairs     │
│ - Run ABSA model    │
│ - Score: -1 to 1    │
│ - Write results     │
│ - Mark processed    │
└──────┬──────────────┘
       │ PostgreSQL Write (Silver Layer)
       │ product_sentiment table
       │ {comment_id, product_name: "NVIDIA RTX 4090", sentiment_score: 0.847,
       │  sentiment_label: "positive", subreddit, comment_score, created_utc, analyzed_at}
       │
       │ PostgreSQL Update (Bronze Layer)
       │ UPDATE raw_comments SET sentiment_processed = TRUE
       ↓
┌─────────────────────┐
│ Ranking Calculator  │
│ (COMPLETED ✓)       │
│ - Aggregate data    │
│ - Bayesian scoring  │
│ - "90d"/"all_time"  │
│   time windows      │
│ - Assign grades     │
│ - Assign badges     │
└──────┬──────────────┘
       │ PostgreSQL Write (Gold Layer)
       │ product_rankings table
       │ {product_name, rank, grade, bayesian_score, avg_sentiment,
       │  mention_count, time_window, ...}
       ↓
┌─────────────────────┐
│ LLM Summary Service │
│ (COMPLETED ✓)       │
│ - Fetch unique      │
│   products (min 10) │
│ - Fetch top 25      │
│   comments balanced │
│ - OpenAI API call   │
│ - 8-16 word TLDRs   │
│ - Punchy tone       │
└──────┬──────────────┘
       │ PostgreSQL Write (Gold Layer)
       │ product_summaries table
       │ {product_name, tldr, time_window, model_used, generated_at}
       ↓
┌─────────────────────┐
│ Insights API        │
│ (COMPLETED ✓)       │
│ - GET /category     │
│ - GET /products     │
│ - GET /search       │
│ - GET /top_comments │
│ - GET /view_more    │
└──────┬──────────────┘
       │ REST API
       ↓
┌─────────────────────┐
│ Frontend            │
│ (COMPLETED ✓)       │
│ - Product rankings  │
│ - Grade display     │
│ - Time windows      │
│ - TLDR summaries    │
│ - Mock data (needs  │
│   API integration)  │
└─────────────────────┘
```

---

## 🎯 GPU PoC Scope

**Goal:** Prove the concept with GPUs before expanding to other categories.

**Subreddits (for full PoC):**
- ✅ r/nvidia (currently enabled)
- ⏳ r/amd
- ⏳ r/buildapc
- ⏳ r/hardware

**GPU Coverage (~20 products for PoC):**
- NVIDIA: RTX 4090, 4080, 4070 Ti, 4070, 3090, 3080, 3070, 3060 Ti
- AMD: RX 7900 XTX, 7900 XT, 7800 XT, 6950 XT, 6900 XT, 6800 XT
- Intel: Arc A770, A750

**Success Criteria:**
1. ✅ Fetch & filter GPU-related comments from Reddit
2. ✅ Normalize GPU name variations to canonical format
3. ✅ Write comments to PostgreSQL raw_comments table (Bronze layer)
4. ✅ Migrate sentiment analysis service to PostgreSQL
5. ✅ Write sentiment results to product_sentiment table (Silver layer)
6. ✅ Aggregate sentiment data and compute product rankings (Gold layer)
7. ✅ Generate conversational TLDRs using LLM (OpenAI API)
8. ✅ Orchestrate pipeline with Airflow (HttpOperator + HttpSensor pattern)
9. ✅ Build Insights API to serve ranked products to frontend
10. ✅ Build Frontend UI with all pages, components, filtering
11. ⏳ Connect Frontend to Insights API (replace mock data with real data)

---

## 📝 Technical Decisions Made

### Data Collection & Processing
1. **Delayed Fetching (24-48h):** Ensures posts have accumulated comments before processing
2. **Comment-Level Filtering:** More accurate than post-title filtering; handles multi-GPU comparisons
3. **Regex + Known Models:** Balances automation with accuracy; catches new models while filtering noise
4. **Quality Filters:** Length + score + bot detection removes 90% of noise without manual word lists
5. **In-Memory Normalization:** Product name normalization using regex parsing instead of database queries - eliminates network overhead and latency
6. **Integrated Normalization:** Normalization integrated directly into ingestion pipeline for efficiency (no separate service needed)

### Architecture Decisions
7. **PostgreSQL over Kafka:** Batch ETL with PostgreSQL instead of streaming with Kafka - better fit for micro-batches every 4 hours, eliminates operational overhead
8. **Medallion Architecture:** Bronze (raw_comments) → Silver (product_sentiment) → Gold (product_rankings) - industry standard for data lakes
9. **Database Staging Layer:** Intermediate storage in database allows debugging, reprocessing, and audit trail - negligible performance impact (~1 second per batch)
10. **Batch Insert with Retry:** Database writes use retry decorator with exponential backoff for transient errors - handles connection issues gracefully
11. **Connection Pooling:** psycopg connection pool reuses database connections - reduces connection overhead

### Sentiment Analysis
12. **ABSA over Generic Sentiment:** Aspect-Based Sentiment Analysis provides product-specific sentiment instead of generic comment sentiment - critical for multi-product comparisons
13. **Batched Inference:** Process 64 product pairs per batch - optimal balance between throughput and memory usage
14. **Sentiment Processed Flag:** Track processing state in raw_comments table - allows reprocessing and prevents duplicate analysis

### Ranking Calculator
15. **Bayesian Scoring (IMDB Method):** Prevents astroturfing and manipulation by weighting products with more mentions higher - pulls low-sample products toward category average
16. **Time Windows:** "90d" and "all_time" windows show recent trends vs long-term reputation - injected via env vars by Airflow
17. **Vectorized Calculations:** Uses NumPy arrays for efficient batch computation of scores, grades, ranks, and badges
18. **Upsert Strategy:** ON CONFLICT UPDATE allows daily recalculation without duplicate entries

### Orchestration
19. **HTTP Operators + HttpSensor over KubernetesPodOperator:** Services run as persistent FastAPI pods with async endpoints
    - POST /run returns "started" immediately, processing happens in background thread
    - GET /status endpoint polled by HttpSensor until completion
    - No Airflow worker blocking - HttpSensor frees worker slots with mode="reschedule"
    - No pod startup latency (services always running)
    - ML models stay loaded in memory (sentiment/LLM models)
    - Easier debugging (persistent service logs vs ephemeral pod logs)
    - Better resource utilization (shared pods for multiple DAG runs)
20. **Per-Category DAGs:** Separate DAGs for GPU, LAPTOP, HEADPHONE with staggered schedules - allows independent scaling and failure isolation
21. **Background Thread Execution:** All services use ThreadPoolExecutor (max_workers=1) to prevent blocking FastAPI event loop
22. **Sequential with Waits:** DAGs use task → wait → task → wait pattern instead of blocking calls
    - Example: ingest → wait_ingest → sentiment → wait_sentiment
    - HttpSensor polls /status endpoint every 30 seconds until completion
23. **Thread-Safe State Management:** JobState class with threading.Lock for concurrent access safety
24. **Graceful Shutdown:** Signal handlers set cancellation flag, current job completes before exit

### LLM Summary
25. **OpenAI API Integration:** Using gpt-4o-mini for cost-effective TLDR generation
26. **Conversational Prompt Engineering:** System prompt enforces 8-16 word summaries with punchy tone
    - Examples provided for different categories (Audio, Computing, Outdoor, Fitness)
    - Encourages language like "legend", "monster", "endgame", "just buy it"
27. **Balanced Comment Selection:** Top 10 positive, 10 negative, 5 neutral comments ordered by Reddit score
    - Uses SQL window functions (ROW_NUMBER) partitioned by sentiment category
    - Ensures LLM sees both positive and negative opinions
28. **Monthly Regeneration:** Summaries regenerated monthly to reflect fresher comments
    - ON CONFLICT UPDATE upsert pattern allows idempotent re-runs
29. **Retry Logic for LLM API:** Exponential backoff for rate limits and transient errors

### Data Architecture
30. **Denormalized Silver Layer:** product_sentiment stores denormalized data for fast aggregation without joins
31. **Gold Layer Extensions:** product_rankings (computed daily) + product_summaries (regenerated monthly)
    - Both use ON CONFLICT UPDATE for idempotent re-runs
    - Separate tables allow independent update schedules (daily vs monthly)

---

## 📚 Key Files Modified/Created

### Data Ingestion Service (PostgreSQL Integration)
**Location:** `backend/data_pipeline/ingestion/src/`

**Created:**
- `utils/fetch_post.py` - Delayed post fetching
- `utils/fetch_comments.py` - Comment fetching with replace_more
- `preprocessing/gpu_detector.py` - GPU product detection
- `preprocessing/is_valid_comment.py` - Comment quality filtering
- `preprocessing/relevant_fields.py` - RedditComment Pydantic model
- `product_utils/gpu_normalization.py` - Product name normalization (regex-based)
- `product_utils/detector_factory.py` - Factory for category-specific detectors
- `product_utils/normalizer_factory.py` - Factory for category-specific normalizers
- `db_utils/conn.py` - PostgreSQL connection pool
- `db_utils/queries.py` - Batch insert queries with retry logic
- `db_utils/retry.py` - Retry decorator with exponential backoff

**Modified:**
- `worker.py` - Migrated from Kafka to PostgreSQL, batch insert to raw_comments table

### Sentiment Analysis Service (PostgreSQL Migration Complete ✓)
**Location:** `backend/data_pipeline/sentiment_analysis/src/`

**Status:** Successfully migrated from Kafka to PostgreSQL

**Core Files:**
- `worker.py` - Main worker with database polling, ABSA inference, graceful shutdown
- `preprocessing/sentiment_analysis.py` - ABSA model integration (DeBERTa v3 base)
- `preprocessing/extract_pairs.py` - Extract product-comment pairs from database rows

**Database Utilities:**
- `db_utils/conn.py` - PostgreSQL connection pool (psycopg_pool)
- `db_utils/queries.py` - fetch_unprocessed_comments, batch_insert_product_sentiment, mark_comments_processed
- `db_utils/retry.py` - Retry decorator with exponential backoff

**Configuration & Logging:**
- `core/settings_config.py` - Pydantic Settings for env var validation
- `core/logger.py` - JSON structured logging
- `core/types.py` - Pydantic models (UnprocessedComment, ProductSentiment)
- `core/model.py` - Model loading utility

**Tests (50+ test cases):**
- `tests/integration/` - Database integration tests with testcontainers
- `tests/unit/` - Unit tests for extraction, retry logic, shutdown handling

**Removed (Kafka-specific):**
- Kafka consumer/producer
- Queue-based batching for backpressure
- Offset management

### Ranking Calculator Service (Complete ✓)
**Location:** `backend/data_pipeline/ranking_calculator/src/`

**Core Files:**
- `ranking_service.py` - Main service with single-pass execution, graceful shutdown
- `calculation_utils/bayesian.py` - IMDB Top 250 Bayesian scoring formula
- `calculation_utils/grading.py` - Grade assignment (S to F-) and ranking
- `calculation_utils/badge.py` - Badge assignment (top_pick, most_discussed, limited_data)

**Database Utilities:**
- `db/conn.py` - PostgreSQL connection pool (psycopg_pool)
- `db/queries.py` - fetch_aggregated_product_scores, batch_upsert_product_score
- `db/retry.py` - Retry decorator with exponential backoff

**API Files:**
- `fastapi_entry_point.py` - FastAPI app entry point
- `api/routes.py` - /run, /status, /health, /ready endpoints
- `api/job_state.py` - Thread-safe JobState class
- `api/schemas.py` - Pydantic request/response models
- `api/signal_handler.py` - Graceful shutdown signal handling

**Configuration & Types:**
- `core/settings_config.py` - Pydantic Settings with grade thresholds, category validation
- `core/types.py` - Pydantic models (SentimentAggregate, ProductScore)
- `core/logger.py` - JSON structured logging
- `core/lifespan.py` - FastAPI lifespan management

**Tests:**
- `tests/unit/` - Unit tests for bayesian, grading, ranking, badges, endpoints, job state
- `tests/integration/` - Database integration tests with testcontainers

### LLM Summary Service (Complete ✓)
**Location:** `backend/data_pipeline/llm_summary/src/`

**Core Files:**
- `summary_service.py` - LLMSummaryService class with full pipeline
- `llm_client/prompts.py` - System prompt and user prompt builder
- `llm_client/response_parser.py` - TLDR extraction and validation
- `llm_client/retry.py` - LLM API retry logic

**Database Utilities:**
- `db/conn.py` - PostgreSQL connection pool (psycopg_pool)
- `db/queries.py` - fetch_unique_products, fetch_top_comments_for_product, upsert_llm_summaries
- `db/retry.py` - Retry decorator with exponential backoff

**API Files:**
- `fastapi_entry_point.py` - FastAPI app entry point
- `api/routes.py` - /run, /status, /health, /ready endpoints
- `api/job_state.py` - Thread-safe JobState class
- `api/schemas.py` - Pydantic request/response models
- `api/signal_handler.py` - Graceful shutdown signal handling

**Configuration & Types:**
- `core/settings_config.py` - Pydantic Settings (OPENAI_API_KEY, LLM_MODEL)
- `core/logger.py` - JSON structured logging
- `core/lifespan.py` - FastAPI lifespan management (DB pool, OpenAI client, ThreadPoolExecutor)

**Tests:**
- `tests/unit/` - Unit tests for prompts, parsing, job state, endpoints, signal handling
- `tests/integration/` - Database integration tests with testcontainers

### Orchestrator Service (Complete ✓)
**Location:** `backend/data_pipeline/orchestrator/`

**DAGs:**
- `src/dags/product_category_sentiment_analysis.py` - Per-category DAGs with ingest → wait → sentiment → wait
- `src/dags/product_category_ranking.py` - Per-category ranking DAGs with all_time → wait → 90d → wait
- `src/dags/product_summary.py` - Monthly summary DAG with all_time → wait → 90d → wait

**Configuration:**
- `src/config/settings.py` - Pydantic Settings (retries, timeouts, scheduling, STATUS_POLL_INTERVAL)
- `src/config/category_mappings.py` - Category-to-subreddit mappings, schedules

**Connections:**
- `src/connections/ingestion_service.py` - HTTP connection to ingestion FastAPI pod
- `src/connections/sentiment_analysis_service.py` - HTTP connection to sentiment FastAPI pod
- `src/connections/llm_summary_service.py` - HTTP connection to LLM summary FastAPI pod
- `src/connections/product_ranking_service.py` - HTTP connection to ranking FastAPI pod

**Utilities:**
- `src/utils/on_task_failure.py` - Failure callback for alerting

**Tests:**
- `tests/unit/` - 16 unit tests for DAG structure, task configs, dependencies
- `tests/integration/` - 13 integration tests with K3s cluster (testcontainers)
- `tests/utils/` - Test utilities (airflow helpers, mock service, pod lifecycle)

### Insights API (Complete ✓ - Updated with Valkey Caching)
**Location:** `backend/insights_api/src/`

**Core Files:**
- `main.py` - FastAPI app entry point with router registration
- `core/settings.py` - Pydantic Settings for environment configuration (DB + Valkey)
- `core/lifespan.py` - App lifecycle management (DB health check, cleanup)
- `core/logger.py` - Structured JSON logging

**Routes:**
- `routes/home.py` - Home endpoints (`/home/trending/product_topics`)
- `routes/topic.py` - Topic endpoints (`/topic/products`, `/topic/total_products_ranked`, `/topic/total_comments`)
- `routes/category.py` - Category endpoints (`/category/top_mentioned_products`, `/category/total_products_count`, `/category/topic_most_mentioned_product`)
- `routes/products.py` - Product endpoints (`/product/sentiment_scores`, `/product/top_comments`, `/product/search`)

**Database Utilities:**
- `db_utils/pg_conn.py` - AsyncIO SQLAlchemy engine and session factory
- `db_utils/product_queries.py` - Product query functions (sentiment scores, top comments, search)
- `db_utils/category_queries.py` - Category query functions (top products, product count)
- `db_utils/topic_queries.py` - Topic query functions (products, comment count, ranked count)
- `db_utils/retry.py` - Retry decorator with exponential backoff

**Valkey Caching Layer:**
- `db_utils/cache_conn.py` - Valkey async connection pool
- `db_utils/cache_commands.py` - Cache utilities (get/set, trending topics, view tracking)

**Middleware:**
- `middleware/metrics.py` - Prometheus instrumentation (DB + cache metrics)
- `middleware/get_client_ip.py` - Client IP extraction for view tracking
- `middleware/topic_category_mapping.py` - Topic-to-category mapping

**Schemas:**
- `schemas/product.py` - RankedProduct, TopMentionedProduct, CategoryTopMentionedProduct
- `schemas/comment.py` - TopComment model
- `schemas/response.py` - API response wrappers
- `schemas/queries.py` - Database query result models
- `schemas/home.py` - TrendingTopic, TrendingTopicsResponse

**Tests (60+ test cases across 31 files):**
- `tests/integration/` (9 files) - Endpoint tests with testcontainers PostgreSQL, caching tests
- `tests/unit/` (13 files) - Lifespan, endpoint, and component unit tests

---

## 🐛 Known Issues & Limitations

1. **Rate Limits:** No explicit rate limiting handling (PRAW handles internally, but may hit limits with many subreddits)
2. **Multiple Subreddits:** Currently configured for 6 subreddits (nvidia, amd, buildapc, gamingpc, pcbuild, hardware)
3. **No Backfill:** Only fetches 24-48h old posts; need arctic_shift/Pushshift for historical data (will use Spark for backfill)
4. **Manual GPU List Maintenance:** Need to update known models when new GPUs release (low frequency)
5. **Frontend Backend Integration:** Frontend UI complete with mock data, needs to be connected to Insights API

---

## 🔧 Environment Setup

**Dependencies:**
- Python 3.13
- PRAW (Reddit API)
- PostgreSQL + TimescaleDB (for data storage)
- psycopg (PostgreSQL adapter)

**Configuration:**
- Reddit API credentials in `.env`
- PostgreSQL connection: via connection pool in `db_utils/conn.py`
- Subreddits: Configured via category mapping in `category_to_subreddit_mapping()`

---

## 📖 Documentation

- **PRD:** `/PRD.md` - Full product requirements document
- **README:** `/README.md` - Original project structure
- **This File:** `/PROGRESS.md` - Current progress & next steps

---

## 🎓 Learning Outcomes So Far

### Data Collection & ETL
1. ✅ Reddit API pagination & delayed fetching strategies
2. ✅ PRAW comment tree traversal with `replace_more()`
3. ✅ Regex pattern design for product detection and normalization
4. ✅ Quality filtering without manual word lists
5. ✅ Pydantic for type-safe data validation
6. ✅ In-memory normalization vs database queries for performance

### Database & Architecture
7. ✅ PostgreSQL connection pooling with psycopg
8. ✅ Batch insert strategies for optimal write performance
9. ✅ Retry patterns with exponential backoff for transient errors
10. ✅ Medallion Architecture (Bronze → Silver → Gold layers)
11. ✅ Batch ETL vs streaming architecture trade-offs
12. ✅ Database staging layers for debugging and reprocessing
13. ✅ Idempotent operations with conflict handling (ON CONFLICT DO NOTHING)

### Sentiment Analysis (Complete)
14. ✅ ABSA (Aspect-Based Sentiment Analysis) for product-specific sentiment
15. ✅ Batching strategies for efficient ML inference
16. ✅ PostgreSQL-based polling architecture (replaced Kafka streaming)
17. ✅ Graceful shutdown handling with signal handlers
18. ✅ Integration testing with testcontainers PostgreSQL
19. ✅ Transaction management for atomic insert + update operations

### Ranking Calculator (Complete)
20. ✅ Bayesian scoring using IMDB Top 250 formula for manipulation resistance
21. ✅ NumPy vectorized operations for efficient batch calculations
22. ✅ SciPy rankdata for tie-handling in ranking assignment
23. ✅ Grade threshold system with configurable boundaries
24. ✅ Badge assignment logic (top_pick, most_discussed, limited_data)
25. ✅ SQL aggregation with FILTER clauses for sentiment breakdown
26. ✅ Upsert patterns with ON CONFLICT UPDATE for idempotent daily runs

### Orchestration (Complete)
27. ✅ Apache Airflow DAG design with dynamic DAG generation per category
28. ✅ HTTP Operators for calling persistent FastAPI services (vs KubernetesPodOperator)
29. ✅ Kubernetes service discovery via DNS (`service-name.namespace.svc.cluster.local`)
30. ✅ Airflow connection management and response validation
31. ✅ Integration testing with K3s clusters via testcontainers
32. ✅ Mock HTTP services for end-to-end DAG testing
33. ✅ Exponential backoff retry strategies with configurable delays

### Insights API (Complete - Enhanced with Valkey Caching)
34. ✅ FastAPI async routes with dependency injection patterns
35. ✅ AsyncIO SQLAlchemy with asyncpg for non-blocking database access
36. ✅ Connection pooling configuration (pool_size, max_overflow, pool_pre_ping)
37. ✅ Lifespan context managers for app startup/shutdown handling
38. ✅ SQL injection prevention with parameterized queries
39. ✅ ILIKE queries with SQL wildcard escaping for safe search
40. ✅ Pydantic response models for type-safe API responses
41. ✅ Integration testing with testcontainers PostgreSQL and FastAPI TestClient
72. ✅ Valkey (Redis-compatible) caching with async connection pool
73. ✅ Cache-aside pattern with TTL-based expiry for different data types
74. ✅ Graceful cache degradation: Fall back to DB if cache unavailable
75. ✅ Valkey sorted sets (ZREVRANGE, ZINCRBY) for real-time trending calculation
76. ✅ Time-based cache key generation for weekly auto-reset (`trending:topics:2026-W04`)
77. ✅ IP-based deduplication using SET with NX flag to prevent refresh spam
78. ✅ Prometheus metrics with histograms for DB queries and cache operations
79. ✅ FastAPI middleware for client IP extraction and metrics collection
80. ✅ Domain-driven query organization (product_queries, category_queries, topic_queries)
81. ✅ Pagination implementation with current_page and total_pages metadata

### Frontend (Complete)
42. ✅ React 19 with TypeScript strict mode for type-safe UI development
43. ✅ React Router v7 for client-side routing with lazy loading
44. ✅ TailwindCSS custom configuration with dark theme and animations
45. ✅ Component composition patterns (ProductRow uses ProductBadges, RankingDetailsBadge, etc.)
46. ✅ useMemo for performance optimization (filtering, sorting)
47. ✅ Custom animations with TailwindCSS (@keyframes fade-in-up, fade-in-left)
48. ✅ TypeScript discriminated unions for type-safe filter and grade types
49. ✅ React hooks patterns (useState, useMemo, useEffect for document title updates)
50. ✅ Expandable UI components with smooth transitions
51. ✅ Interactive data visualization (sentiment breakdown bar chart with hover tooltips)
52. ✅ Responsive design patterns (max-w-4xl containers, fixed sidebar/header)
53. ✅ Client-side filtering with composable filter functions
54. ✅ URL-based routing with deep linking support
55. ✅ Mock data structures matching backend API response format

### LLM Summary Service (Complete)
56. ✅ OpenAI API integration with custom system prompts for conversational tone
57. ✅ Prompt engineering: 8-16 word TLDRs with punchy language ("legend", "monster", "endgame")
58. ✅ Response parsing and validation (TLDR extraction from LLM output)
59. ✅ Balanced comment retrieval: 10 positive, 10 negative, 5 neutral ordered by Reddit score
60. ✅ SQL window functions (ROW_NUMBER) with sentiment category partitioning
61. ✅ Retry logic for LLM API calls with exponential backoff
62. ✅ Upsert patterns for monthly summary regeneration (ON CONFLICT UPDATE)
63. ✅ Background thread execution with ThreadPoolExecutor to prevent blocking FastAPI
64. ✅ Thread-safe JobState class for tracking LLM job progress

### Async Service Pattern (All Services)
65. ✅ FastAPI background task execution with ThreadPoolExecutor
66. ✅ POST /run endpoint returns "started" immediately, processes in background thread
67. ✅ GET /status endpoint for Airflow HttpSensor polling (returns job status)
68. ✅ Thread-safe state management with JobState class (RUNNING, COMPLETED, FAILED, CANCELLED)
69. ✅ Graceful shutdown with signal handlers (SIGTERM/SIGINT sets cancellation flag)
70. ✅ Airflow HttpSensor pattern: poke_interval, mode="reschedule" to free worker slots
71. ✅ Prevents Airflow timeout issues - services can run for hours without blocking workers

### Previously Learned (Kafka - Now Deprecated)
- Kafka backpressure management with bounded queues
- Partition-safe offset management for Kafka consumers
- Producer flush patterns and message delivery guarantees

---

## ✅ Completed: Frontend (React + TypeScript + TailwindCSS)

### What Was Built

The frontend is a fully styled, responsive product ranking platform built with modern React patterns and TailwindCSS. All UI components are complete with mock data integration. **Ready for backend API integration.**

**1. Tech Stack**
- React 19 with TypeScript (strict mode)
- React Router v7 for client-side routing
- Vite as build tool
- TailwindCSS + Custom animations (fade-in-up, fade-in-left)
- Redux Toolkit (will be replaced with React Query + Zustand)
- Lucide React for icons
- Motion for animations

**2. Pages & Routing (3 Routes)**

**HomePage (`/`):**
- Landing page with trending topics grid
- Browse categories section with category cards
- Navigation to category pages

**CategoryPage (`/:category`):**
- Shows all topics within a category (e.g., /computing)
- Top mentioned products grid (top 6 products)
- All product topics list with metadata (product count, view count)
- Breadcrumb navigation

**TopicPage (`/:category/:topic`):**
- Main product ranking page (e.g., /computing/gpus)
- Product list with ranks, grades, badges, and sentiment scores
- Filter tabs: Best Overall, Most Discussed, Highest Approval, Hidden Gems
- Price point filter: $, $$, $$$ (budget, mid-range, premium)
- Time window toggle: 90d vs All Time
- Search bar for filtering products by name
- Expandable product rows showing:
  - Sentiment breakdown (positive/neutral/negative bar chart with hover tooltips)
  - Top 3 Reddit comments with upvotes and external links
- Source subreddit badges with links to Reddit
- Breadcrumb navigation

**3. Component Structure (25 Components)**

**Layout Components:**
- `MainLayout` - Wrapper with header, sidebar, and content area
- `Header` - Fixed top header with logo and global product search
- `Sidebar` - Fixed left sidebar with category tree navigation
- `SideBarSectionLayout` - Reusable section wrapper for sidebar

**Product Components:**
- `ProductList` - Renders list of products with loading/empty states
- `ProductRow` - Individual product card with expandable details
- `ProductBadges` - Badge display (Top Pick, Most Discussed, Hidden Gem, Limited Data)
- `RankingDetailsBadge` - Rank, grade, approval %, and mention count display
- `SentimentBreakDown` - Interactive bar chart with hover tooltips showing sentiment counts
- `TopComments` - Top 3 Reddit comments with scores and external links
- `FilterTabs` - Filter buttons (Best, Discussed, Approval, Hidden Gems)
- `TimeRangeSwitch` - Toggle between 90d and All Time
- `PriceFilterSwitch` - Dropdown for $, $$, $$$ filtering
- `TopicProductSearchBar` - Search input for filtering products by name

**Category Components:**
- `TopicCardList` - Clickable topic cards with metadata
- `TopProductsGrid` - Grid showing top 6 products for a category
- `ExtraRedditSourceList` - Popover showing additional subreddit sources

**Home Components:**
- `TrendingTopicsList` - Grid of trending topics with stats
- `BrowseCategoriesGrid` - Category cards with icons and metadata
- `CategoryDropDownGrid` - Dropdown menu for category navigation

**Sidebar Components:**
- `SidebarCategoryTree` - Expandable/collapsible category tree
- `SidebarCategoryItem` - Individual category item with expand/collapse
- `SidebarTopicItem` - Individual topic link with active state
- `TopicBreadcrumb` - Breadcrumb navigation (Home > Category > Topic)

**Header Components:**
- `AllProductsSearchList` - Dropdown showing search results from all products

**4. Features Implemented**

**Product Display:**
- Rank display with trophy icons for top 3 (gold, silver, bronze)
- Grade badges: S, A+, A, A-, B+, B, B-, C+, C, C-, D+, D, D-, F
- Approval percentage display
- Mention count display
- Product badges: Top Pick (crown), Most Discussed (flame), Hidden Gem (diamond), Limited Data (warning)
- TL;DR summaries (placeholder for LLM summaries)

**Filtering & Search:**
- Badge-based filtering: Best Overall, Most Discussed, Highest Approval, Hidden Gems
- Price point filtering: $, $$, $$$ (client-side mock implementation)
- Time window filtering: 90d vs All Time
- Search by product name (global header search + per-topic search)
- Filters are composable (badge + price + time window + search work together)

**Sentiment Visualization:**
- Interactive sentiment breakdown bar chart
- Color-coded sections: green (positive), gray (neutral), red (negative)
- Hover tooltips showing exact counts
- Percentage breakdown display
- Total mentions count

**Reddit Integration (UI Only):**
- Top 3 Reddit comments display with upvote scores
- External links to Reddit comments
- Source subreddit badges with links to Reddit
- "View more details" dropdown for each product

**Animations & Interactions:**
- Fade-in-up animation for product rows
- Fade-in-left animation for sentiment breakdown and comments
- Expandable product rows with smooth transitions
- Hover states for buttons, links, and badges
- Loading states for filter changes

**Navigation:**
- Client-side routing with React Router
- Breadcrumb navigation on all pages
- Active state highlighting in sidebar
- Deep linking support (shareable URLs)

**5. Data Types & Models**

**TypeScript Interfaces (src/mock/types.ts):**
```typescript
- Category: id, name, slug, icon, viewCount, rankedAmount, topics[]
- Topic: id, name, slug, icon, parentSlug, productCount, sourceSubreddits[], viewCount
- ProductV3: id, product_name, price_point, time_window, rank, grade, mention_count,
  approval_percentage, badges (is_top_pick, is_most_discussed, is_hidden_gem, has_limited_data),
  tldr_summary, parentSlug, subcategory_slug
- Sentiment: positive_count, neutral_count, negative_count
- Comment: id, comment_text, reddit_link, score
- TrendingCategory: id, product_name, category, subcategory, grade, trendReason
- Subreddit: name
```

**Grade Type:** "S" | "A+" | "A" | "A-" | "B+" | "B" | "B-" | "C+" | "C" | "C-" | "D+" | "D" | "D-" | "F"

**TimeWindow Type:** "90d" | "all"

**FilterType:** "best" | "discussed" | "approval" | "hidden_gems"

**6. Utilities (6 Files)**

**Product Utilities:**
- `productFilters.ts` - Filter functions (FilterByBadge, FilterByPricePoint, FilterBySearchTerm, FilterByTimeWindow)
- `GetColors.ts` - Color mapping for ranks (gold, silver, bronze)
- `GetProductsByTopic.ts` - Fetch products by topic slug (mock implementation)

**Category Utilities:**
- `getTopProductsByCategory.ts` - Fetch top 6 products for a category

**Topic Utilities:**
- `GetTopicBySlug.ts` - Fetch topic data by category and topic slug

**Home Utilities:**
- `IconMap.ts` - Icon name to Lucide icon component mapping

**7. Styling & Design System**

**TailwindCSS Configuration:**
- Dark theme: `#0a0a0a` background, zinc color palette
- Custom animations: fade-in-up, fade-in-left
- Custom shadows: cards, dropdowns, inner borders
- Custom colors: gold (#ffd700), orange (#FF9900 for Reddit), zinc grays
- Responsive breakpoints (max-w-4xl content containers)

**Design Patterns:**
- Dark theme throughout (no light mode)
- Consistent spacing (px-6, py-8 for page padding)
- Border colors: zinc-600/50, zinc-800/40
- Hover states: hover:bg-zinc-900/20, hover:text-zinc-300
- Focus states: focus:outline-none, focus:border-zinc-600
- Transitions: transition-colors duration-250

**8. Mock Data Implementation**

**Mock Data Files:**
- `mockData.ts` - Categories, topics, products, comments, sentiment data
- Realistic data structure matching backend API response format
- 6 mock topics: Laptops, GPUs, CPUs, Monitors, Mechanical Keyboards, Soundbars
- 3 mock categories: Computing, Audio, Gaming
- 50+ mock products with realistic grades, ranks, and sentiment scores
- Mock comments with Reddit-style formatting

**Mock Data Functions:**
- `getCategoryBySlug()` - Find category by URL slug
- `getTopicBySlug()` - Find topic within category
- `getProductsByTopic()` - Filter products by topic
- `getPopularCategories()` - Get top 3 categories by view count

**9. State Management (To Be Replaced)**

**Current Implementation (Redux Toolkit):**
- `app/store.ts` - Redux store configuration
- `app/base/insightsSlice.ts` - Insights state slice
- `app/api-slices/insights.ts` - API slice for backend calls (RTK Query)
- `app/state/ui.ts` - UI state management

**Will Be Replaced With:**
- React Query for API data fetching/caching
- Zustand for lightweight global state (UI state, filters, search)

### Key Implementation Details

**Routing Structure:**
- `/` - Homepage
- `/:category` - Category page (e.g., /computing)
- `/:category/:topic` - Topic/product page (e.g., /computing/gpus)

**Component Reusability:**
- All components are pure and accept props (no hardcoded data)
- Components are composable (ProductRow uses ProductBadges, RankingDetailsBadge, etc.)
- Utility functions are shared across components

**Performance Optimizations:**
- Lazy loading for page components (React.lazy)
- useMemo for expensive computations (filtering, sorting)
- Minimal re-renders with proper dependency arrays

**Accessibility:**
- Semantic HTML (nav, section, header, main, aside)
- Keyboard navigation support
- Focus states on interactive elements
- ARIA labels (to be added during API integration)

---

## 🎯 Frontend Status Summary

### ✅ Completed
1. **All Pages:** HomePage, CategoryPage, TopicPage with full routing
2. **All Components:** 25 components with proper TypeScript types
3. **All Features:** Filtering, search, time windows, expandable rows, sentiment visualization
4. **Styling:** Complete dark theme with TailwindCSS, custom animations, responsive design
5. **Mock Data:** Comprehensive mock data matching backend API structure
6. **Navigation:** Client-side routing, breadcrumbs, sidebar navigation, active states

### ⏳ Needs Backend Integration
1. **Replace Mock Data with API Calls:**
   - Category list: `GET /api/v1/category`
   - Ranked products: `GET /api/v1/category/products?category=GPU&time_window=all_time`
   - Product sentiment: `GET /api/v1/product/view_more?product_name=X&time_window=Y`
   - Top comments: `GET /api/v1/product/top_comments?product_name=X&time_window=Y`
   - Product search: `GET /api/v1/product/search?q={query}`

2. **Replace Redux with React Query + Zustand:**
   - Remove `@reduxjs/toolkit`, `react-redux` dependencies
   - Install `@tanstack/react-query`, `zustand`
   - Create query hooks for each API endpoint
   - Create Zustand store for UI state (filters, search term, selected price, time window)
   - Replace `useSelector` with `useQuery` and Zustand hooks

3. **Add API Integration Layer:**
   - Create `src/api/client.ts` - Axios/Fetch client with base URL
   - Create `src/api/endpoints.ts` - API endpoint constants
   - Create `src/hooks/useRankedProducts.ts` - React Query hook
   - Create `src/hooks/useSentiment.ts` - React Query hook
   - Create `src/hooks/useTopComments.ts` - React Query hook
   - Create `src/hooks/useProductSearch.ts` - React Query hook
   - Create `src/hooks/useCategories.ts` - React Query hook

4. **Add Loading & Error States:**
   - Loading spinners for API calls
   - Error boundaries for page-level errors
   - Retry logic for failed API calls
   - Empty states for no results
   - Skeleton loaders for products

5. **Environment Variables:**
   - Create `.env` file with `VITE_API_BASE_URL`
   - Update Vite config to use env vars
   - Add environment-specific API URLs (dev, staging, prod)

6. **Additional Features (Nice to Have):**
   - Debounce search input to reduce API calls
   - URL query params for filters (shareable filtered URLs)
   - Pagination or infinite scroll for large product lists
   - Product detail modal with full sentiment data
   - "View Prices" button integration (Amazon Affiliate API)

---

## 📋 Frontend File Structure

```
frontend/
├── src/
│   ├── app/                    # Redux (to be removed)
│   │   ├── api-slices/
│   │   │   └── insights.ts
│   │   ├── base/
│   │   │   └── insightsSlice.ts
│   │   ├── state/
│   │   │   └── ui.ts
│   │   └── store.ts
│   ├── components/             # 25 components
│   │   ├── category/           # 3 components
│   │   ├── header/             # 1 component
│   │   ├── home/               # 3 components
│   │   ├── layout/             # 3 components
│   │   ├── product/            # 10 components
│   │   └── sidebar/            # 5 components
│   ├── mock/                   # Mock data (to be removed after API integration)
│   │   ├── constants.ts
│   │   ├── mockData.ts
│   │   └── types.ts
│   ├── pages/                  # 3 pages
│   │   ├── CategoryPage.tsx
│   │   ├── HomePage.tsx
│   │   └── TopicPage.tsx
│   ├── utils/                  # 6 utility files
│   │   ├── category/
│   │   ├── home/
│   │   ├── product/
│   │   └── topic/
│   ├── App.tsx                 # Route definitions
│   ├── main.tsx                # App entry point
│   └── index.css               # Global styles
├── package.json                # Dependencies
├── tailwind.config.js          # TailwindCSS config
├── vite.config.ts              # Vite config
└── tsconfig.json               # TypeScript config
```

---

## Next Session: Start Here 👇

**Current Status:**
- ✅ Data Ingestion Service: Writes to raw_comments table (Bronze layer) with async /run + /status endpoints
- ✅ Sentiment Analysis Service: Reads/writes from database (Silver layer) with async /run + /status endpoints
- ✅ Ranking Calculator Service: Computes rankings and writes to product_rankings table (Gold layer) with async /run + /status endpoints
- ✅ LLM Summary Service: Generates conversational TLDRs using OpenAI API, writes to product_summaries table with async /run + /status endpoints
- ✅ Orchestrator Service: Airflow DAGs with HttpOperator + HttpSensor pattern (all services use background threads + status polling)
- ✅ Insights API: **Enhanced with Valkey caching layer**
  - 13 endpoints across home, topic, category, and product routes
  - Weekly trending topics with IP-based view deduplication
  - Cache-aside pattern with TTL expiry (10-30 minute TTLs)
  - Prometheus metrics for DB queries and cache operations
  - 60+ tests across 31 test files (integration + unit)
- ✅ Frontend UI: All pages, components, styling complete with mock data
- ⏳ Frontend Backend Integration: Need to connect frontend to Insights API

**Immediate Next Task:**
**Frontend Backend Integration**
1. Replace Redux with React Query + Zustand
2. Create API client and query hooks for all Insights API endpoints
3. Connect all pages to backend:
   - HomePage: Categories, trending topics
   - CategoryPage: Topics, top products
   - TopicPage: Ranked products, sentiment breakdown, top comments, search
4. Add loading states, error handling, and retry logic
5. Add TLDR summaries from LLM Summary service to product cards
6. Test end-to-end flow with real data
7. Deploy frontend + insights API + all services to Kubernetes

---

## Session Summaries

**Session: 2026-01-26 - Insights API Enhanced with Valkey Caching + New Routes**
- ✅ **Completed:** Comprehensive Insights API enhancement with Valkey caching layer
  - Added **Valkey (Redis-compatible) caching** with async connection pool
  - Implemented cache-aside pattern with TTL-based expiry (10-30 minute TTLs)
  - Added **weekly trending topics** feature using Valkey sorted sets (ZREVRANGE)
  - IP-based view deduplication to prevent refresh spam (SET with NX flag)
  - Weekly auto-reset for trending via time-based cache keys (`trending:topics:2026-W04`)
- ✅ **New Routes Added:**
  - **Home endpoints**: `/home/trending/product_topics` - Real-time trending topics
  - **Topic endpoints**: `/topic/products`, `/topic/total_products_ranked`, `/topic/total_comments`
  - **Category endpoints**: `/category/top_mentioned_products`, `/category/total_products_count`, `/category/topic_most_mentioned_product`
  - **Product endpoints**: Updated with caching for `/product/top_comments` and `/product/search`
- ✅ **Prometheus Metrics:**
  - Added `db_query_duration_seconds` histogram (labels: query_type, query_name, table)
  - Added `cache_operation_duration_seconds` histogram (labels: operation, hit)
  - FastAPI request instrumentation with prometheus-fastapi-instrumentator
- ✅ **Middleware:**
  - Client IP extraction middleware for view tracking
  - Topic-to-category mapping helper
  - Metrics middleware for observability
- ✅ **Database Query Refactor:**
  - Split queries into domain-specific modules: `product_queries.py`, `category_queries.py`, `topic_queries.py`
  - Added pagination support for product search
  - Optimized queries for top mentioned products across topics
- ✅ **Test Coverage Expansion:**
  - 60+ tests across 31 test files (previously 30+ tests)
  - 9 integration test files with testcontainers PostgreSQL
  - 13 unit test files
  - New tests for caching behavior, trending topics, pagination
- 📋 **Key Implementation Details:**
  - Cache graceful degradation: Falls back to DB if cache unavailable
  - Weekly trending reset via ISO week-based cache keys
  - Set cache with optional callback for side effects (e.g., increment trending count)
  - Prometheus metrics exposed on `/metrics` endpoint
- 📝 **Updated PROGRESS.md** with:
  - Expanded "Insights API" section documenting all new routes and caching layer
  - Detailed Valkey caching architecture and strategy
  - Updated file structure to reflect new modules (cache, middleware, query split)
  - Updated test coverage numbers (60+ tests across 31 files)
- **Next Step:** Frontend Backend Integration (connect React app to Insights API)

**Session: 2026-01-24 - LLM Summary Service Complete + Services Updated with Async Pattern**
- ✅ **Completed:** Comprehensive LLM Summary Service implementation
  - OpenAI API integration with custom conversational prompts (8-16 words, punchy tone)
  - Fetches unique products with min 10 comments from product_sentiment table
  - Retrieves balanced top comments (10 positive, 10 negative, 5 neutral) ordered by Reddit score
  - Generates TLDRs using system prompt with examples for different categories
  - Upserts to product_summaries table with ON CONFLICT UPDATE for monthly regeneration
  - Background thread execution with ThreadPoolExecutor to prevent blocking
  - POST /run endpoint returns "started" immediately, processes in background
  - GET /status endpoint for Airflow HttpSensor polling until completion
  - Thread-safe JobState class for tracking progress (RUNNING, COMPLETED, FAILED, CANCELLED)
  - Comprehensive test coverage (unit + integration with testcontainers)
- ✅ **Updated:** All services (ingestion, sentiment_analysis, ranking_calculator) with async pattern
  - Refactored to use background thread execution (ThreadPoolExecutor max_workers=1)
  - POST /run returns {status: "started"} immediately, processing happens in background
  - GET /status endpoint allows Airflow HttpSensor to poll for completion
  - JobState class for thread-safe job tracking
  - Signal handlers for graceful shutdown (sets cancellation flag on SIGTERM/SIGINT)
- ✅ **Updated:** Orchestrator DAGs with HttpOperator + HttpSensor pattern
  - product_category_sentiment_analysis.py: ingest → wait → sentiment → wait (sequential with waits)
  - product_category_ranking.py: all_time → wait → 90d → wait (sequential with waits)
  - product_summary.py (NEW): all_time → wait → 90d → wait (monthly schedule)
  - HttpSensor polls /status endpoint with poke_interval=30s, mode="reschedule" to free worker slots
  - Prevents timeout issues - services can run for hours without blocking Airflow workers
- 📋 **Key Architecture Decision:** Background thread + status polling pattern
  - Services process in background thread, return "started" immediately to Airflow
  - Airflow uses HttpSensor to poll /status endpoint until completion
  - Prevents blocking, frees worker slots, no timeout issues
  - Same pattern across all 4 services for consistency
- 📝 **Updated PROGRESS.md** with:
  - New "LLM Summary Service" section with full implementation details
  - Updated "Orchestrator Service" section with HttpSensor pattern and new DAG structure
  - Updated service file listings to include API routes, job state, signal handlers
  - Updated "Next Session" to reflect LLM Summary completion
  - Updated status line to include LLM Summary ✓
- **Next Step:** Frontend Backend Integration (connect React app to Insights API)

**Session: 2026-01-21 - Frontend Audit Complete**
- ✅ **Completed:** Comprehensive frontend audit and documentation
  - Reviewed all 25 components across layout, product, category, home, sidebar, and header sections
  - Documented 3 pages (HomePage, CategoryPage, TopicPage) with full routing structure
  - Analyzed TypeScript types, mock data structure, and utility functions
  - Identified all implemented features: filtering, search, time windows, sentiment visualization, badges
  - Documented styling system: TailwindCSS with dark theme, custom animations, responsive design
- 📋 **Key Findings:**
  - Frontend is 100% complete with mock data integration
  - All UI components are styled and functional
  - React 19 + TypeScript + Vite + TailwindCSS stack
  - Redux Toolkit currently used (will be replaced with React Query + Zustand)
  - 6 utility files for filtering, color mapping, and data fetching
  - Mock data matches backend API response format
- 📋 **Next Steps:**
  - Replace Redux with React Query + Zustand for cleaner state management
  - Create API client and query hooks for Insights API
  - Connect all pages to backend endpoints
  - Add loading states and error handling
  - Remove mock data after successful integration
- 📝 **Updated PROGRESS.md** with comprehensive frontend documentation (section: "✅ Completed: Frontend")
- **Next Step:** Frontend Backend Integration OR LLM Summary Service

**Session: 2026-01-19 - Insights API Complete**
- ✅ **Completed:** Built FastAPI Insights API with 5 endpoints
  - `GET /api/v1/category` - Returns all product categories
  - `GET /api/v1/category/products` - Returns ranked products with grades, scores, badges
  - `GET /api/v1/product/view_more` - Returns sentiment breakdown (positive/neutral/negative counts)
  - `GET /api/v1/product/top_comments` - Returns top 5 Reddit comments with links
  - `GET /api/v1/product/search` - Intelligent search with prefix ordering, SQL injection safe
- 📋 **Key Features:**
  - AsyncIO SQLAlchemy with asyncpg for non-blocking database access
  - Connection pooling: pool_size=10, max_overflow=20, health checks enabled
  - Lifespan management: DB health check on startup, graceful cleanup on shutdown
  - Exponential backoff retry decorator for transient database errors
  - SQL injection prevention and wildcard escaping in search
- 📋 **Test Coverage:** 30+ tests
  - Integration tests with testcontainers PostgreSQL
  - Endpoint validation, time window filtering, case-insensitive matching
  - SQL injection and wildcard escaping tests
  - Unit tests for lifespan management
- 📝 **Updated PROGRESS.md** to reflect completion of Insights API
- **Next Step:** Build Frontend (React/Next.js) or LLM Summary Service

**Session: 2026-01-18 - Orchestrator Service Complete**
- ✅ **Completed:** Built Airflow orchestrator with HTTP operators calling persistent FastAPI pods
  - Per-category pipeline DAGs: `product_gpu_pipeline`, `product_laptop_pipeline`, `product_headphone_pipeline`
  - Per-category ranking DAGs: `product_gpu_ranking`, `product_laptop_ranking`, `product_headphone_ranking`
  - Task structure: Ingest >> [Sentiment, LLM_Summary] for pipelines, [90d, all_time] parallel for ranking
  - Staggered schedules: GPU (00:00), LAPTOP (01:00), HEADPHONE (02:00); ranking 30 min after
- 📋 **Key Architecture Decision:** HTTP Operators over KubernetesPodOperator
  - Services run as persistent FastAPI pods with `/run` endpoints
  - Benefits: No pod startup latency, models stay in memory, easier debugging, better resource utilization
- 📋 **Test Coverage:**
  - 16 unit tests (DAG structure, task configs, dependencies)
  - 13 integration tests with K3s cluster via testcontainers (full end-to-end with mock services)
- 📋 **Configuration:** Pydantic Settings for retries (2), exponential backoff (5-30 min), execution timeout (1 hour)
- 📝 **Updated PROGRESS.md** to reflect completion of orchestrator service
- **Next Step:** Build LLM Summary Service or Insights API

**Session: 2026-01-15 - Ranking Calculator Service Complete**
- ✅ **Completed:** Built ranking calculator service for Gold layer
  - Created worker with single-pass execution and graceful shutdown
  - Implemented Bayesian scoring (IMDB Top 250 formula) for manipulation resistance
  - Grade assignment: S, A, A-, B, B-, C, C-, D, D-, F, F- based on configurable thresholds
  - Badge assignment: is_top_pick, is_most_discussed, has_limited_data
  - Database utilities: connection pool, aggregation queries, upsert with conflict handling
- 📋 **Key Features:**
  - Time windows: "90d" and "all_time" via `TIME_WINDOWS` env var
  - Category processing via `PRODUCT_CATEGORY` env var (GPU, LAPTOP, HEADPHONE)
  - NumPy/SciPy for vectorized calculations (efficient batch processing)
  - Comprehensive test coverage: unit tests + integration tests with testcontainers
- 📋 **Airflow Integration Design:**
  - Worker processes ONE category + ONE time window per run
  - Airflow calls worker multiple times with different env var combinations
- 📝 **Updated PROGRESS.md** to reflect completion of ranking calculator
- **Next Step:** Set up Airflow DAGs for orchestration

**Session: 2026-01-14 - Sentiment Analysis Migration Complete**
- ✅ **Completed:** Migrated sentiment analysis service from Kafka to PostgreSQL
  - Created database utilities: connection pool (psycopg_pool), queries, retry decorator
  - Updated worker.py with database polling loop, graceful shutdown handling
  - Implemented atomic transactions: insert sentiments + mark comments processed
  - Comprehensive test coverage: 50+ tests (unit + integration with testcontainers)
- 📋 **Key Features:**
  - Category-based processing via `PRODUCT_CATEGORY` environment variable
  - Batch fetch (200 comments) + batch inference (64 pairs) for optimal throughput
  - Graceful shutdown: SIGTERM/SIGINT handlers, completes current batch before exit
  - Idempotent operations: ON CONFLICT DO NOTHING prevents duplicate processing
- 📝 **Updated PROGRESS.md** to reflect completion of sentiment analysis migration
- **Next Step:** Build Ranking Calculator Service

**Session: 2026-01-12 - Data Ingestion PostgreSQL Migration**
- ✅ **Completed:** Migrated data ingestion service from Kafka to PostgreSQL
  - Created database utilities: connection pooling, batch insert, retry logic
  - Updated worker.py to write directly to `raw_comments` table (Bronze layer)
  - Added `sentiment_processed` flag for tracking processing state
  - Batch size: 100 comments per insert with conflict handling
- 📋 **Architecture Decision:** Removed Kafka from pipeline, moved to batch ETL with PostgreSQL
  - Medallion Architecture: Bronze (raw_comments) → Silver (product_sentiment) → Gold (product_rankings)
  - Better fit for micro-batch processing (every 4 hours)
  - Eliminates Kafka/Zookeeper operational overhead
  - Database staging allows debugging and reprocessing

**Previous Sessions (Kafka-based - Now Deprecated):**
- Created GPU detection and normalization pipeline
- Built sentiment analysis service with Kafka integration
- Implemented ABSA model with batched inference
- Added Kafka backpressure management and offset tracking

**Current Pipeline Status:**
- ✅ Data Ingestion → PostgreSQL (Bronze Layer) with async /run + /status endpoints
- ✅ Sentiment Analysis → PostgreSQL (Silver Layer) with async /run + /status endpoints
- ✅ Ranking Calculator → PostgreSQL (Gold Layer) with async /run + /status endpoints
- ✅ LLM Summary → PostgreSQL (product_summaries table) with async /run + /status endpoints
- ✅ Airflow Orchestration → HttpOperator + HttpSensor pattern with background threads
- ✅ Insights API → 5 endpoints serving rankings, search, comments, metadata
- ✅ Frontend → All pages, components, styling complete with mock data
- ⏳ Frontend Backend Integration → Need to connect React app to Insights API
