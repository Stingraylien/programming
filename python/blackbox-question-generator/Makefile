.PHONY: help install test run clean format lint

help:
	@echo "Black Box Question Generator - Available Commands"
	@echo ""
	@echo "make install       - Install dependencies"
	@echo "make test          - Run all tests"
	@echo "make run           - Start the API server"
	@echo "make test-api      - Test API endpoints"
	@echo "make clean         - Clean up generated files"
	@echo "make format        - Format code with black"
	@echo "make lint          - Lint code with flake8"

install:
	pip install -r requirements.txt

test:
	python -m pytest tests/ -v

run:
	python scripts/start_server.py

test-api:
	python scripts/test_api.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	rm -rf uploads/* outputs/*

format:
	black src/ api/ tests/

lint:
	flake8 src/ api/ tests/ --max-line-length=100