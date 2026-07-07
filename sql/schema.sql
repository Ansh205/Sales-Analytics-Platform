-- ============================================
-- Sales Analytics Platform Database Schema
-- ============================================

-- Drop tables if they already exist
DROP TABLE IF EXISTS orders CASCADE;
DROP TABLE IF EXISTS returns CASCADE;
DROP TABLE IF EXISTS people CASCADE;

-- ============================================
-- Orders Table
-- ============================================

CREATE TABLE orders (

    row_id              INTEGER PRIMARY KEY,

    order_id            VARCHAR(25) NOT NULL,

    order_date          DATE NOT NULL,

    ship_date           DATE NOT NULL,

    ship_mode           VARCHAR(50) NOT NULL,

    customer_id         VARCHAR(25) NOT NULL,

    customer_name       VARCHAR(120) NOT NULL,

    segment             VARCHAR(40) NOT NULL,

    country_region      VARCHAR(80) NOT NULL,

    city                VARCHAR(80) NOT NULL,

    state_province      VARCHAR(80) NOT NULL,

    postal_code         VARCHAR(20),

    region              VARCHAR(40) NOT NULL,

    product_id          VARCHAR(30) NOT NULL,

    category            VARCHAR(40) NOT NULL,

    sub_category        VARCHAR(50) NOT NULL,

    product_name        TEXT NOT NULL,

    sales               NUMERIC(12,2) NOT NULL,

    quantity            INTEGER NOT NULL,

    discount            NUMERIC(5,2) NOT NULL,

    profit              NUMERIC(12,2) NOT NULL,

    order_year          INTEGER,

    order_month         VARCHAR(20),

    order_quarter       INTEGER,

    order_week          INTEGER,

    order_day           VARCHAR(20),

    shipping_days       INTEGER,

    profit_margin       NUMERIC(10,4),

    sales_bucket        VARCHAR(30),

    profit_bucket       VARCHAR(30)

);

-- ============================================
-- Returns Table
-- ============================================

CREATE TABLE returns (

    return_id SERIAL PRIMARY KEY,

    returned VARCHAR(10) NOT NULL,

    order_id VARCHAR(25) NOT NULL

);

-- ============================================
-- People Table
-- ============================================

CREATE TABLE people (

    region              VARCHAR(40) PRIMARY KEY,

    regional_manager    VARCHAR(120) NOT NULL

);