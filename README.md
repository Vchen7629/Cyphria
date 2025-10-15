# Cyphria
![React](https://img.shields.io/badge/React-19.0.0-orange)
![Python](https://img.shields.io/badge/Python-3.13-purple)
![Database](https://img.shields.io/badge/Database-PostgreSQL-cyan)
![NPM](https://img.shields.io/badge/NPM-23.6.1-blue)
![API](https://img.shields.io/badge/API-RedditApi-fcba03)
![Infrastructure](https://img.shields.io/badge/Infrastructure-K3S-blue)

## Table of Contents
1. [Overview](#project-overview)
2. [Features](#features)
3. [Project Structure](#project-structure)
4. [Quick Start](#quick-start)
5. [ML Model Details](#model-details)
6. [Monitoring and Observability](#monitoring-and-observability)
## Project Overview
A Social Media Sentiment and Trend Analysis Web Application. This project utilizes SBert for sentiment analysis and XGBoost for Category Classification

## Features 
### Machine Learning Models

| Model | Type | Accuracy | Parameters | Use Case |
|-------|------|----------|------------|----------|
| **SBert** | Transformer | ... | ... | Sentiment Analysis |
| **XGBoost** | Ensemble Gradient Boosted Trees | 92.11 | ... | Category Classification |

### Data Pipeline
- **Source**: Reddit Api with PRAW
- **Processing**: Ingested Data gets sent through Kafka topics which gets processed by the text classification and sentiment analysis workers
- **Storage**: Data is stored in a PostgreSQL (TimescaleDB) database to be queried later.
- **Scalability**: Lightweight Data processing workers can be easily horizontally scaled via k3s pods and nodes.


### Architecture
- **Frontend**: React interface
- **Backend**: FastApi and Apache Kafka
- **Data Stores**: PostgreSql and Redis
- **Infrastructure**: Kubernetes (K3s)

### Project Structure

```
Cyphria/
├── .github/workflows/                 # Github Actions files for running the CI/CD Pipeline
├── backend/data_processing/           # Data processing pipeline backend files
│   ├── category_classification        # XGBoost Text Classification
│        ├── src/components            # Service components like bounded internal queue, batching, etc
|        ├── src/configs               # files for configuring kafka settings, loading model
|        ├── src/middleware            # middleware like logging, kafka consumer/producer
|        ├── src/model                 # XGBoost model files
|        ├── src/training              # Folder containing components i used to train the model
|        ├── tests/integration         # integration tests
|        ├── tests/unit                # unit tests
|        └── dockerfile                # Dockerfile for containerizing the worker service
|   ├── data_ingestion                 # Data ingestion Service to get reddit posts from
│        ├── src/components            # Service components like fetching data
|        ├── src/configs               # files for configuring kafka settings, reddit praw 
|        ├── src/middleware            # middleware like logging, kafka producer
|        ├── src/preprocessing         # functions to do preprocessing like extracting select fields, removing stop words, removing url, etc
|        ├── tests/integration         # integration tests
|        ├── tests/unit                # unit tests
|        └── dockerfile                # Dockerfile for containerizing the worker service
│   ├──  post_embeddings               # Service for embedding the posts using a bert model
│        ├── src/components            # Service components like bounded internal queue, batching, etc
|        ├── src/configs               # files for configuring kafka settings, model
|        ├── src/middleware            # middleware like logging, kafka producer/consumer
|        ├── src/preprocessing         # functions to do preprocessing like extracting sentences, doing inference processing
|        ├── tests/integration         # integration tests
|        ├── tests/unit                # unit tests
|        └── dockerfile                # Dockerfile for containerizing the worker service
│   ├──  sentiment_analysis            # SBert model for sentiment analysis service
│        ├── src/components            # Service components like bounded internal queue, batching, etc
|        ├── src/configs               # files for configuring kafka settings, model
|        ├── src/middleware            # middleware like logging, kafka producer/consumer
|        ├── src/preprocessing         # functions to do preprocessing like sentence pairs, doing inference processing
|        ├── tests/integration         # integration tests
|        ├── tests/unit                # unit tests
|        └── dockerfile                # Dockerfile for containerizing the worker service
│   └── topic_classification           # Topic classification
│        ├── src/components            # Service components like bounded internal queue, batching, etc
|        ├── src/configs               # files for configuring kafka settings, model
|        ├── src/middleware            # middleware like logging, kafka producer/consumer
|        ├── src/preprocessing         # functions to do preprocessing like, doing inference processing
|        ├── tests/integration         # integration tests
|        ├── tests/unit                # unit tests
|        └── dockerfile                # Dockerfile for containerizing the worker service
├── backend/kafka_streams_aggregator   # Kafka streams aggregator to aggregate category topic and sentiment analysis topic
|        ├── src/main/java/cyphria     # folder containing service files
|            ├── aggregate/config      # folder for config like defining types, kafka
|            └── aggregate/middleware  # middleware like serialization, joining messages, logging
|        └── pom.xml                   # xml file defining dependencies
├── backend/insights-api               # Fast Api that handles user queries
|        ├── app/config/               # configuration files for kafka sub
|        ├── app/middleware/           # files for api middleware logic such as logging, auth, etc
|        ├── app/models/               # files for defining how db tables should be structured
|        ├── app/routes/               # files for handling api route logic
|        ├── app/schemas/              # files for defining how api requests and responses should be structured
|        ├── tests/integration/        # integration tests 
|        ├── tests/unit/               # unit tests
|        └── dockerfile                # Dockerfile for containerizing the fastapi service
|        └── main.py                   # entry point
├── frontend/                          # React application
|   ├── src/app/                       # Files for Redux Routing and State
|       ├── api-slices/                # logic for interacting with backend apis
|       ├── base/                      # config for backend api endpoints
|       ├── state/                     # global state managed by redux
|       └── store.ts                   # single source of truth for application state managed by redux
│   ├── src/features/category          # Folder containing all the files for the category feature
|       └── pages/                     # various pages used by this feature
|       └── components/                # UI components used for this feature
|       └── utils/                     # functions and logic used by this feature
│   ├── src/features/Homepage          # Folder containing all the files for the homepage feature
|       └── pages/                     # various pages used by this feature
|       └── components/                # UI components used for this feature
|       └── utils/                     # functions and logic used by this feature
│   ├── src/features/navbar            # Folder containing all the files for the navbar feature
|       └── components/                # UI components used for this feature
|       └── utils/                     # functions and logic used by this feature
│   ├── src/features/subreddits        # Folder containing all the files for the subreddit feature
|       └── pages/                     # various pages used by this feature
|       └── components/                # UI components used for this feature
|       └── utils/                     # functions and logic used by this feature
│   ├── src/features/topics            # Folder containing all the files for the post topics feature
|       └── pages/                     # various pages used by this feature
|       └── components/                # UI components used for this feature
|       └── utils/                     # functions and logic used by this feature
│   ├── shared/assets/                 # assets (svg, png, etc) used by more than one feature
|   ├── shared/components/             # Reusable components used by more than one feature
|   ├── shared/styles/                 # CSS styling used by more than one feature
|   ├── shared/utils/                  # Reusable functions used by more than one feature
│   ├── main.tsx                       # entry point
|   └── dockerfile                     # Dockerfile for containerizing react frontend
├── Infrastructure/Kubernetes          # Ansible Playbooks for provisioning an on premises k3s cluster
│       ├── cluster_roles              # yaml files for project infrastructure (CI/CD, Networking, k3s, Database)
│           ├── folder_name/defaults   # yaml files for helm chart configuration values
│           ├── folder_name/tasks      # yaml files for actually deploying the infrastructure component onto k3s
│           ├── folder_name/templates  # yaml files for kubernetes specific config (Secrets, ClusterIssuer, Certificates, etc)                       
├── Infrastructure/docker-compose.yaml # Docker Compose files for deploying local infrastructure via docker containers
├── .gitignore                       # Ignoring sensitive and unneeded files
└── README.md                        # This file
```
## Quick Start

### 1. Local Development

First Clone the project

```bash
git clone https://github.com/Vchen7629/Cyphria.git
```
#### Frontend Setup
Note: if you don't have node installed on your pc, you need to install it to use the package manager via: https://nodejs.org/en/download

```bash
cd frontend
npm install
npm run dev
```

#### Backend Setup
This project uses the [UV package manager](https://docs.astral.sh/uv/getting-started/installation/#standalone-installer) to manage dependencies.

Installing UV (Windows)

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
Skip the previous step if you have UV installed

```bash
cd backend

# Start Text Classification service
cd category_classification
uv sync 
uv run worker.py

# Start Data Ingestion
cd data_ingestion
uv sync
uv run worker.py

```

## Model Details

### XgBoost Text Classification

### Training Data

- **Dataset Size**: 12,000 Reddit Posts
- **Features**: Text Embeddings generated using [all-MiniLM-L12-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L12-v2)
- **Labels**: Category of the post

###  Hyperparams
Hyper-parameters were selected using RandomizedSearchCV and uses 5-fold cross validation
and iterates through a list of paramaters to find best paramters

* estimators: 300
* max-depth: 3
* learning-rate: 0.1

###  Performance Metrics

| Metric | XGBoost | 
|--------|---------------|
| **Accuracy** | 92.11% |
| **Precision** | 0.92 |
| **Recall** | 0.92 | 
| **F1-Score** | 0.92 | 
| **Inference Speed** | 10 ms | 
| **Memory Usage** | TBT | 

### Scalability Metrics

- **Throughput**: To be tested
- **Latency**: To be tested
- **Concurrency**: To be Tested
- **Worker Scaling**: Horizontal scaling via Kubernetes

## Monitoring and Observability

### Health Checks 
All workers/fastapi expose these endpoints for health checks
- **Backend**: /health endpoint
- **Model Metadata**: /api/v1/info

### Logging
All logs are in structured json logs

1. **Text Classification Logs**:
    - timestamp: ISO 8601 timestamp of event
    - level: Log error, can be INFO, ERROR
    - service: "text-classification-worker"
    - pod: Kubernetes Pod Name
    - event_type: can be either classification, kafka_consume, or db_insert
    - message: short desc of the event
    - post_id: unique post identifier
    - subreddit: Subreddit post is from
    - predicted_category: xgboost predicted category
    - inference_time_ms: inference time in ms
      
2. **Sentiment Analysis Logs**:
    - timestamp: ISO 8601 timestamp of event
    - level: Log error, can be INFO, ERROR
    - service: "sentiment-analysis-worker"
    - pod: Kubernetes Pod Name
    - event_type: can be either sentiment_analysis, kafka_consume, or db_insert
    - message: short desc of the event
    - post_id: unique post identifier
    - subreddit: Subreddit post is from
    - sentiment: sentiment of keyword in post
    - inference_time_ms: inference time in ms
      
3. **Reddit Api Data Ingestion Logs**:
    - timestamp: ISO 8601 timestamp of event
    - level: Log error, can be INFO, ERROR
    - service: "api-ingestion-worker"
    - pod: Kubernetes Pod Name
    - event_type: can be either ingest or kafka_produce
    - message: short desc of the event
    - post_id: unique post identifier
    - subreddit: Subreddit post is from
    - latency: latency time in ms

### Metrics
This project uses prometheus and grafana to view metrics. Backend services
will expose metrics on a /metrics endpoint

