-- optimization.sql
-- Performance tuning examples

-- 1. Index creation for faster lookups
CREATE INDEX idx_sales_date ON sales_cleaned(transaction_date);
CREATE INDEX idx_sales_store ON sales_cleaned(store_location(50));
CREATE INDEX idx_sales_product ON sales_cleaned(product_id);

-- 2. Avoid correlated subquery (bad pattern shown, then fixed)

-- ❌ Bad:
-- SELECT s.store_location,
--        (SELECT SUM(transaction_qty*unit_price)
--         FROM sales_cleaned WHERE store_location = s.store_location) AS revenue
-- FROM sales_cleaned s;

-- ✅ Optimized:
SELECT store_location, SUM(transaction_qty * unit_price) AS revenue
FROM sales_cleaned
GROUP BY store_location;

-- 3. Use EXPLAIN to check query plan
EXPLAIN
SELECT product_type, SUM(transaction_qty * unit_price) AS Revenue
FROM sales_cleaned
GROUP BY product_type
ORDER BY Revenue DESC;