up:
	docker compose up -d

seed_platform:
	uv run python -m generators.platform
seed_weblog:
	uv run python -m generators.weblog $(ARGS)
seed_leads:
	uv run python -m generators.leads $(ARGS)
seed: seed_platform seed_weblog seed_leads # platform first on purpose

elt:
	uv run python -m dwh.runner

psql:
	docker compose exec postgres psql -U b2b -d b2b_platform

diagrams:
	@command -v d2 >/dev/null || { echo "d2 not installed: https://d2lang.com"; exit 1; }
	d2 docs/diagrams/pipeline.d2 docs/img/pipeline.svg