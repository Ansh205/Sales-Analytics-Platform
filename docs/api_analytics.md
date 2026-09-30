# Sales Analytics Platform — REST API Documentation (Phase 5 Final)

Comprehensive documentation for the Sales Analytics Platform REST API built with FastAPI, SQLAlchemy, and PostgreSQL.

---

## 1. Overview & Architecture

The API exposes PostgreSQL analytics views and tables through a high-performance, read-only REST API.

```
Global Superstore Dataset
       ↓
Python ETL Layer
       ↓
PostgreSQL Database (sales_analytics_db)
       ↓
SQL Analytics Views & Queries
       ↓
FastAPI Application (app/main.py & app/routes/analytics.py)
       ↓
REST API Endpoints (JSON)
```

- **Base URL (Local)**: `http://127.0.0.1:8000`
- **Interactive Documentation**: `http://127.0.0.1:8000/docs` (Swagger UI)
- **Alternative Documentation**: `http://127.0.0.1:8000/redoc` (ReDoc)
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

---

## 2. Environment & Configuration

Environment variables are loaded from `.env` via `python-dotenv`:

| Variable | Description | Example / Default |
|---|---|---|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/sales_analytics_db` |

A safe template is provided in `.env.example`.

---

## 3. Endpoints Reference

### Health Endpoints

#### Root Health Check
- **Endpoint**: `GET /`
- **Description**: Returns API service health status.
- **Response**:
```json
{
  "message": "Sales Analytics Platform API is running",
  "status": "healthy"
}
```

#### Database Health Check
- **Endpoint**: `GET /api/health/db`
- **Description**: Verifies active PostgreSQL connection by executing `SELECT 1`.
- **Response**:
```json
{
  "status": "healthy",
  "database": "connected"
}
```

---

### Core Analytics & Filter Endpoints

All analytics endpoints support optional query parameters for interactive dashboard filtering.

#### 1. Executive Summary (`GET /api/summary`)
- **Query Parameters**:
  - `year` (optional `int`): Filter by order year (e.g. `2023`).
  - `region` (optional `str`): Filter by region (`Central`, `East`, `North`, `South`).
  - `category` (optional `str`): Filter by product category (`Technology`, `Furniture`, `Office Supplies`).
  - `segment` (optional `str`): Filter by customer segment (`Consumer`, `Corporate`, `Home Office`).
- **Response**:
```json
{
  "total_sales": 2297200.86,
  "total_profit": 286397.02,
  "total_orders": 5009,
  "total_customers": 793,
  "profit_margin": 12.47,
  "return_rate": 5.43
}
```

#### 2. Sales Summary (`GET /api/sales/summary`)
- **Query Parameters**: `year`, `region`, `category`, `segment`
- **Response**:
```json
{
  "total_sales": 2297200.86,
  "total_profit": 286397.02,
  "total_orders": 5009,
  "total_quantity": 37873,
  "average_order_value": 458.61,
  "average_discount": 0.16,
  "profit_margin": 12.47
}
```

#### 3. Monthly Sales (`GET /api/sales/monthly`)
- **Query Parameters**: `year`, `region`, `category`, `segment`
- **Response**:
```json
[
  {
    "year": 2023,
    "month": 1,
    "sales": 43971.38,
    "profit": 5210.15
  },
  {
    "year": 2023,
    "month": 2,
    "sales": 38120.45,
    "profit": 4122.80
  }
]
```

#### 4. Regional Performance (`GET /api/sales/region`)
- **Query Parameters**: `year`, `category`, `segment`
- **Response**:
```json
[
  {
    "region": "Central",
    "sales": 501239.89,
    "profit": 39706.36,
    "orders": 2323
  }
]
```

#### 5. Top Products (`GET /api/products/top`)
- **Query Parameters**:
  - `year`, `region`, `category`, `segment`
  - `limit` (optional `int`, default `10`, min `1`, max `100`)
- **Response**:
```json
[
  {
    "product_name": "Apple Smart Phone, Full Size",
    "category": "Technology",
    "sub_category": "Phones",
    "sales": 86935.78,
    "profit": 30021.15
  }
]
```

#### 6. Top Customers (`GET /api/customers/top`)
- **Query Parameters**:
  - `year`, `region`, `category`, `segment`
  - `limit` (optional `int`, default `10`, min `1`, max `100`)
- **Response**:
```json
[
  {
    "customer_id": "SM-20320",
    "customer_name": "Sean Miller",
    "segment": "Consumer",
    "sales": 25043.07,
    "profit": -1980.75
  }
]
```

---

## 4. Query Validation & Error Handling

### Validation Rules (HTTP 422)
FastAPI validates request parameters. Invalid parameter types or out-of-range values return `HTTP 422 Unprocessable Entity`:
- `GET /api/products/top?limit=0` → `HTTP 422` (`ge=1`)
- `GET /api/products/top?limit=101` → `HTTP 422` (`le=100`)
- `GET /api/sales/monthly?year=abc` → `HTTP 422` (`integer required`)

### Database Error Masking (HTTP 500 / 503)
Internal database errors log details on the server side while masking credentials and stack traces from the client:
```json
{
  "detail": "Unable to retrieve analytics data"
}
```

---

## 5. Security & Read-Only Guarantee

- **Strict Read-Only Operations**: All queries execute `SELECT` statements only. No mutation or DDL queries are permitted.
- **SQL Injection Prevention**: All user-supplied query parameters are bound safely using SQLAlchemy bind variables (`:year`, `:region`, `:category`, `:segment`, `:limit`).
- **Secrets Protection**: Credentials and passwords are excluded from git and error outputs.

---

## 6. How to Run & Test

### Start API Server
```powershell
.\venv\Scripts\python -m uvicorn app.main:app --reload
```

### Run Test Suite
```powershell
.\venv\Scripts\python -m unittest discover -s tests
```
All 24 automated unit & integration tests pass.
