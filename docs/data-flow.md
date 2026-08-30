# Data Flow

## Overview

The project is centered around a clear pipeline-driven flow that transforms raw job data into normalized listings and salary insights. This data flow is one of the strongest parts of the repository because it is already implemented and tested.

## End-to-end flow

```text
Job source data
  -> bronze/raw payload storage
  -> pandas dataframe loading
  -> cleaning and normalization
  -> listing persistence
  -> salary statistics calculation
  -> salary insight snapshot persistence
  -> backend API exposure
  -> frontend rendering
```

## Stage 1: source ingestion

The project can ingest data from an external provider such as Adzuna or from repository-stored mock data. The data ingestion flow is implemented primarily through the clients and storage modules in the data pipeline.

The bronze stage is important because it preserves the original response payload before transformation. This ensures the project retains raw source material for debugging and traceability.

## Stage 2: bronze storage

Raw payloads are written to the bronze directory under the data folder. This preserves a timestamped snapshot of each incoming dataset.

The bronze storage logic is implemented in:

- [data_pipeline/storage/raw.py](../data_pipeline/storage/raw.py)
- [data_pipeline/storage/bronze_loader.py](../data_pipeline/storage/bronze_loader.py)

This allows the project to:

- inspect original payload structure
- reprocess historical source records
- compare transformations across different runs

## Stage 3: dataframe parsing and cleaning

Bronze JSON data is loaded into a pandas DataFrame and transformed through the cleaning pipeline. The transformation logic handles:

- missing-value removal
- whitespace sanitization
- nested object flattening
- location extraction and normalization
- salary normalization and midpoint assignment
- dtype enforcement for database compatibility

Key files:

- [data_pipeline/processing/clean.py](../data_pipeline/processing/clean.py)
- [data_pipeline/processing/transform.py](../data_pipeline/processing/transform.py)

## Stage 4: database persistence

After transformation, the cleaned listing rows are persisted into the Listing table. This table stores the canonical structured representation of each job record.

Relevant files:

- [data_pipeline/database/models.py](../data_pipeline/database/models.py)
- [data_pipeline/services/pipeline.py](../data_pipeline/services/pipeline.py)

The listing model includes fields such as:

- title and description
- salary min/max values
- contract information
- company and location metadata
- normalized salary fields
- geographic details when present

## Stage 5: salary statistics and insights

Once listings are persisted, the pipeline calculates salary statistics and stores a snapshot of those values in the salary_insights table.

The analysis layer computes:

- mean, median, min, max
- standard deviation
- Q1 and Q3 values
- IQR
- sigma-based thresholds
- outlier counts and range summaries

This work is implemented in:

- [data_pipeline/processing/statistics.py](../data_pipeline/processing/statistics.py)
- [data_pipeline/services/salary_insights.py](../data_pipeline/services/salary_insights.py)

These statistics are not just transient calculations. They are persisted as a historical snapshot, which is useful for comparing market conditions over time.

## Stage 6: backend exposure

The backend reads from the database and returns the processed listing data to the client layer. The current API surface exposes listing records through the /jobs endpoint in [backend/main.py](../backend/main.py).

This means the backend is effectively a consumer of the pipeline’s persisted output, rather than the component that performs the transformation logic itself.

## Stage 7: frontend presentation

The frontend is intended to consume the backend data and render it visually. At this point, the pipeline is already producing the upstream data needed for the UI, which makes the frontend integration point much clearer than it would be in a less mature project.

## Why this flow is strong

The project’s core data flow is strong because it separates concerns cleanly:

- raw data is preserved
- transformation is explicit
- database persistence is structured and consistent
- analytical output is stored as a snapshot
- the backend consumes completed data instead of re-deriving it ad hoc

This makes the pipeline well suited for testing, debugging, and future extension.

## Current operational note

The pipeline is effectively complete enough to be treated as the project’s analytical core. The remaining work is mostly around integration and product maturity in the backend and frontend layers.
