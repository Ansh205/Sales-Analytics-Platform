# Database Design

## Overview

The Sales Analytics Platform uses PostgreSQL as its relational database.

The ETL pipeline processes the Global Superstore dataset and stores the cleaned data in PostgreSQL for reporting and analytics.

The database is designed to support Power BI dashboards, SQL analytics, and FastAPI services.

---

# Database Architecture

```
Global Superstore Dataset
            │
            ▼
Python ETL Pipeline
            │
            ▼
Clean CSV Files
            │
            ▼
PostgreSQL Database
      │
      ├── orders
      ├── returns
      └── people
            │
            ▼
SQL Views
            │
            ▼
Power BI Dashboard
            │
            ▼
FastAPI Backend
```

---

# Tables

## Orders

Stores all sales transactions.

Contains:

- Customer Information
- Product Information
- Sales
- Profit
- Quantity
- Discount
- Shipping Details
- Date Features

Rows

```
10194
```

---

## Returns

Stores returned orders.

Rows

```
800
```

---

## People

Stores Regional Managers.

Rows

```
4
```

---

# SQL Views

The following reporting views are available:

- vw_executive_summary
- vw_sales_summary
- vw_customer_summary
- vw_product_summary
- vw_region_summary
- vw_profit_summary
- vw_monthly_sales
- vw_shipping_summary

Power BI connects to these views instead of raw tables.

---

# Indexes

Indexes were created on:

- order_date
- customer_id
- product_id
- region
- category
- sub_category
- order_year
- ship_mode
- segment
- state_province
- city

These improve SQL query performance.

---

# ETL Flow

```
Excel

↓

Python ETL

↓

Data Cleaning

↓

Feature Engineering

↓

CSV Export

↓

PostgreSQL Import

↓

SQL Views

↓

Power BI
```

---

# Technologies

- Python
- Pandas
- PostgreSQL
- SQLAlchemy
- SQL
- Power BI