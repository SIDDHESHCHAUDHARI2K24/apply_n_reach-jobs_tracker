install:
	uv sync

dev:
	uv run uvicorn app.app:create_app --factory --reload --reload-dir app --loop asyncio

test:
	uv run python -m pytest

migrate:
	uv run alembic upgrade head

revision:
	uv run alembic revision -m "new migration"
