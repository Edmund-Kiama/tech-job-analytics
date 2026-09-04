# Project Documentation

This folder contains the project-level documentation for the UKJob Analytics repository.

## Scope

This project combines a Python-based data pipeline, a FastAPI backend, and a React frontend to collect, clean, analyze, and present job market data for technology roles.

## Current status

The data pipeline is the most mature and functionally complete part of the repository. It already performs end-to-end ingestion, cleaning, database persistence, and salary-statistic generation.

The backend and frontend are still under active development and should be treated as evolving application layers rather than fully stabilized production interfaces.

## Documentation map

- [architecture.md](architecture.md) – overall system design and module responsibilities
- [setup.md](setup.md) – local environment setup and startup workflow
- [data-flow.md](data-flow.md) – data lineage from source files to analytics outputs

## Repository layout

- [backend](../backend) – FastAPI application layer and request-facing logic
- [data_pipeline](../data_pipeline) – complete ingestion, transformation, validation, and analytics pipeline
- [frontend](../frontend) – React/Vite user interface currently under development
- [data](../data) – raw and bronze job data snapshots
- [pyproject.toml](../pyproject.toml) – Python tooling and project configuration

## Architectural summary

The repository follows a layered design:

1. Source data and bronze snapshots are stored in the data layer.
2. The data pipeline cleans and transforms the data into normalized listings.
3. Salary and market statistics are calculated and stored in the database.
4. The backend exposes processed data through API endpoints.
5. The frontend consumes those results and presents them to users.

## Pipeline maturity

The data pipeline already includes the following responsibilities:

- Adzuna data retrieval and ingestion
- bronze payload persistence
- dataframe-level cleaning and normalization
- standardized salary handling and midpoint generation
- SQLite persistence for listings and salary insights
- analytical snapshot generation for job market statistics

This means the pipeline can be treated as a near-complete analytical core, even though the app layer around it is still being finalized.

## Working assumptions

This project is intentionally structured to keep the pipeline independent from the frontend and backend implementation details. That allows the analytics layer to remain stable while the presentation layer continues to evolve.
