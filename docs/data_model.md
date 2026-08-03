# Data model

This covers the source database, how the fake data is generated, and how the
data is shaped in the warehouse.

## How the layers work

I use two ideas here and they are for different purposes, so worth separating
them.

**Medallion (bronze, silver, gold)** is about refinement. Bronze is the data as
it arrived, silver is cleaned, gold is business ready. It says nothing about
what shape the business ready layer takes.

**Star schema** is my modelling choice for gold. One fact table in the middle
holding the numbers, dimension tables around it holding the descriptions, one
join between them. I picked it because all three reports are the same kind of
question — take a measure, group it by some attribute — and that is what a star
is good at.

Dimensions are flat on purpose. For example `dim_product` carries the supplier name as a
plain column instead of pointing at a separate supplier dimension. That repeats
the name on every product row, but it saves a join in every query that needs it.
Normalise in the source, denormalise in the warehouse.

## The platform, as I understood it

The brief describes a drop-ship business:

- Suppliers are companies that offer products at a default price.
- Companies buy those products and sell them on to end customers.
- A company places one order and says which end customer receives the goods.
  There is no second transaction between company and customer — the same order
  covers both sides.
- End customers are recipients, not users. They are identified by document
  number, full name and date of birth, which is delivery information, not login
  information. So **they do not appear in the weblog**.
- Users of the website are companies and suppliers.

"Sales" in the monthly report means quantity times unit price on order lines,
grouped by the month of the order. The platform takes no commission in the
brief, so there is nothing else to count.

## Source database (Postgres)

| Table | What it holds |
|---|---|
| `companies` | CUIT, name, username, `is_supplier` flag |
| `customers` | document number (unique), full name, date of birth, owning company |
| `products` | name, default price, supplier |
| `catalog_items` | company, product, the price that company sells it at |
| `orders` | company, end customer, order timestamp |
| `order_lines` | order, product, quantity, unit price |

Suppliers are companies with a flag rather than a separate table, because the
brief says a supplier is just a different type of company.

`unit_price` is written onto the order line when the order is placed. It comes
from the company catalog, falling back to the supplier default price if the
product is not in the catalog. Snapshotting the price on the line is how real
systems work — a later price change must not rewrite history.

### CUIT

The Argentine tax id. Eleven digits, written `XX-XXXXXXXX-X`. The first two
digits say what kind of holder it is (30, 33, 34 for companies), the last digit
is a checksum over the first ten. I generate valid ones for the database and
some invalid ones for the spreadsheet, so the validator has something real to
catch. CUIT is also the key that matches a marketing lead back to a company.

## Generators

Three scripts under `generators/`. All of them are seeded, so the same data
comes out every time. The data still looks random, it is just the same random
data on every machine — which means the numbers in the reports are reproducible.

### Platform database

Written through SQLAlchemy, so it comes out clean. Foreign keys and constraints
are enforced by the database itself, which is realistic — a real OLTP system
would not let broken rows in. 

### Weblog

Lines in the Apache combined format. This is where most of the mess goes:

- malformed lines that do not parse
- usernames that match nobody on the platform
- missing or junk user-agent strings
- timestamps outside the expected range

IPs are drawn from a fixed set of country ranges, so the geo lookup has
something to resolve. User-agents cover desktop, mobile, tablet and a few bots.

### Marketing spreadsheet

An xlsx file with the mess a human file has: inconsistent casing, extra
whitespace, duplicate rows, mixed date formats, and some invalid CUITs.

Columns: lead name, company name, CUIT, email, phone, channel (ads, referral,
event, cold outreach), lead date, status, owner.

## Landing

One Parquet directory per source object, written in batches. Nothing is
transformed here. The point is that a failed load does not mean reading the
sources again.

## Bronze — `raw_*`
 
One table per landed dataset, loaded straight from Parquet. Same columns, same
values, nothing cleaned. Three columns are added to every table:
 
- `_loaded_at`
- `_run_id`
- `_source_file`
so any row in the warehouse can be traced back to the run that put it there.
 
Bronze stays untouched on purpose, and it is a complete copy of the source. If a
transformation is wrong, I fix the model and rebuild from bronze without going
back to Postgres or the files. That only works if nothing was filtered out on
the way in.
 
## Silver — `stg_*`
 
Silver prepares what gold needs, and nothing else. Cast types, rename columns,
trim whitespace, fix casing. One row in, one row out, no joins across sources,
no aggregation. Materialised as views since they are cheap.
 
Five models: `stg_companies`, `stg_products`, `stg_orders`, `stg_order_lines`,
`stg_weblog`.
 
`customers`, `catalog_items` and `leads` stop at bronze. Nothing in gold reads
them, so a staging model would be a view nobody selects from.
 
The marketing spreadsheet is worth saying more about, since it is one of the
three named sources. It goes through the whole ingest pipeline — extracted,
validated against the CUIT checksum and the date formats, bad rows quarantined
with a reason, landed as Parquet, loaded into bronze with lineage columns.
Nothing was skipped. It simply is not modelled above bronze, because modelling
exists to serve reports and no report reads it. The natural consumer would be a
lead conversion report, which is not in scope.
 
`stg_weblog` is the one model that does real work rather than renaming. It
parses the log line into columns, then derives device type, browser and OS from
the user-agent, and country from the IP. The IP to country mapping is a dbt seed
— a CSV in the project, versioned with everything else.
 
## What goes in gold
 
One rule runs through the whole warehouse: **bronze is complete, silver prepares
what gold needs, gold serves the reports.**
 
So gold only holds what a report reads. That is the point of the layer — it
exists to answer the three questions, not to model everything the business has.
There is no customer dimension and no catalog dimension: both exist in the
source, neither is something any of the three reports groups by.
 
## Gold — dimensions
 
| Model | Grain | Key | Main columns |
|---|---|---|---|
| `dim_date` | one day | `date_key` (YYYYMMDD) | date, year, quarter, month, month name, day of week |
| `dim_company` | one company | source id | CUIT, name, username, is_supplier |
| `dim_product` | one product | source id | name, default price, supplier name |
 
Source ids are used as keys where they exist. They are stable and unique, and it
means a warehouse row can be traced back to the source row without a lookup.
Generated keys only where there is no natural one.
 
## Gold — facts

a fact carries a dimension's key and nothing else from it; a dimension needs at least one attribute beyond its key, otherwise the value is degenerate and lives on the fact.
 
**`fct_order_lines`** — one row per order line.
 
Keys: date, company, product. Measures: quantity, unit price, line amount. `order_id` sits on the fact as a degenerate dimension — it is useful for
grouping lines into orders, but everything else about the order is already a key
on the line, so a separate order dimension would hold nothing.
 
**`fct_web_requests`** — one row per log line.
 
Keys: date, company (null when the username matches nobody), device, country.
`username` is degenerate. I call it requests rather than sessions because I do
not sessionise anything, and both reports work fine at request level.
 
## Gold — reports
 
**`rpt_top_devices`** — requests joined to devices, grouped by device type, top
five.
 
**`rpt_top_products_by_country`** — two steps. Find the country with the most
distinct companies logging in, then take the companies that logged in from
there, look at their order lines, and rank products by quantity. Nothing here
assigns a permanent country to a company; the link goes through the request
fact.
 
**`rpt_monthly_sales`** — order lines joined to dates, sum of line amount by
month, last twelve months.
 
The data quality report and the run summary are not dbt models. They read the
`rejects` and `job_runs` tables directly from the reporting CLI.


![dbt lineage](docs/img/lineage.png)

Generated by `dbt docs generate` from the `ref()` calls in the models — the
dependency graph is derived from the code, not drawn.

## Report decisions

A few of the three reports needed an interpretation. These are the readings I
took.

**Device classification.** Device type comes from pattern matching on the
user-agent string in SQL — a `CASE` with `LIKE` and regex, ordered so bots are
caught before anything else and tablets before mobiles. A production system
would parse user-agents at ingest with a maintained library, since the format
is decades of compatibility lies and every browser claims to be Mozilla. For a
generated log with a handful of shapes, pattern matching is honest enough.

**Most popular devices.** Counted by requests, not by distinct companies. A
company that logs in often weighs more than one that logs in once, which is
what "most popular" reads like to me. Suppliers are excluded, since the report
asks about clients. Anonymous requests drop out with them — they are real
device usage, but they cannot be attributed to a client.

**Most popular products by country.** The country is the one with the most
logins. A company qualifies if it logged in from that country at all, so a
company with traffic from several countries counts in each of them. Nothing
here assigns a permanent country to a company — the link goes through the
request fact, and it is a login-based question, not a registration-based one.
Ties on the country are broken by name, so the report gives the same answer
every run.

**Monthly sales.** Twelve complete months ending before the current one. The
current month is excluded because a partial period distorts a trend, and the
window is anchored to the start of the month rather than to today, so the row
count does not change depending on which day it runs.

**No dbt packages.** The date dimension is built with DuckDB's
`generate_series` rather than the `dbt_utils.date_spine` macro. The macro
exists because most warehouses have no convenient series generator; DuckDB
does, so there is nothing to install.