# User Friction Intelligence Platform (UFIP)

UFIP is an AI-powered customer friction detection and automated recovery platform.

## Architecture

1. **MySQL Database**: Stores event log streams, computed metrics, cohort groupings, and recovery actions.
2. **SQL view (`v_user_features`)**: Aggregates user telemetry features dynamically.
3. **Friction Scoring Engine**: Calculates experience health scores (0-100).
4. **KMeans Clustering & MLflow**: Cohorts users into behavioral clusters and tracks model metadata.
5. **Ollama & Llama 3**: Asynchronously pre-generates recovery suggestions for frustrated users.
6. **Streamlit Console**: Interactive operations dashboard.

## Setup & Execution

See the `Makefile` for shortcuts:
```bash
# Setup virtual environment and dependencies
make setup

# Start services
make start-db
make start-ollama

# Run the end-to-end processing pipeline
make run-etl

# Run dashboard console
make start-dashboard
```
