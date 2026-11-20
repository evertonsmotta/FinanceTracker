
PYTHON := backend/.venv/bin/python
PIP := $(PYTHON) -m pip
COMPOSE := docker compose

.PHONY: help db-up db-down db-status db-test-up \
        db-test-migrate migrate migration-status \
        test test-cov run requirements requirements-install

help:
	@echo "FinanceTracker - Available commands"
	@echo ""
	@echo "  make db-up                Start development database"
	@echo "  make db-down              Stop Docker services"
	@echo "  make db-status            Show Docker services"
	@echo "  make db-test-up           Start test database"
	@echo "  make db-test-migrate      Apply test database migrations"
	@echo "  make migrate              Apply development migrations"
	@echo "  make migration-status     Show development migration status"
	@echo "  make test                 Run tests"
	@echo "  make test-cov             Run tests with coverage"
	@echo "  make run                  Start FastAPI development server"
	@echo "  make requirements         Export installed Python packages"
	@echo "  make requirements-install Install Python dependencies"

db-up:
	$(COMPOSE) up -d db

db-down:
	$(COMPOSE) stop

db-status:
	$(COMPOSE) ps

db-test-up:
	$(COMPOSE) up -d --wait db_test

db-test-migrate: db-test-up
	cd backend && .venv/bin/python -m alembic -x db=test upgrade head

migrate:
	cd backend && .venv/bin/python -m alembic upgrade head

migration-status:
	cd backend && .venv/bin/python -m alembic current

test:
	cd backend && .venv/bin/python -m pytest -v

test-cov:
	cd backend && .venv/bin/python -m pytest --cov=app --cov-branch --cov-report=term-missing -v

run:
	cd backend && .venv/bin/python -m uvicorn app.main:app --reload

requirements:
	$(PIP) freeze > backend/requirements.txt

requirements-install:
	$(PIP) install -r backend/requirements.txt
