# Architecture

## Overview

The project is organized into a layered system whose core analytical engine is already largely complete.

The main architectural layers are:

- data pipeline: the operational core for collecting, cleaning, normalizing, and analyzing job data
- database layer: the persistence layer for listings and salary insight snapshots
- backend: the application/API interface for exposing processed results
- frontend: the presentation layer for end-user access and dashboards
- data: raw and bronze storage for source traceability

## The mature core: data pipeline

The data pipeline is the strongest and most complete part of the repository. It is responsible for the full transformation sequence from source payload to analytical output.

The current pipeline flow is:

1. job data is fetched from a source provider or mock data source
2. the raw payload is saved as a bronze snapshot
3. the bronze JSON is loaded into pandas
4. the dataset is cleaned and normalized
5. salary values are standardized and midpoint values are produced
6. transformed records are written to the listings table
7. descriptive salary statistics are calculated
8. a snapshot of analytics is stored in the salary_insights table

This workflow is executed by [data_pipeline/services/pipeline.py](../data_pipeline/services/pipeline.py).

## Component responsibilities

### Data ingestion and storage

The ingestion and storage layer is responsible for:

- fetching job records from Adzuna or repository fixture data
- saving immutable raw payloads to bronze storage
- preserving source records for auditing and debugging

Relevant implementation areas include:

- [data_pipeline/clients](../data_pipeline/clients)
- [data_pipeline/storage](../data_pipeline/storage)

### Cleaning and normalization

The cleaning and transformation layer ensures records are structurally consistent and ready for analysis. It handles:

- missing-value cleanup
- nested object flattening
- location normalization
- salary standardization
- dtype enforcement

This logic lives primarily in:

- [data_pipeline/processing/clean.py](../data_pipeline/processing/clean.py)
- [data_pipeline/processing/transform.py](../data_pipeline/processing/transform.py)

### Statistical analysis

The statistics engine calculates descriptive metrics and distribution-based summaries for job salary data. It supports:

- mean, median, min, max, standard deviation
- p25, p50, p75 quartiles
- IQR and outlier detection
- range and variance summaries

This logic is implemented in:

- [data_pipeline/processing/statistics.py](../data_pipeline/processing/statistics.py)

### Database layer

The database layer defines the canonical persisted representation of job data and analytics snapshots.

Key persistence objects include:

- Listing: normalized job listings
- SalaryInsight: statistical summary snapshots tied to a run or analysis version

Defined in:

- [data_pipeline/database/models.py](../data_pipeline/database/models.py)
- [data_pipeline/database/connection.py](../data_pipeline/database/connection.py)

### Backend layer

The backend acts as the API-facing layer over the processed project data. It is currently lightweight but is meant to serve the cleaned pipeline output to the frontend or other consumers.

Current implementation:

- [backend/main.py](../backend/main.py)

### Frontend layer

The frontend is a React/Vite interface that is intended to display job analytics and allow user interaction with the processed dataset. It is still under active development.

## Data-flow architecture

The repository currently follows this conceptual flow:

```text
Source data
  -> bronze/raw storage
  -> cleaning and transformation
  -> SQLite listings
  -> salary statistics
  -> salary insight snapshots
  -> backend API
  -> frontend UI
```

## Design strengths

The current architecture is strong for a project at this stage because it keeps the following concerns separated:

- source acquisition
- data storage
- transformation
- database persistence
- analytics
- API access
- UI presentation

This separation makes the pipeline easy to test, debug, and extend.

## Current limitations

The project is not yet a fully finalized production system. Key areas still evolving include:

- API contract standardization in the backend
- UI route structure and dashboard design in the frontend
- environment configuration for non-local deployments
- operational automation and deployment scaffolding

## Recommendation for future work

As the application matures, the team should formalize:

- database schema documentation
- endpoint contract documentation
- environment variable documentation
- deployment process documentation
- frontend-to-backend integration patterns

The pipeline, however, is sufficiently mature that it should be considered the backbone of the project and documented as such.
