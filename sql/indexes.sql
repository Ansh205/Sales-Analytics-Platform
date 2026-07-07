-- ============================================
-- Sales Analytics Platform
-- Database Indexes
-- ============================================

-- ============================================
-- Orders Table Indexes
-- ============================================

-- Order Date
CREATE INDEX IF NOT EXISTS idx_orders_order_date
ON orders(order_date);

-- Customer
CREATE INDEX IF NOT EXISTS idx_orders_customer
ON orders(customer_id);

-- Product
CREATE INDEX IF NOT EXISTS idx_orders_product
ON orders(product_id);

-- Region
CREATE INDEX IF NOT EXISTS idx_orders_region
ON orders(region);

-- Category
CREATE INDEX IF NOT EXISTS idx_orders_category
ON orders(category);

-- Sub Category
CREATE INDEX IF NOT EXISTS idx_orders_sub_category
ON orders(sub_category);

-- Order Year
CREATE INDEX IF NOT EXISTS idx_orders_order_year
ON orders(order_year);

-- Ship Mode
CREATE INDEX IF NOT EXISTS idx_orders_ship_mode
ON orders(ship_mode);

-- Segment
CREATE INDEX IF NOT EXISTS idx_orders_segment
ON orders(segment);

-- State
CREATE INDEX IF NOT EXISTS idx_orders_state
ON orders(state_province);

-- City
CREATE INDEX IF NOT EXISTS idx_orders_city
ON orders(city);



-- ============================================
-- Returns Table Indexes
-- ============================================

CREATE INDEX IF NOT EXISTS idx_returns_order
ON returns(order_id);



-- ============================================
-- People Table Indexes
-- ============================================

CREATE INDEX IF NOT EXISTS idx_people_region
ON people(region);

CREATE INDEX IF NOT EXISTS idx_people_manager
ON people(regional_manager);