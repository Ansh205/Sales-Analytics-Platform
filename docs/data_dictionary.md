# Data Dictionary

## Orders Table

| Column | Data Type | Description |
|---------|-----------|-------------|
| row_id | INTEGER | Unique row identifier |
| order_id | VARCHAR | Order ID |
| order_date | DATE | Date of order |
| ship_date | DATE | Shipping date |
| ship_mode | VARCHAR | Shipping method |
| customer_id | VARCHAR | Customer ID |
| customer_name | VARCHAR | Customer name |
| segment | VARCHAR | Customer segment |
| country_region | VARCHAR | Country |
| city | VARCHAR | City |
| state_province | VARCHAR | State |
| postal_code | VARCHAR | Postal code |
| region | VARCHAR | Sales region |
| product_id | VARCHAR | Product ID |
| category | VARCHAR | Product category |
| sub_category | VARCHAR | Product subcategory |
| product_name | TEXT | Product name |
| sales | NUMERIC | Sales amount |
| quantity | INTEGER | Quantity sold |
| discount | NUMERIC | Discount applied |
| profit | NUMERIC | Profit amount |
| order_year | INTEGER | Order year |
| order_month | VARCHAR | Month name |
| order_quarter | INTEGER | Quarter |
| order_week | INTEGER | Week number |
| order_day | VARCHAR | Day name |
| shipping_days | INTEGER | Shipping duration |
| profit_margin | NUMERIC | Profit margin |
| sales_bucket | VARCHAR | Sales category |
| profit_bucket | VARCHAR | Profit category |

---

## Returns Table

| Column | Data Type | Description |
|---------|-----------|-------------|
| return_id | SERIAL | Primary key |
| order_id | VARCHAR | Returned order |
| returned | VARCHAR | Return status |

---

## People Table

| Column | Data Type | Description |
|---------|-----------|-------------|
| region | VARCHAR | Sales region |
| regional_manager | VARCHAR | Regional manager |