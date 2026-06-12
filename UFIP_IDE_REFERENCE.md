# User Friction Intelligence Platform (UFIP)

## IDE Reference Document

### Project Type
AI-Powered Customer Friction Detection & Automated Recovery Platform

### Objective
Build a production-grade platform that continuously monitors user behavior, detects friction signals, assigns risk scores, clusters users into behavioral cohorts, and automatically generates recovery actions using a local LLM.

## High-Level Architecture

```text
MySQL Database
       │
       ▼
Feature Aggregation View
       │
       ▼
Prefect ETL Pipeline
       │
       ▼
Friction Scoring Engine
       │
       ▼
ML Clustering Layer
       │
       ▼
Generated Friction Dataset
       │
       ▼
Streamlit Dashboard
       │
       ▼
Ollama + Llama3
       │
       ▼
Recovery Recommendations
```

## Core Stack

- MySQL 8+
- SQLAlchemy + PyMySQL
- Pandas
- Prefect
- MLflow
- Scikit-Learn (KMeans)
- Streamlit
- Ollama
- Llama 3

## Folder Structure

```text
ufip/
├── app/
├── pipelines/
├── database/
├── models/
├── data/
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Success Criteria

- MySQL schema operational
- Aggregation view generates features
- Prefect flow runs end-to-end
- Friction scores generated
- MLflow logs experiments
- KMeans clustering works
- Streamlit dashboard functional
- Ollama generates recovery responses
