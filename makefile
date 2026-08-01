up:
	docker compose up -d

seed:
seed_dwh:
	uv run python -m generators.dwh
seed_weblog:
	uv run python -m generators.weblog $(ARGS)
seed_leads:
	uv run python -m generators.leads
seed: seed_dwh seed_weblog seed_leads

etl:
	uv run python -m dwh.runner

psql:
	docker compose exec postgres psql -U dwh -d dwh_platform

diagrams:
	@command -v d2 >/dev/null || { echo "d2 not installed: https://d2lang.com"; exit 1; }
	d2 docs/diagrams/pipeline.d2 docs/img/pipeline.svg