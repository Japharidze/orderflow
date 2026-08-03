# --- infrastructure ---
up:
	docker compose up -d
down:
	docker compose down
psql:
	docker compose exec postgres psql -U b2b -d b2b_platform

# --- data generation ---
seed_platform:
	uv run python -m generators.platform
seed_weblog:
	uv run python -m generators.weblog $(ARGS)
seed_leads:
	uv run python -m generators.leads $(ARGS)
seed: seed_platform seed_weblog seed_leads # platform first on purpose

# --- elt ---
run:
	uv run python -m dwh.runner $(ARGS)

# examples:
#   make run
#   make run ARGS="--from bronze"
#   make run ARGS="--restart"
#   make run ARGS="--full-refresh"

# --- reports ---
report:
	uv run python -m dwh.reports $(ARGS)

# examples:
#   make report
#   make report ARGS="--runs"
#   make report ARGS="--quality"
#   make report ARGS="--all"

# --- development ---
dbt:
	cd dbt_project && uv run dbt run --profiles-dir .

dbt_test:
	cd dbt_project && uv run dbt test --profiles-dir .

dbt_docs:
	cd dbt_project && uv run dbt docs generate --profiles-dir . && uv run dbt docs serve --profiles-dir .

diagrams:
	@command -v d2 >/dev/null || { echo "d2 not installed: https://d2lang.com"; exit 1; }
	d2 docs/diagrams/pipeline.d2 docs/img/pipeline.svg

# --- everything --
all: up seed run report