# PostgreSQL Database Connection Layer Architecture (Phase 5.2)

## Overview

The **Sales Analytics Platform API** connects to the existing PostgreSQL database (`sales_analytics_db`) using synchronous **SQLAlchemy 2.x** and the `psycopg2` driver.

The database connection layer is designed for high efficiency, thread safety, and secure credential handling.

---

## Architecture Flow

```
FastAPI Request
      │
      ▼
Depends(get_db)  ──►  SessionLocal()  ──►  SQLAlchemy Engine  ──►  PostgreSQL (sales_analytics_db)
      │                                                                  │
      ▼                                                                  ▼
Session Yielded                                                    Execute Query
      │                                                                  │
      ▼                                                                  │
Response Sent    ◄───────────────────────────────────────────────────────┘
      │
      ▼
db.close() (finally block)
```

---

## Environment Configuration

Database connection parameters are loaded dynamically from environment variables using `python-dotenv`. Credentials are **never** hardcoded into application source files.

### Environment Variable Format

```env
DATABASE_URL=postgresql+psycopg2://<DB_USER>:<DB_PASSWORD>@<DB_HOST>:<DB_PORT>/<DB_NAME>
```

### Files
- `.env`: Local development configuration containing active database credentials (**ignored by Git**).
- `.env.example`: Safe template file containing placeholder values only.

---

## Connection Pooling & Session Management

- **Engine Initialization**: Configured in `app/database.py` as a single application-wide engine instance.
- **`pool_pre_ping=True`**: Verifies database connection health prior to executing queries to automatically recover from stale or dropped connections.
- **`pool_size=5`**: Conservative connection pool size suitable for development and production workloads.
- **`max_overflow=10`**: Permits temporary connection expansion during high request concurrency.
- **Session Lifecycle (`get_db`)**: Each incoming request receives an isolated `SessionLocal` database session. The session is guaranteed to close in a `finally` block once the HTTP response is complete.

---

## Database Health Endpoint

### `GET /api/health/db`

- **Purpose**: Verifies that FastAPI can successfully connect to PostgreSQL and execute SQL queries against `sales_analytics_db`.
- **Query Executed**: `SELECT 1`

#### Success Response (`HTTP 200 OK`)
```json
{
    "status": "healthy",
    "database": "connected"
}
```

#### Failure Response (`HTTP 503 Service Unavailable`)
```json
{
    "detail": "Database connection error"
}
```
*Note: Passwords, connection strings, and internal stack traces are suppressed from API clients and logged server-side.*

---

## Security Guidelines

1. `.env` is listed in `.gitignore` and must **never** be committed to version control.
2. Production environments should supply `DATABASE_URL` via environment variables or secret managers.
