# Frontend Documentation

## Purpose

The frontend provides the user-facing interface for the Tech Job Analytics application. It is responsible for rendering job and salary analytics to end users in a browser-based experience.

## Stack

- React
- Vite
- JavaScript
- CSS

## Current state

The frontend is still under active development. The repository already contains a standard Vite React app scaffold, but the full application features and backend integration are still being finalized.

## Local development

Use the project configuration in [package.json](package.json) to install dependencies and start the app locally.

Typical workflow:

```bash
cd frontend
npm install
npm run dev
```

The app will typically run on the Vite default port, usually http://localhost:5173.

## Current responsibilities

At the moment, the frontend is expected to:

- display job listings
- render analytics or summary views
- connect to backend data sources
- present user-friendly interfaces for exploring job market information

## Integration expectations

As the backend becomes more complete, the frontend should document:

- API endpoints consumed by the app
- expected payload structures
- loading and error states
- user flows and dashboard interactions

## Project structure

The frontend contains the standard React app structure:

- entry point files
- assets and styling
- app-level UI and components
- Vite configuration and scripts

## Development guidance

- keep UI components modular and focused
- separate business/transport logic from presentation
- document user-facing flows as the app expands
- match backend response contracts once they are stable

## Planned work

The frontend should eventually include:

- dashboard pages
- filtering and search behavior
- job card or detail views
- charts or summary statistics
- connection to live backend data

## Current status

The frontend is scaffolded and ready for implementation, but the actual end-user product and integration patterns are still evolving.
