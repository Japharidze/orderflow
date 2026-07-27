up:
	docker compose up -d

seed:
	uv run python -m generators.seed_platform

etl:
	uv run python -m dwh.runner

psql:
	docker compose exec postgres psql -U dwh -d dwh_platform