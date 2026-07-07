-- ============================================
-- SALES ANALYTICS
-- ============================================

-- Q1 Total Sales
SELECT
ROUND(SUM(sales),2) AS total_sales
FROM orders;


-- Q2 Total Profit
SELECT
ROUND(SUM(profit),2) AS total_profit
FROM orders;


-- Q3 Total Orders
SELECT
COUNT(DISTINCT order_id) AS total_orders
FROM orders;


-- Q4 Average Order Value
SELECT
ROUND(SUM(sales)/COUNT(DISTINCT order_id),2) AS average_order_value
FROM orders;


-- Q5 Monthly Sales
SELECT

order_year,

order_month,

ROUND(SUM(sales),2) AS total_sales

FROM orders

GROUP BY

order_year,

order_month

ORDER BY

order_year,
order_month;










-- ============================================
-- CUSTOMER ANALYTICS
-- ============================================

-- Q6 Top 10 Customers

SELECT

customer_name,

ROUND(SUM(sales),2) AS sales

FROM orders

GROUP BY customer_name

ORDER BY sales DESC

LIMIT 10;


-- Q7 Bottom 10 Customers

SELECT

customer_name,

ROUND(SUM(sales),2) AS sales

FROM orders

GROUP BY customer_name

ORDER BY sales

LIMIT 10;


-- Q8 Customer Segment Performance

SELECT

segment,

ROUND(SUM(sales),2) AS sales,

ROUND(SUM(profit),2) AS profit

FROM orders

GROUP BY segment;







-- ============================================
-- PRODUCT ANALYTICS
-- ============================================

-- Q9 Top Products

SELECT

product_name,

ROUND(SUM(sales),2) AS sales

FROM orders

GROUP BY product_name

ORDER BY sales DESC

LIMIT 10;


-- Q10 Category Performance

SELECT

category,

ROUND(SUM(sales),2) AS sales,

ROUND(SUM(profit),2) AS profit

FROM orders

GROUP BY category;


-- Q11 Subcategory Performance

SELECT

sub_category,

ROUND(SUM(sales),2) AS sales,

ROUND(SUM(profit),2) AS profit

FROM orders

GROUP BY sub_category;









-- ============================================
-- REGIONAL ANALYTICS
-- ============================================

-- Q12 Sales by Region

SELECT

region,

ROUND(SUM(sales),2) AS sales

FROM orders

GROUP BY region;


-- Q13 Sales by State

SELECT

state_province,

ROUND(SUM(sales),2) AS sales

FROM orders

GROUP BY state_province

ORDER BY sales DESC;


-- Q14 Sales by City

SELECT

city,

ROUND(SUM(sales),2) AS sales

FROM orders

GROUP BY city

ORDER BY sales DESC

LIMIT 20;








-- ============================================
-- PROFIT ANALYTICS
-- ============================================

-- Q15 Highest Profit Products

SELECT

product_name,

ROUND(SUM(profit),2) AS profit

FROM orders

GROUP BY product_name

ORDER BY profit DESC

LIMIT 10;


-- Q16 Loss Making Products

SELECT

product_name,

ROUND(SUM(profit),2) AS profit

FROM orders

GROUP BY product_name

HAVING SUM(profit) < 0

ORDER BY profit;








-- ============================================
-- SHIPPING ANALYTICS
-- ============================================

-- Q17 Average Shipping Days

SELECT

ROUND(AVG(shipping_days),2)

FROM orders;


-- Q18 Ship Mode Performance

SELECT

ship_mode,

ROUND(AVG(shipping_days),2) AS avg_days,

COUNT(*) AS orders

FROM orders

GROUP BY ship_mode;





-- ============================================
-- RETURNS ANALYSIS
-- ============================================

-- Q19 Returned Orders

SELECT

COUNT(*) AS returned_orders

FROM returns;


-- Q20 Return Rate

SELECT

ROUND(

COUNT(DISTINCT r.order_id)*100.0/

COUNT(DISTINCT o.order_id),

2

) AS return_rate

FROM orders o

LEFT JOIN returns r

ON o.order_id=r.order_id;












-- ============================================
-- WINDOW FUNCTIONS
-- ============================================

-- Q21 Top Customers Rank

SELECT

customer_name,

SUM(sales) AS sales,

RANK() OVER(

ORDER BY SUM(sales) DESC

) AS customer_rank

FROM orders

GROUP BY customer_name;


-- Q22 Dense Rank

SELECT

product_name,

SUM(profit) AS profit,

DENSE_RANK() OVER(

ORDER BY SUM(profit) DESC

)

FROM orders

GROUP BY product_name;


-- Q23 Row Number

SELECT

order_id,

sales,

ROW_NUMBER() OVER(

ORDER BY sales DESC

)

FROM orders;






-- ============================================
-- CTE
-- ============================================

WITH customer_sales AS (

SELECT

customer_name,

SUM(sales) AS total_sales

FROM orders

GROUP BY customer_name

)

SELECT *

FROM customer_sales

WHERE total_sales>10000;






-- ============================================
-- RUNNING TOTAL
-- ============================================

SELECT

order_date,

SUM(sales) AS sales,

SUM(

SUM(sales)

) OVER(

ORDER BY order_date

)

AS running_sales

FROM orders

GROUP BY order_date

ORDER BY order_date;






-- ============================================
-- LAG
-- ============================================

SELECT

order_date,

SUM(sales) AS sales,

LAG(

SUM(sales)

)

OVER(

ORDER BY order_date

)

AS previous_sales

FROM orders

GROUP BY order_date;





-- ============================================
-- LEAD
-- ============================================

SELECT

order_date,

SUM(sales) AS sales,

LEAD(

SUM(sales)

)

OVER(

ORDER BY order_date

)

AS next_sales

FROM orders

GROUP BY order_date;








-- ============================================
-- YOY GROWTH
-- ============================================

WITH yearly_sales AS (

SELECT

order_year,

SUM(sales) AS total_sales

FROM orders

GROUP BY order_year

)

SELECT

order_year,

total_sales,

LAG(total_sales)

OVER(

ORDER BY order_year

)

AS previous_year_sales,

ROUND(

(

total_sales-

LAG(total_sales)

OVER(

ORDER BY order_year

)

)

/

LAG(total_sales)

OVER(

ORDER BY order_year

)

*100,

2

) AS growth_percent

FROM yearly_sales;