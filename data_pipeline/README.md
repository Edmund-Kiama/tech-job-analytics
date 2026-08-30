# Data Pipeline Documentation

## Overview

The data pipeline is the most mature and functionally complete layer in this repository. It is responsible for retrieving job data, preserving raw source snapshots, cleaning and normalizing the records, calculating salary insights, and persisting both the structured listings and the analytical summary snapshots.

This subsystem already behaves as the project’s analytical core and should be treated as a near-complete processing layer even though the surrounding backend and frontend are still evolving.

## Pipeline purpose

The project’s main analytical goal is to collect job market data, standardize it, and produce salary-related insight metrics that can be surfaced to users.

The pipeline supports this by performing the following:

- retrieving raw job records
- preserving bronze snapshot files
- cleaning records with pandas-based normalization logic
- normalizing salary values and derived midpoint values
- writing processed listings to SQLite
- computing descriptive salary statistics
- storing periodic analytical snapshots in the database

## Current maturity

The pipeline is already substantially complete. It includes the following implemented behaviors:

- source client integration
- bronze raw payload storage
- dataframe transformation pipeline
- location and salary normalization
- listing database persistence
- salary insight generation and storage
- repeated-run safety and snapshot creation logic
- coverage through a dedicated automated test suite

## End-to-end workflow

The core orchestration lives in [data_pipeline/services/pipeline.py](services/pipeline.py).

The full execution path is:

1. fetch job records from the Adzuna source client
2. build a payload containing the returned results
3. save a bronze snapshot of the source payload
4. load the bronze JSON into pandas
5. clean and normalize the records
6. persist the cleaned listings
7. compute salary statistics
8. produce and save one salary insight snapshot
9. return a summary of the run

## Major modules

### Clients

This package is responsible for source-specific integrations, especially the Adzuna client used to fetch jobs.

Relevant files:

- [data_pipeline/clients](clients)
- [data_pipeline/clients/adzuna.py](clients/adzuna.py)

### Storage

This package handles raw and bronze persistence logic.

Relevant files:

- [data_pipeline/storage/raw.py](storage/raw.py)
- [data_pipeline/storage/bronze_loader.py](storage/bronze_loader.py)

### Processing

This is the transformation and statistics engine.

Key files:

- [data_pipeline/processing/clean.py](processing/clean.py)
- [data_pipeline/processing/transform.py](processing/transform.py)
- [data_pipeline/processing/statistics.py](processing/statistics.py)

This layer is responsible for:

- missing-value handling
- string sanitization
- flattening nested Adzuna fields
- extracting country, region, and city data
- deriving normalized salary values
- measuring salary central tendency and spread
- identifying outliers

### Database

The database layer defines the project’s canonical model objects and connection handling.

Key files:

- [data_pipeline/database/models.py](database/models.py)
- [data_pipeline/database/connection.py](database/connection.py)

Persisted entities include:

- Listing
- SalaryInsight

### Services

This package coordinates the pipeline and the insight persistence workflow.

Key files:

- [data_pipeline/services/pipeline.py](services/pipeline.py)
- [data_pipeline/services/salary_insights.py](services/salary_insights.py)

### Scripts

This area contains operational helper scripts for initialization and inspection.

Key files:

- [data_pipeline/scripts/init_db.py](scripts/init_db.py)
- [data_pipeline/scripts/profile_jobs.py](scripts/profile_jobs.py)

### Tests

The pipeline has dedicated test coverage for its core behavior.

Relevant tests include:

- [data_pipeline/tests/test_pipeline.py](tests/test_pipeline.py)
- [data_pipeline/tests/test_clean_jobs.py](tests/test_clean_jobs.py)

These tests validate the end-to-end execution path and the transformation logic.

## Data model summary

### Listing

The Listing table stores a normalized job listing. It includes fields such as:

- id
- title
- description
- created timestamp
- redirect URL
- company name
- category label/tag
- location name and area components
- salary min/max values
- salary prediction flag
- normalized salary values

### SalaryInsight

The SalaryInsight table stores analytical snapshots generated for each pipeline execution. It includes fields such as:

- job_count
- salary_count
- mean_salary
- median_salary
- minimum_salary
- maximum_salary
- standard_deviation
- p25, p50, p75
- q1, q3, iqr
- lower/upper outlier counts
- analysis_version
- created_at

## Pipeline validation and quality rules

The current pipeline logic is designed to enforce several quality expectations:

- records without an id or title are discarded
- salary values of zero are treated as missing
- salary fields are standardized to GB annual values
- normalized midpoint values are derived from min/max when possible
- records are typed consistently before persistence

This ensures that downstream analytics are based on a reasonably clean and consistent dataset.

## Operational notes

### Re-run behavior

The pipeline is designed to be idempotent for listings while still creating new salary insight snapshots per run. This distinction is important:

- listing records should not be duplicated on repeated runs
- analytics snapshots should reflect the current run and remain historical

### Data lineage

The project preserves raw source payloads and bronze snapshots, which makes it easier to trace from original response to final output.

### Monitoring and debugging

When the pipeline is run, console output and stored bronze files give you a practical way to inspect how data flows through the system.

## Recommended future improvements

Even though the pipeline is mature, a few improvements would still increase maintainability:

- formal schema documentation for each persisted table
- a clearer contract for pipeline parameters and config values
- more explicit validation reporting for failed or skipped rows
- stronger operational dashboards for pipeline health and run history
- a defined schedule or orchestrator for production runs

## Current status

This pipeline is effectively the project’s analytical backbone and should be considered the most complete subsystem in the repository. It is the layer best positioned to support product development and downstream UI integration.
