# Backend Documentation

## Purpose

The backend provides API access for the Tech Job Analytics application. It exposes data from the project’s database layer and acts as the application boundary between the frontend and the processing pipeline.

## Current implementation

The main API entry point is [backend/main.py](main.py). It creates a FastAPI app and exposes a /jobs endpoint.

The /jobs endpoint currently does the following:

- opens a database session
- queries the Listing model
- serializes the listing records into JSON-friendly dictionaries
- returns them to the client

## Current responsibilities

The backend currently handles:

- serving job listings
- converting database rows to JSON payloads
- enabling frontend access to processed data

## Interaction with other layers

The backend depends on the database model and data produced by the pipeline layer. In other words, it is intended to serve the results of data ingestion and cleaning rather than own the data processing logic itself.

## Directory structure

The backend directory is intentionally small at this stage, which suggests the project is still evolving from a prototype toward a fuller application architecture.

## Development guidance

As the backend grows, the following should be documented:

- API routes and HTTP methods
- request/response models
- validation and error handling
- auth or access concerns if they are added later
- database interaction boundaries

## Suggested next steps

- define a clearer service layer
- separate route handlers from business logic
- document endpoint contracts and sample responses
- add tests for API behavior

## Current status

The backend is functional for basic retrieval but still under development. The documentation should remain flexible as the API surface expands.
