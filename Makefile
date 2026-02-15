.PHONY: help install dev test build start stop clean logs

help:
	@echo "Odoo Cloud Platform - Available Commands"
	@echo ""
	@echo "  make install    Install dependencies"
	@echo "  make dev        Run development servers"
	@echo "  make test       Run tests"
	@echo "  make build      Build Docker images"
	@echo "  make start      Start all services"
	@echo "  make stop       Stop all services"
	@echo "  make clean      Clean up containers and volumes"
	@echo "  make logs       View logs"
	@echo ""

install:
	cd backend && pip install -r requirements.txt
	cd frontend && npm install

dev:
	@echo "Starting backend..."
	cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8001 &
	@echo "Starting frontend..."
	cd frontend && npm run dev

test:
	cd backend && python -m pytest

build:
	docker-compose build

start:
	docker-compose up -d

stop:
	docker-compose down

clean:
	docker-compose down -v
	rm -rf frontend/dist
	rm -rf backend/__pycache__

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend
