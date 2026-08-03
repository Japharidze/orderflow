-- Pipeline run metadata. Created on every run; all statements are idempotent.

create sequence if not exists run_id_seq;
create sequence if not exists job_run_id_seq;

create table if not exists runs (
    run_id       bigint primary key,
    from_stage   varchar,        -- which stage the run was entered from
    status       varchar,        -- running | success | failed
    started_at   timestamp,
    finished_at  timestamp,
    error        varchar
);

create table if not exists job_runs (
    job_run_id     bigint primary key,
    run_id         bigint,
    stage          varchar,      -- ingest | bronze | transform
    job_name       varchar,      -- dataset name, or dbt_run / dbt_test
    status         varchar,      -- running | success | failed
    started_at     timestamp,
    finished_at    timestamp,
    rows_read      bigint,
    rows_written   bigint,
    rows_rejected  bigint,
    error          varchar
);

create table if not exists rejects (
    run_id      bigint,
    source      varchar,         -- which dataset the row came from
    raw_row     varchar,
    reason      varchar,
    rejected_at timestamp
);