up:
	docker compose up -d

seed:
	uv run python -m generators.seed_platform

etl:
	uv run python -m dwh.runner

psql:
	docker compose exec postgres psql -U dwh -d dwh_platform

diagrams:
	@command -v d2 >/dev/null || { echo "d2 not installed: https://d2lang.com"; exit 1; }
	d2 docs/diagrams/pipeline.d2 docs/img/pipeline.svg