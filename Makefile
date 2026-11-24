.PHONY: up down build logs ps test test-backend test-frontend clean help

# Default target
all: up

## up: Build and start all services in detached mode (PRD Section 6 mandatory)
up:
	docker compose up -d --build

## down: Stop and remove containers and networks (PRD Section 6 mandatory)
down:
	docker compose down

## build: Build all container images without starting
build:
	docker compose build

## logs: Tail logs from all running services
logs:
	docker compose logs -f

## ps: Show status of compose services
ps:
	docker compose ps

## test: Run both backend and frontend automated test suites
test: test-backend test-frontend

## test-backend: Run backend unit and integration test suite
test-backend:
	cd backend && if [ -d ".venv" ]; then . .venv/bin/activate && pytest -v; else pytest -v; fi

## test-frontend: Run frontend unit test suite
test-frontend:
	cd frontend && npm run test

## clean: Stop services and remove persistent volumes
clean:
	docker compose down -v

## help: Display this help message
help:
	@echo "Available make commands:"
	@grep -E '^## ' $(MAKEFILE_LIST) | sed -e 's/## //' | awk 'BEGIN {FS = ": "}; {printf "  \033[36m%-16s\033[0m %s\n", $$1, $$2}'
