# Project structure

```text
backend/
  app/
    api/v1/          Versioned API routers
    core/            Configuration and authentication helpers
    jobs/            Expiry alert and scheduled jobs
    models/          SQLAlchemy domain models
    repositories/    Database query abstractions
    schemas/         Pydantic request/response contracts
    services/        Business rules and calculations
    utils/           Framework-independent utilities
    main.py           Working application entry point
  tests/              Backend tests

frontend/
  public/             PWA/static assets
  src/
    components/       Reusable forms, tables, charts and UI
    context/          Application-wide React context
    hooks/            Reusable hooks
    layouts/          Page shells and navigation
    pages/            Feature-oriented page packages
    routes/           Route metadata
    services/         HTTP API client
    utils/            Formatting and shared helpers
    main.jsx           Working application entry point
```

The first stable MVP remains executable through `backend/app/main.py` and
`frontend/src/main.jsx`. The added packages establish clear boundaries for
incrementally extracting each feature without breaking the current application.
