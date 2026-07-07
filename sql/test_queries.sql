-- ============================================================
-- Sales Analytics Platform
-- Database Validation Queries
-- ============================================================

---------------------------------------------------------------
-- SECTION 1 : TABLE VALIDATION
---------------------------------------------------------------

-- Q1 List all tables

SELECT table_name
FROM information_schema.tables
WHERE table_schema='public'
ORDER BY table_name;


---------------------------------------------------------------
-- Q2 Orders Row Count

SELECT COUNT(*) AS total_orders
FROM orders;


---------------------------------------------------------------
-- Q3 Returns Row Count

SELECT COUNT(*) AS total_returns
FROM returns;


---------------------------------------------------------------
-- Q4 People Row Count

SELECT COUNT(*) AS total_people
FROM people;


---------------------------------------------------------------
-- SECTION 2 : SAMPLE DATA
---------------------------------------------------------------

-- Q5 First 10 Orders

SELECT *
FROM orders
LIMIT 10;


---------------------------------------------------------------

-- Q6 First 10 Returns

SELECT *
FROM returns
LIMIT 10;


---------------------------------------------------------------

-- Q7 People Table

SELECT *
FROM people;


---------------------------------------------------------------
-- SECTION 3 : NULL CHECKS
---------------------------------------------------------------

-- Q8 NULL Customer IDs

SELECT COUNT(*) AS null_customer_ids

FROM orders

WHERE customer_id IS NULL;


---------------------------------------------------------------

-- Q9 NULL Product IDs

SELECT COUNT(*) AS null_product_ids

FROM orders

WHERE product_id IS NULL;


---------------------------------------------------------------

-- Q10 NULL Sales

SELECT COUNT(*) AS null_sales

FROM orders

WHERE sales IS NULL;


---------------------------------------------------------------

-- Q11 NULL Profit

SELECT COUNT(*) AS null_profit

FROM orders

WHERE profit IS NULL;


---------------------------------------------------------------

-- Q12 NULL Region

SELECT COUNT(*) AS null_region

FROM orders

WHERE region IS NULL;


---------------------------------------------------------------
-- SECTION 4 : DUPLICATE CHECKS
---------------------------------------------------------------

-- Q13 Duplicate Row IDs

SELECT

row_id,

COUNT(*)

FROM orders

GROUP BY row_id

HAVING COUNT(*)>1;


---------------------------------------------------------------

-- Q14 Duplicate Order IDs

SELECT

order_id,

COUNT(*)

FROM orders

GROUP BY order_id

HAVING COUNT(*)>1

ORDER BY COUNT(*) DESC;


---------------------------------------------------------------
-- SECTION 5 : DATA QUALITY
---------------------------------------------------------------

-- Q15 Negative Sales

SELECT COUNT(*) AS negative_sales

FROM orders

WHERE sales<0;


---------------------------------------------------------------

-- Q16 Negative Quantity

SELECT COUNT(*) AS negative_quantity

FROM orders

WHERE quantity<0;


---------------------------------------------------------------

-- Q17 Invalid Discount

SELECT COUNT(*) AS invalid_discount

FROM orders

WHERE discount<0
OR discount>1;


---------------------------------------------------------------

-- Q18 Shipping Days

SELECT

MIN(shipping_days) AS minimum,

MAX(shipping_days) AS maximum,

AVG(shipping_days) AS average

FROM orders;


---------------------------------------------------------------
-- SECTION 6 : RETURNS VALIDATION
---------------------------------------------------------------

-- Q19 Returned Orders

SELECT COUNT(*)

FROM returns;


---------------------------------------------------------------

-- Q20 Returned Orders Existing in Orders

SELECT COUNT(*)

FROM returns r

JOIN orders o

ON r.order_id=o.order_id;


---------------------------------------------------------------
-- SECTION 7 : PEOPLE VALIDATION
---------------------------------------------------------------

-- Q21 Regions in Orders

SELECT DISTINCT region

FROM orders

ORDER BY region;


---------------------------------------------------------------

-- Q22 Regions in People

SELECT DISTINCT region

FROM people

ORDER BY region;


---------------------------------------------------------------

-- Q23 Orders Without Regional Manager

SELECT

o.region

FROM orders o

LEFT JOIN people p

ON o.region=p.region

WHERE p.region IS NULL

GROUP BY o.region;


---------------------------------------------------------------
-- SECTION 8 : VIEW VALIDATION
---------------------------------------------------------------

-- Q24 Executive View

SELECT *

FROM vw_executive_summary;


---------------------------------------------------------------

-- Q25 Sales View

SELECT *

FROM vw_sales_summary

LIMIT 10;


---------------------------------------------------------------

-- Q26 Customer View

SELECT *

FROM vw_customer_summary

LIMIT 10;


---------------------------------------------------------------

-- Q27 Product View

SELECT *

FROM vw_product_summary

LIMIT 10;


---------------------------------------------------------------

-- Q28 Region View

SELECT *

FROM vw_region_summary

LIMIT 10;


---------------------------------------------------------------

-- Q29 Profit View

SELECT *

FROM vw_profit_summary

LIMIT 10;


---------------------------------------------------------------

-- Q30 Monthly Sales View

SELECT *

FROM vw_monthly_sales

LIMIT 10;


---------------------------------------------------------------

-- Q31 Shipping View

SELECT *

FROM vw_shipping_summary;


---------------------------------------------------------------
-- SECTION 9 : INDEX VALIDATION
---------------------------------------------------------------

-- Q32 List All Indexes

SELECT

tablename,

indexname

FROM pg_indexes

WHERE schemaname='public'

ORDER BY tablename;


---------------------------------------------------------------
-- SECTION 10 : PERFORMANCE TEST
---------------------------------------------------------------

-- Q33 Customer Search

EXPLAIN ANALYZE

SELECT *

FROM orders

WHERE customer_id='CG-12520';


---------------------------------------------------------------

-- Q34 Product Search

EXPLAIN ANALYZE

SELECT *

FROM orders

WHERE product_id='OFF-LA-10000240';


---------------------------------------------------------------

-- Q35 Regional Sales

EXPLAIN ANALYZE

SELECT

region,

SUM(sales)

FROM orders

GROUP BY region;


---------------------------------------------------------------
-- END OF FILE
---------------------------------------------------------------