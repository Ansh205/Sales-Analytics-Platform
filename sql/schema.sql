CREATE TABLE orders (

    row_id INTEGER,

    order_id VARCHAR(30),

    order_date DATE,

    ship_date DATE,

    ship_mode VARCHAR(50),

    customer_id VARCHAR(30),

    customer_name VARCHAR(150),

    segment VARCHAR(50),

    country_region VARCHAR(100),

    city VARCHAR(100),

    state_province VARCHAR(100),

    postal_code VARCHAR(20),

    region VARCHAR(50),

    product_id VARCHAR(50),

    category VARCHAR(50),

    sub_category VARCHAR(50),

    product_name TEXT,

    sales NUMERIC,

    quantity INTEGER,

    discount NUMERIC,

    profit NUMERIC,

    order_year INTEGER,

    order_month VARCHAR(20),

    order_quarter INTEGER,

    order_week INTEGER,

    order_day VARCHAR(20),

    shipping_days INTEGER,

    profit_margin NUMERIC,

    sales_bucket VARCHAR(30),

    profit_bucket VARCHAR(30)

);

CREATE TABLE returns (

    returned VARCHAR(20),

    order_id VARCHAR(30)

);


CREATE TABLE people (

    region VARCHAR(100),

    person VARCHAR(100)

);