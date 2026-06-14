.PHONY: setup start-db start-ollama start-prefect start-mlflow start-dashboard run-etl test clean

setup:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -e .[dev]

start-db:
	brew services start mysql

start-ollama:
	brew services start ollama

start-prefect:
	.venv/bin/prefect server start

start-mlflow:
	.venv/bin/mlflow server --host 127.0.0.1 --port 5001

start-dashboard:
	.venv/bin/streamlit run app/dashboard.py

run-etl:
	.venv/bin/python pipelines/etl_flow.py

test:
	PYTHONPATH=. TESTING=True .venv/bin/pytest tests/
