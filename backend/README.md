# Backend Documentation

FastAPI application for the UKJob Analytics frontend. The backend reads processed
job, application-tracking, salary-insight, and ingestion data from the database;
ingestion and transformation remain owned by `data_pipeline`.

## Running the API

Run commands from the repository root so both `backend` and `data_pipeline` are
importable:

```bash
uvicorn backend.main:app --reload
```

The application reads environment variables through `data_pipeline.config`.
`DATABASE_URL` is required by the SQLAlchemy engine. `CORS_ORIGINS` is a
comma-separated list of allowed origins; when it is empty, the current
implementation falls back to `[*]`. Adzuna settings are consumed by the
pipeline and are listed in `data_pipeline/config.py`.

FastAPI also exposes generated documentation at `/docs` (Swagger UI) and
`/redoc` (ReDoc), with the OpenAPI schema at `/openapi.json`.

At startup, the application starts the pipeline scheduler. It shuts the
scheduler down when the application lifespan ends.

## API overview

All routes are relative to the server root. There is currently no authentication
or version prefix.

### Jobs

#### `GET /jobs`

Returns a paginated list of listings.

Query parameters:

| Parameter             | Type    | Default        | Notes                                           |
| --------------------- | ------- | -------------- | ----------------------------------------------- |
| `page`                | integer | `1`            | Minimum `1`                                     |
| `page_size`           | integer | `25`           | `1` to `100`                                    |
| `search`              | string  | omitted        | Searches title, company, and description        |
| `category`            | string  | omitted        | Case-insensitive category match                 |
| `location`            | string  | omitted        | Searches location, city, region, and country    |
| `contract_type`       | string  | omitted        | Case-insensitive match                          |
| `contract_time`       | string  | omitted        | Case-insensitive match                          |
| `min_salary`          | number  | omitted        | Minimum `0`; overlaps normalized salary maximum |
| `max_salary`          | number  | omitted        | Minimum `0`; overlaps normalized salary minimum |
| `salary_is_predicted` | boolean | omitted        | Filter predicted salaries                       |
| `is_active`           | boolean | omitted        | Filter active or inactive listings              |
| `sort`                | enum    | `created_desc` | See [sort values](#job-sort-values)             |

Response: `JobListResponse`.

#### `GET /jobs/{job_id}`

Returns one listing as `JobResponse`. This response includes `adref`, which is
not included in the list response. Returns `404` when the ID does not exist.

### Applications

Applications are stored on the listing record and are updated through the
application-tracking service.

#### `GET /applications`

Returns a list of tracked jobs as `ApplicationJobResponse` objects. Without a
`status` filter, jobs with status `NEW` are excluded.

| Parameter  | Type    | Default | Notes                                                  |
| ---------- | ------- | ------- | ------------------------------------------------------ |
| `status`   | enum    | omitted | See [application statuses](#application-status-values) |
| `priority` | integer | omitted | `1` to `3`                                             |

#### `GET /jobs/{job_id}/application`

Returns the job’s `ApplicationResponse`. The underlying tracker may raise a
not-found error for an unknown job.

#### `PATCH /jobs/{job_id}/application`

Updates application-tracking fields and returns `ApplicationResponse`.

Request body (`ApplicationUpdate`):

```json
{
  "application_status": "APPLIED",
  "user_priority": 3,
  "follow_up_at": "2026-09-10T09:00:00Z",
  "application_notes": "Follow up after one week"
}
```

All fields are optional. `user_priority` must be between `1` and `3`.
`application_status` is optional at schema-validation time, but the tracker
accepts only the statuses listed below. Dates are ISO 8601 datetimes.

### Analytics

Analytics routes are under `/analytics`. They currently use a flexible response
model while the individual payload contracts are being stabilized. The JSON
returned by each handler is as follows:

| Method and path                          | Purpose and top-level response keys                                                                                                                                                                     |
| ---------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GET /analytics/prioritization/{job_id}` | Scores one job. Query parameters are comma-separated `target_titles`, `preferred_categories`, `preferred_locations`, and `preferred_contract_types`; returns `job` plus prioritization score fields.    |
| `GET /analytics/prioritization`          | Scores active jobs and paginates them. Uses the same four profile parameters plus `page` (default `1`) and `page_size` (default `20`, maximum `100`). Returns `page`, `page_size`, `total`, and `jobs`. |
| `GET /analytics/metadata`                | Returns filter options: `categories`, `locations`, `contract_time`, `contract_type`, and `salary_prediction`.                                                                                           |
| `GET /analytics/trends`                  | Returns `daily`; each item has `date`, `jobs_added`, `jobs_inactivated`, and `active_jobs`.                                                                                                             |
| `GET /analytics/summary`                 | Returns the latest salary insight: timestamps, analysis version, counts, and mean, median, minimum, maximum, and standard deviation.                                                                    |
| `GET /analytics/salary`                  | Returns the latest insight with `distribution`, `standard_deviation_ranges`, `outliers`, `salary_coverage`, and `salary_ranges`.                                                                        |
| `GET /analytics/breakdown`               | Returns `job_status`, `top_salary_jobs`, `top_categories`, `top_locations`, `top_companies`, `contract_time`, `contract_type`, and `salary_prediction`.                                                 |
| `GET /analytics/categories`              | Returns `categories`, an alphabetized list of available category labels.                                                                                                                                |
| `GET /analytics/categories/{category}`   | Returns category, job count, salary statistics, and up to ten `top_jobs`; only active jobs are analyzed.                                                                                                |
| `GET /analytics/salary/distribution`     | Optional `category` filter. Returns scope, job and salary counts, histogram `bins`, and salary `statistics`. Only active listings with a normalized midpoint are included.                              |

Analytics endpoints that require data return `404` when no matching salary,
category, or active salary records exist.

### System and ingestion

#### `GET /health`

Checks database access and returns `status`, `database`, `listings`, and
`latest_ingestion`. A database failure returns `503`.

#### `GET /ingestion/status`

Returns the latest ingestion status and job totals. When no ingestion has run,
the response is `{ "status": "never_run", "last_run": null, "jobs": ... }`.
After a run, it also includes run timestamps, row counters, inserted/updated/
inactivated counts, salary insight ID, analysis version, bronze path, and any
error message.

#### `GET /ingestion/runs`

Returns paginated `IngestionRunResponse` records in newest-first order.
`page` defaults to `1`; `page_size` defaults to `20` and is limited to `100`.
The response is `IngestionRunListResponse` with `pagination` and `runs`.

## Schemas

### Common response models

- `Pagination`: `page`, `page_size`, `total`, and `total_pages`.
- `PaginatedResponse[T]`: generic `items` plus `pagination`.
- `ErrorResponse`: `{ "error": { "code": string, "message": string } }`.
- `FlexibleResponse`: compatibility wrapper for evolving analytics payloads;
  it permits additional fields.

### JobResponse fields

`JobResponse` contains the listing identity and source data: `id`, required
`title`, `description`, `created`, `redirect_url`, `adref`, salary fields,
contract fields, company/category/location fields, coordinates, and currency
and period fields. It also contains normalized salary values:
`normalized_salary_min`, `normalized_salary_max`, and
`normalized_salary_midpoint`.

Tracking and lifecycle fields are `first_seen_at`, `last_seen_at`, `is_active`,
`inactive_at`, `application_status`, `saved_at`, `applied_at`, `follow_up_at`,
`user_priority`, and `application_notes`. All fields except `id` and `title` are
optional in the response model.

`ApplicationJobResponse` is the compact listing shape used by
`GET /applications`. `ApplicationResponse` contains the job ID, status, and
tracking timestamps, priority, and notes.

### Enum values

#### Job sort values

`created_asc`, `created_desc`, `salary_asc`, `salary_desc`, `title_asc`,
`title_desc`, `company_asc`, `company_desc`.

#### Application status values

`NEW`, `SAVED`, `APPLIED`, `INTERVIEW`, `OFFER`, `REJECTED`, `ARCHIVED`.

## Error handling and validation

The global exception handlers return the same error envelope for HTTP errors and
FastAPI validation failures:

```json
{
  "error": {
    "code": "INVALID_QUERY",
    "message": "..."
  }
}
```

The main error codes are:

| HTTP status | Code                   | Typical cause                           |
| ----------- | ---------------------- | --------------------------------------- |
| `404`       | `JOB_NOT_FOUND`        | Unknown job ID                          |
| `404`       | `CATEGORY_NOT_FOUND`   | No active jobs for a category           |
| `404`       | `NO_ANALYTICS`         | No salary insight exists                |
| `404`       | `NOT_FOUND`            | Other missing resource                  |
| `422`       | `INVALID_QUERY`        | Invalid query or request body           |
| `503`       | `DATABASE_UNAVAILABLE` | Health check cannot access the database |
| other       | `API_ERROR`            | Unclassified HTTP error                 |

Query constraints are enforced by FastAPI. Invalid pagination, salary, priority,
or enum values produce `422`.

## Backend structure

```text
backend/
├── main.py                    # FastAPI app, middleware, lifespan, errors
├── api/
│   ├── schemas.py              # Public response models and enums
│   └── routers/
│       ├── jobs.py             # Job listing and detail routes
│       ├── applications.py     # Application tracker routes
│       ├── analytics.py        # Analytics route registration
│       └── system.py           # Health and ingestion routes
└── services/
		├── jobs.py                 # Listing queries, filters, sorting, serialization
		├── applications.py         # Application query and update adapters
		├── analytics.py            # Prioritization and analytics calculations
		└── system.py               # Health and ingestion status queries
```

### Database and pipeline boundary

The backend services use SQLAlchemy sessions created from the shared engine in
`data_pipeline.database.connection`. The main database entities are:

- `Listing`: job source fields, normalized salary fields, lifecycle state, and
  application-tracking fields.
- `SalaryInsight`: latest aggregate salary analysis used by summary and salary
  endpoints.
- `IngestionRun`: pipeline run metrics and status used by system endpoints.

The backend does not ingest Adzuna data or perform cleaning. The pipeline writes
those records, and the API reads and serializes them for the frontend.

## Development notes

- Keep route handlers thin; put database queries and response shaping in the
  corresponding service module.
- Update `backend/api/schemas.py` when a public response contract is finalized.
- Keep analytics response changes synchronized with the frontend because those
  routes currently use `FlexibleResponse`.
- Add API tests for filters, pagination, application transitions, error envelopes,
  and empty-database behavior as the endpoint contracts settle.
