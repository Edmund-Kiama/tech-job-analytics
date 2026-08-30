# Setup and Startup

## Prerequisites

Before running the project locally, ensure you have the following installed:

- Python 3.9+
- pip or another Python package manager
- Node.js and npm
- a virtual environment for the Python project
- access to the repository data files and any required local database files

## Python project setup

The Python configuration is defined in [pyproject.toml](../pyproject.toml).

Recommended workflow:

1. create a virtual environment at the repository root
2. activate it
3. install project dependencies
4. verify database and pipeline scripts can run

## Database initialization

The project uses SQLAlchemy with a SQLite database. The database schema is defined in [data_pipeline/database/models.py](../data_pipeline/database/models.py), and database creation is handled through initialization scripts such as [data_pipeline/scripts/init_db.py](../data_pipeline/scripts/init_db.py).

A typical setup flow is:

```bash
python -m data_pipeline.scripts.init_db
```

This creates the tables defined in the database models if they do not yet exist.

## Pipeline startup

The data pipeline is the most complete functional subsystem in the project. It is designed to run through the orchestration function in [data_pipeline/services/pipeline.py](../data_pipeline/services/pipeline.py).

The general execution path is:

1. instantiate the Adzuna client
2. fetch job records
3. save the bronze payload
4. clean and transform the data
5. persist listings
6. calculate salary statistics
7. save salary insight snapshots

In practice, the pipeline is typically run via Python execution or a script that imports and calls the pipeline function.

## Running the backend

The backend is implemented in [backend/main.py](../backend/main.py) and uses FastAPI.

Typical local startup workflow:

```bash
uvicorn backend.main:app --reload
```

This exposes the backend API and allows requests to the job listing endpoints.

## Running the frontend

The frontend uses Vite and React and is configured through [frontend/package.json](../frontend/package.json).

Typical local workflow:

```bash
cd frontend
npm install
npm run dev
```

The app is normally served on the default Vite local port, which is usually http://localhost:5173.

## Recommended local run order

Because the project includes both a data layer and an app layer, the following order is recommended:

1. initialize the database
2. run the pipeline to load and transform the data
3. start the backend
4. start the frontend
5. validate the end-to-end data flow

## Environment variable expectations

The project relies on configuration values such as:

- DATABASE_URL
- ADZUNA_APP_ID
- ADZUNA_APP_KEY
- ADZUNA_COUNTRY
- ADZUNA_BASE_URL

These are defined in [data_pipeline/config.py](../data_pipeline/config.py).

## Current status

The data pipeline is effectively complete enough to be treated as the project’s analytical core. The backend and frontend are still being developed and their startup and integration patterns may evolve as the application matures.

This file should be updated whenever the default run procedure or environment configuration changes.
