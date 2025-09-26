-- Run this against 'coffeesalesdb' database

-- Total row count
SELECT COUNT(*) AS total_rows FROM sales;

-- Check NULLs per COLUMNS
SELECT
	SUM(transaction_id IS NULL) AS null_transaction_id,
	SUM(transaction_date IS NULL) AS null_transaction_date,
	SUM(transaction_time IS NULL) AS null_transaction_time,
	SUM(transaction_qty IS NULL) AS null_transaction_qty,
	SUM(store_id IS NULL) AS null_store_id,
	SUM(store_location IS NULL) AS null_store_location,
	SUM(product_id IS NULL) AS null_product_id,
	SUM(unit_price IS NULL) AS null_unit_price,
	SUM(product_category IS NULL) AS null_product_category,
	SUM(product_type IS NULL) AS null_product_type,
	SUM(product_detail IS NULL) AS null_product_detail
FROM sales;


-- Detect duplicate values

SELECT transaction_id, COUNT(*)
FROM sales
GROUP BY transaction_id
HAVING COUNT(*)>1;


-- Outlier check: negative or zero quantities or prices

SELECT * FROM sales WHERE transaction_qty <= 0 OR unit_price <= 0;

-- Check Min/Max date 

SELECT MIN(transaction_date), MAX(transaction_date) FROM sales;
