.PHONY: install run-dev run-docker migrate test lint

install:
	poetry install

run-dev:
	poetry run uvicorn src.app.main:app --reload

run-bot:
	poetry run python -m src.bot.main

run-docker:
	docker-compose up -d --build

migrate:
	poetry run alembic upgrade head

migration:
	poetry run alembic revision --autogenerate -m "$(msg)"

test:
	poetry run pytest

lint:
	poetry run ruff check . --fix
	poetry run black .
	poetry run mypy .
