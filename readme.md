# Cyphria
![React](https://img.shields.io/badge/React-19.0.0-orange)
![Python](https://img.shields.io/badge/Python-3.13-purple)
![Database](https://img.shields.io/badge/Database-PostgreSQL-cyan)
![NPM](https://img.shields.io/badge/NPM-23.6.1-blue)
![API](https://img.shields.io/badge/API-RedditApi-fcba03)
![Infrastructure](https://img.shields.io/badge/Infrastructure-K3S-blue)

## Table of Contents
1. [Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Project Architecture](#project-architecture)

## Project Overview
A web application that ranks products based on community sentiment on Reddit. Comments for various products are aggregated from related subreddits to figure out what people actually recommend and use.

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

1. Installing UV (Windows)

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```


## Project Architecture
- **Frontend**: React interface
- **Backend**: FastApi and Apache Airflow
- **Data Stores**: PostgreSql and Valkey
- **Infrastructure**: Kubernetes (K3s)

### Data Pipeline

The data pipeline is split into 2 categories, historic and daily

#### 1. Daily Batched Data Pipeline
Fresh sentiments for each product is ingested and processed daily for up to date rankings
- **Source**: Reddit Api with PRAW
- **Orchestration**: Apache airflow is used to ensure comments are processed in the correct order and trigger ingestion/processing 
for a different topic every hour of the day to avoid rate limits.
- **Processing**: Ingested Data is processed by seperate services for sentiment analysis, ranking, and summarization
- **Storage**: Data is stored in a PostgreSQL database to be queried later.

#### 2. Historic Backfill
Comments older than 1 month are pulled from monthly academic torrent sources to fill out the sentiment history
- **Source**: 
- **Processing**: The large dataset is processed via a Apache Spark Cluster
- **Storage**: Processed Data is stored in PostgreSQL database to be queried later