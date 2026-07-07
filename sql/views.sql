DROP VIEW IF EXISTS vw_executive_summary;

CREATE VIEW vw_executive_summary AS

SELECT

COUNT(DISTINCT order_id)      AS total_orders,

COUNT(DISTINCT customer_id)   AS total_customers,

COUNT(DISTINCT product_id)    AS total_products,

ROUND(SUM(sales),2)           AS total_sales,

ROUND(SUM(profit),2)          AS total_profit,

ROUND(AVG(profit_margin),2)   AS avg_profit_margin,

ROUND(AVG(discount),2)        AS avg_discount,

ROUND(AVG(shipping_days),2)   AS avg_shipping_days

FROM orders;

DROP VIEW IF EXISTS vw_sales_summary;

CREATE VIEW vw_sales_summary AS

SELECT

order_year,

order_month,

region,

category,

sub_category,

ROUND(SUM(sales),2) AS total_sales,

ROUND(SUM(profit),2) AS total_profit,

SUM(quantity) AS total_quantity,

COUNT(DISTINCT order_id) AS total_orders

FROM orders

GROUP BY

order_year,

order_month,

region,

category,

sub_category;


DROP VIEW IF EXISTS vw_customer_summary;

CREATE VIEW vw_customer_summary AS

SELECT

customer_id,

customer_name,

segment,

COUNT(DISTINCT order_id) AS total_orders,

ROUND(SUM(sales),2) AS total_sales,

ROUND(SUM(profit),2) AS total_profit,

ROUND(AVG(sales),2) AS average_order_value

FROM orders

GROUP BY

customer_id,

customer_name,

segment;



DROP VIEW IF EXISTS vw_product_summary;

CREATE VIEW vw_product_summary AS

SELECT

product_id,

product_name,

category,

sub_category,

ROUND(SUM(sales),2) AS total_sales,

ROUND(SUM(profit),2) AS total_profit,

SUM(quantity) AS total_quantity

FROM orders

GROUP BY

product_id,

product_name,

category,

sub_category;



DROP VIEW IF EXISTS vw_region_summary;

CREATE VIEW vw_region_summary AS

SELECT

region,

country_region,

state_province,

COUNT(DISTINCT order_id) AS total_orders,

COUNT(DISTINCT customer_id) AS customers,

ROUND(SUM(sales),2) AS total_sales,

ROUND(SUM(profit),2) AS total_profit

FROM orders

GROUP BY

region,

country_region,

state_province;



DROP VIEW IF EXISTS vw_profit_summary;

CREATE VIEW vw_profit_summary AS

SELECT

category,

sub_category,

ROUND(SUM(sales),2) AS total_sales,

ROUND(SUM(profit),2) AS total_profit,

ROUND(AVG(profit_margin),2) AS avg_profit_margin

FROM orders

GROUP BY

category,

sub_category;




DROP VIEW IF EXISTS vw_monthly_sales;

CREATE VIEW vw_monthly_sales AS

SELECT

order_year,

order_month,

ROUND(SUM(sales),2) AS total_sales,

ROUND(SUM(profit),2) AS total_profit,

SUM(quantity) AS total_quantity

FROM orders

GROUP BY

order_year,

order_month

ORDER BY

order_year;



DROP VIEW IF EXISTS vw_shipping_summary;

CREATE VIEW vw_shipping_summary AS

SELECT

ship_mode,

ROUND(AVG(shipping_days),2) AS avg_shipping_days,

COUNT(DISTINCT order_id) AS total_orders

FROM orders

GROUP BY

ship_mode;