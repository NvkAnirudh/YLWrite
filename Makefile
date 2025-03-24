.PHONY: install dev run-ui run-worker run-airflow init-airflow clean test help

# Show this help menu
help:
	@echo "Available commands:"
	@echo "  make install       - Install dependencies"
	@echo "  make dev           - Set up development environment"
	@echo "  make run-ui        - Run the Flask UI server"
	@echo "  make run-worker    - Run Celery worker"
	@echo "  make run-airflow   - Run Airflow webserver and scheduler"
	@echo "  make init-airflow  - Initialize Airflow database"
	@echo "  make clean         - Clean cache files and temporary files"
	@echo "  make test          - Run tests"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

dev:
	@echo "Setting up development environment..."
	pip install -r requirements-dev.txt
	pre-commit install

run-ui:
	@echo "Starting Flask UI server..."
	python run.py

run-worker:
	@echo "Starting Celery worker..."
	celery -A app.celery_worker.celery worker --loglevel=info

run-airflow:
	@echo "Starting Airflow webserver..."
	airflow webserver -p 8080 &
	@echo "Starting Airflow scheduler..."
	airflow scheduler

init-airflow:
	@echo "Initializing Airflow database..."
	airflow db init
	@echo "Setting up Airflow admin user..."
	airflow users create \
		--username admin \
		--firstname Admin \
		--lastname User \
		--role Admin \
		--email admin@example.com \
		--password admin

clean:
	@echo "Cleaning cache files..."
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	find . -type f -name ".coverage" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "*.egg" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".coverage" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	find . -type d -name ".tox" -exec rm -rf {} +
	find . -type d -name ".hypothesis" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +

test:
	@echo "Running tests..."
	pytest 