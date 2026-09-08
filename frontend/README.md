# UK Job Analytics Frontend

The frontend is the browser application for **UK Job Analytics**. It turns the collected UK technology-job data into a workspace where a person can search listings, compare salary and market patterns, prioritize opportunities, and track applications.

This document serves two audiences:

- **People using the product:** the sections on capabilities and workflows explain what the workspace is for in plain language.
- **Developers maintaining it:** the sections on setup, architecture, routes, API integration, configuration, and validation describe how the application works.

## Live application

The current production frontend is available at [tech-job-analytics.vercel.app](https://tech-job-analytics.vercel.app/).

The deployment serves the Vite single-page application from Vercel. The UI still requires a reachable backend API for health checks, listings, analytics, recommendations, applications, and ingestion status; the public URL alone does not provide a database or API service.

## What the product does

The application helps someone move from "What jobs are available?" to "Which opportunities should I act on?" It provides:

- A dashboard with an overview of the current job market.
- Searchable and filterable job listings.
- Individual job detail pages.
- Salary statistics, distributions, category comparisons, and market trends.
- Recommended jobs ranked against a saved job-search profile.
- Application tracking with status, priority, notes, and follow-up dates.
- Category and company views for comparing the market.
- Data-health and ingestion views for understanding whether the data is current.
- Light, dark, and system theme options.
- Installable Progressive Web App behavior through a service worker and web manifest.

The frontend is a client-side React application. It does not own the job database or ingestion pipeline; it requests that information from the backend API.

## Technology

- **React 19** for the user interface.
- **TypeScript** for application code and API response types.
- **Vite** for local development and production bundling.
- **React Router** for client-side navigation.
- **Tailwind CSS 4** and the Tailwind Vite plugin for styling.
- **Recharts** for analytics visualizations.
- **React Icons** for interface icons.
- **vite-plugin-pwa** for service-worker generation and installable-app metadata.
- **ESLint** and **Prettier** for code quality and formatting.

## User guide

### Starting the workspace

When the application opens, it checks the backend health endpoint before rendering the workspace. While that check is running, a boot/loading state is shown. If the backend cannot be reached, the application displays the connection error instead of showing an empty dashboard.

The application uses `/uk` as its base path. Opening `/` redirects to `/uk/dashboard`.

### Exploring jobs

Use **Jobs** to search and narrow the listing dataset. The API-backed filters include:

- Free-text search.
- Category and location.
- Contract time and contract type.
- Minimum and maximum salary.
- Whether salary is predicted.
- Active/inactive status.
- Sort order and pagination.

Selecting a listing opens a job detail page. A listing can expose its source/application link and its application-tracking controls.

### Understanding analytics

The analytics area is split into three views:

- **Salary:** salary distribution and summary statistics.
- **Market:** breakdowns such as categories, locations, contract types, job status, and top-paying jobs.
- **Trends:** changes in the dataset over time.

Additional category and company pages make it easier to compare a specific part of the market without manually interpreting the full dashboard.

Salary values are supplied by the backend. A salary may be an advertised range, a midpoint-derived value, or a predicted value, so the interface should be read as an analysis of the available data rather than a guarantee of an offer.

### Sidebar analytics pages explained in detail

The sidebar exposes three dedicated analytics workspaces. Each one is a different lens on the same job dataset, and they are intentionally designed to answer a different decision question.

#### 1) Salary analytics

Route: `/analytics/salary`

This is the compensation analysis page. It is built to answer: "What is the market paying, and how much salary coverage do I actually have?"

What it shows:

- A salary distribution histogram for all jobs, with optional filtering by category.
- Summary statistics such as minimum, Q1, median, mean, Q3, maximum, IQR, and standard deviation.
- Coverage metrics showing how many listings include minimum salary, maximum salary, midpoint salary, and complete salary ranges.
- A top-paying jobs table that ranks the highest-paid listings by normalized midpoint salary.

How it behaves:

- On load, the page requests salary statistics, a market summary, analytics metadata, and a market breakdown.
- It also fetches a detailed salary distribution for the selected category (or for all jobs when no category is chosen).
- The category selector lets a user compare a single segment such as a technology field against the full market.
- The histogram includes vertical reference lines for mean and median, so the spread can be interpreted quickly.
- The table of high-paying jobs is useful for noticing outlier roles or unusually strong compensation bands.

Why it matters:

- This page is the strongest tool for comparing offers, understanding salary bands, and spotting which categories or segments sit above or below the market median.
- It also helps explain whether the data is strong enough to rely on for compensation decisions: coverage and outlier counts show whether the salary picture is broad or sparse.

#### 2) Market analysis

Route: `/analytics/market`

This is the market-structure page. It is designed to answer: "Where is the highest demand, and how is the market distributed across categories and employers?"

What it shows:

- Job counts by category, plotted as a horizontal bar chart.
- Mean and median salary by category, allowing quick comparison between the biggest categories and their compensation levels.
- Job counts by location and salary by location.
- Contract-time mix (for example, permanent versus temporary or other contract arrangements).
- Contract-type mix for the current dataset.
- Salary prediction breakdown to show how many jobs include predicted salary values versus non-predicted values.

How it behaves:

- The page focuses on the backend analytics breakdown response rather than raw listing data.
- It aggregates job counts and salary metrics by category, location, and employment shape so the user can compare market composition without reading every listing individually.
- The visual layout separates volume and pay into different panels, which makes the difference between demand and compensation easier to interpret.
- It is especially useful when the question is not just "what jobs pay well?" but "which segments of the market have the most jobs and where are the strongest opportunities?"

Why it matters:

- This page helps a user evaluate which parts of the market are crowded, which geographies are strongest, and which types of contracts dominate the dataset.
- It is the best place to understand the overall shape of the market before narrowing down individual job matches.

#### 3) Market activity

Route: `/analytics/trends` and compatibility alias `/job/analytics/trends`

This is the historical market change page. It answers: "Is the market growing, shrinking, or shifting month to month?"

What it shows:

- A time-series line chart of job additions over time.
- A line for jobs inactivated over time.
- A line for the active job count over time.
- A summary panel for the latest observed date showing added, inactivated, and active jobs.

How it behaves:

- The page requests the trend dataset from the backend and renders a line chart keyed by date.
- It compares change in new jobs versus removed or inactivated jobs, while also tracking the cumulative active pool.
- This makes it easier to notice whether market activity is expanding, contracting, or plateauing.
- The page is intentionally simpler than the salary or market pages: it explains movement in the overall dataset rather than per-role compensation or category composition.

Why it matters:

- Trend analysis helps a user decide whether current opportunities are part of a large, growing market or a shrinking one.
- It is useful when evaluating timing, market sentiment, and whether the current data volume appears stable or volatile.

These three analytics views work together as a decision-making stack: salary answers pay, market answers composition, and trends answer direction of change.

### Using recommendations

The **Recommended** view uses a saved profile containing target titles, preferred locations, preferred categories, and preferred contract types. The backend returns a ranked list with a priority score and, where available, the factors explaining the ranking.

The profile is stored in the browser's `localStorage`, so it is local to the current browser/device. It is not an account profile and is not synchronized between devices.

### Tracking applications

Application information is stored through the backend API. A job can have one of these statuses:

`NEW`, `SAVED`, `APPLIED`, `INTERVIEW`, `OFFER`, `REJECTED`, or `ARCHIVED`.

The tracker also supports a user priority, notes, an application date, and a follow-up date. **Applications** provides a filtered view of tracked jobs, while **Follow-ups** surfaces overdue and upcoming actions within the configured reminder window.

### Checking data health

The **Data health** page is primarily an operational view. It combines backend health, listing counts, the latest ingestion status, and recent ingestion runs. It helps a user or maintainer distinguish "there are no matching jobs" from "the data service is unavailable or stale."

### Personalizing the workspace

Settings currently include:

- Default jobs per page.
- Default job sort order.
- Whether predicted salaries are shown.
- Whether the dashboard refreshes on load.
- The follow-up reminder window.
- The recommendation profile described above.

Workspace settings and the recommendation profile are persisted in `localStorage` under `workspace-settings` and `job-profile`. The selected theme is stored under `theme`.

## Application routes

All routes below are relative to the `/uk` base path.

| Route                   | Purpose                                         |
| ----------------------- | ----------------------------------------------- |
| `/dashboard`            | Market overview and dashboard analytics         |
| `/jobs`                 | Search, filter, sort, and paginate job listings |
| `/jobs/:jobId`          | Details and application actions for one job     |
| `/recommended`          | Ranked jobs based on the saved profile          |
| `/applications`         | Tracked applications                            |
| `/follow-ups`           | Upcoming and overdue follow-up actions          |
| `/analytics/salary`     | Salary analytics                                |
| `/analytics/market`     | Market breakdowns                               |
| `/analytics/trends`     | Time-based market trends                        |
| `/job/analytics/trends` | Compatibility alias for the trends view         |
| `/categories`           | Category-level job and salary analysis          |
| `/companies`            | Employer presence and salary comparison         |
| `/data-health`          | Backend and ingestion health                    |
| `/settings`             | Workspace and recommendation preferences        |

The application also has built-in error and not-found states. The root path redirects to the dashboard, and unknown routes show a recoverable 404 page.

## Repository layout

```text
frontend/
|-- public/                 # Static files copied as-is into the build
|   `-- icons/              # PWA icons
|-- src/
|   |-- App.tsx             # Router, startup health check, app state
|   |-- api.ts              # Typed frontend-to-backend request functions
|   |-- main.tsx            # React entry point and initial theme setup
|   |-- pwa.ts              # Service-worker registration
|   |-- index.css           # Global styles and Tailwind entry styles
|   |-- assets/             # Source-controlled imported assets
|   |-- components/         # Shared layout, panels, loaders, and controls
|   |   `-- dashboard/      # Dashboard-specific components
|   |-- hooks/              # Reusable React hooks, including theme state
|   |-- pages/              # Route-level screens
|   `-- typings/            # Shared API and domain TypeScript types
|-- .env.example            # Local environment variable template
|-- eslint.config.ts        # ESLint configuration
|-- index.html              # HTML shell and document metadata
|-- package.json            # Scripts and dependencies
|-- tsconfig.json           # TypeScript compiler configuration
|-- vercel.json             # SPA fallback rules for Vercel
`-- vite.config.ts         # Vite, Tailwind, and PWA configuration
```

`dist/` and `dev-dist/` are generated build/service-worker output. They should not be edited by hand.

## Local development

### Prerequisites

- Node.js and npm compatible with the versions used by the repository's lockfile.
- A running backend API that implements the endpoints listed in [API integration](#api-integration).

### Install and run

From the repository root:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Vite normally serves the development app at `http://localhost:5173`. The exact port is printed in the terminal and may change if that port is already occupied.

The frontend performs a health check immediately. A working page therefore requires the backend to be reachable at the configured API base URL, even if a particular page has no data to display.

### Useful development commands

Run these commands from `frontend/`:

| Command                | Purpose                                                                  |
| ---------------------- | ------------------------------------------------------------------------ |
| `npm run dev`          | Start the Vite development server                                        |
| `npm run build`        | Create a production build in `dist/` and generate the PWA service worker |
| `npm run preview`      | Serve the production build locally                                       |
| `npm run typecheck`    | Run TypeScript without emitting files                                    |
| `npm run lint`         | Run ESLint across the frontend                                           |
| `npm run format`       | Format frontend files with Prettier                                      |
| `npm run format:check` | Check formatting without changing files                                  |

For a production-style local check:

```bash
npm run typecheck
npm run build
npm run preview
```

## Configuration

Copy `.env.example` to `.env` for local development. Vite exposes only variables prefixed with `VITE_` to browser code.

| Variable                 | Required | Description                                                                                                                                                  |
| ------------------------ | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `VITE_API_BASE_URL`      | No       | URL prefix used for backend requests. Leave empty when the API is served from the same origin; set it to a backend origin or reverse-proxy path when needed. |
| `VITE_DEFAULT_PAGE_SIZE` | No       | Reserved configuration value for the default listing page size. The current app-level default is defined in `App.tsx` settings.                              |

Do not put secrets in frontend environment variables. Anything exposed through `import.meta.env` is shipped to the browser and must be treated as public.

## API integration

The request boundary is centralized in [src/api.ts](src/api.ts). It prefixes every endpoint with `VITE_API_BASE_URL`, sends JSON headers, parses common backend error shapes, and throws an `Error` for non-2xx responses. Pages own their loading, success, empty, and error states.

The current request surface is:

| Endpoint                                | Used for                                                        |
| --------------------------------------- | --------------------------------------------------------------- |
| `GET /health`                           | Startup and data-health checks                                  |
| `GET /jobs`                             | Filtered, sorted, paginated listings                            |
| `GET /jobs/{jobId}`                     | One job's details                                               |
| `GET /jobs/{jobId}/application`         | One job's application record                                    |
| `PATCH /jobs/{jobId}/application`       | Update application status, priority, notes, or follow-up date   |
| `GET /applications`                     | Tracked applications, optionally filtered by status or priority |
| `GET /analytics/salary`                 | Salary statistics                                               |
| `GET /analytics/salary/distribution`    | Salary bins and outliers                                        |
| `GET /analytics/metadata`               | Analytics metadata such as categories                           |
| `GET /analytics/breakdown`              | Market breakdowns                                               |
| `GET /analytics/trends`                 | Daily trend data                                                |
| `GET /analytics/summary`                | High-level market summary                                       |
| `GET /analytics/categories`             | Available categories                                            |
| `GET /analytics/categories/{category}`  | Analytics for one category                                      |
| `GET /analytics/prioritization`         | Ranked recommendations                                          |
| `GET /analytics/prioritization/{jobId}` | Prioritization details for one job                              |
| `GET /ingestion/status`                 | Latest ingestion state and counts                               |
| `GET /ingestion/runs`                   | Ingestion history                                               |

The TypeScript interfaces in [src/typings/api-typings.ts](src/typings/api-typings.ts) describe the main job, analytics, pagination, prioritization, ingestion, and application shapes. When the backend contract changes, update the request function and its corresponding type together.

### Same-origin and cross-origin setups

With an empty `VITE_API_BASE_URL`, requests are relative, for example `/jobs`. This is appropriate when a reverse proxy or hosting platform sends frontend and API traffic to the same origin.

For a separately hosted backend, set a complete URL such as `https://api.example.com` and ensure the backend permits requests from the frontend origin through its CORS policy. Rebuild the frontend after changing Vite environment variables; they are read at build time.

## Build and deployment

`npm run build` produces a static single-page application in `dist/`. The Vite PWA plugin also generates:

- A web manifest with the application name, icons, standalone display mode, and `/` start URL.
- A service worker with precaching and an `/index.html` navigation fallback.

The Vercel configuration rewrites all incoming paths to `index.html`, which allows client-side routes such as `/uk/jobs` to work after a direct refresh. Any other static host must provide the equivalent SPA fallback behavior.

The deployed frontend still needs access to the backend API. Configure `VITE_API_BASE_URL` in the deployment environment before building, or deploy the API behind the same origin. A frontend deployment without a reachable `/health` endpoint will remain on the boot/error screen.

### Vercel deployment

The production frontend is deployed at [https://tech-job-analytics.vercel.app/](https://tech-job-analytics.vercel.app/). The Vercel project should use `frontend/` as its root directory, install dependencies with `npm install`, and build with `npm run build`.

Set `VITE_API_BASE_URL` in the Vercel project environment before deploying when the backend is hosted separately. Because Vite reads environment variables at build time, a new deployment is required after changing this value. The backend must also allow the Vercel origin through `CORS_ORIGINS`.

## Styling and UI conventions

- Keep route-level orchestration in `pages/` and reusable visual behavior in `components/`.
- Keep network calls in `src/api.ts` rather than calling `fetch` directly from unrelated components.
- Reuse the shared layout, `Panel`, `Loader`, and page-introduction patterns before adding a new visual pattern.
- Preserve responsive behavior: several data tables intentionally switch to compact card layouts on small screens.
- Keep user-facing loading, empty, and error states explicit; API failure should not look like an empty dataset.
- Keep backend field names and frontend type names aligned unless a deliberate mapping is documented.

## Troubleshooting

### The app stays on the boot screen

Open the browser developer tools and check the request to `/health`. Verify that:

1. The backend is running.
2. `VITE_API_BASE_URL` points to the correct origin or proxy path.
3. The backend route is reachable from the browser.
4. CORS allows the frontend origin when the API is hosted separately.

Restart Vite after changing `.env` values.

### Refreshing a nested route returns a 404

The host must rewrite frontend routes to `index.html`. Vercel is configured for this in `vercel.json`; configure the equivalent fallback on other hosts.

### `npm run lint` reports errors in `dev-dist`

The generated service-worker bundle is currently included by the broad ESLint glob. The current installed ESLint/TypeScript ESLint combination also reports unavailable rule definitions from that generated file. This is a tooling/configuration issue in generated output, not a runtime API failure. Do not edit the generated Workbox file; fix the lint scope or dependency/configuration mismatch in a separate maintenance change.

### The production build warns about a large JavaScript chunk

The build currently succeeds but Vite reports a minified chunk over 500 kB. If load performance becomes a priority, introduce route-level `import()` code splitting and measure the result before changing the warning threshold.

## Contribution checklist

Before opening a change that affects the frontend:

1. Confirm the user flow and route affected.
2. Update API types and request functions when a backend contract changes.
3. Handle loading, empty, error, and success states.
4. Check the affected route at desktop and mobile widths.
5. Run `npm run typecheck` and `npm run build`.
6. Run `npm run lint` and mention the known generated-output issue if it remains present.
7. Run `npm run format:check` and format only the files involved in the change.
8. Update this README when routes, scripts, configuration, persistence, or deployment behavior changes.

## Project status

The frontend is an active, API-backed dashboard with the core exploration, analytics, recommendation, and application-tracking workflows implemented. It is not a standalone data source: the quality and freshness of the displayed results depend on the backend API and its ingestion pipeline. Generated build output is present in the working tree, but source changes should be made under `src/`, `public/`, or the frontend configuration files.
