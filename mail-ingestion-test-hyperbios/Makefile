VENV ?= .venv
PYTHON ?= python3

.PHONY: setup test lint run-local local-up local-send

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install -U pip
	$(VENV)/bin/pip install -e .[dev]

test:
	$(VENV)/bin/pytest

lint:
	$(VENV)/bin/ruff check src tests

local-up:
	docker compose up -d

local-send:
	$(VENV)/bin/ingestion-tester local-send --scenario BANK_RELEVE_JAN
