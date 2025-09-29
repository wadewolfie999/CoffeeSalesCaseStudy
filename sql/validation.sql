-- validation.sql
-- QA checks for data quality

-- 1. Duplicate transactions
SELECT transaction_id, COUNT(*) AS dup_count
FROM sales_cleaned
GROUP BY transaction_id
HAVING COUNT(*) > 1;

-- 2. Missing critical fields
SELECT * FROM sales_cleaned
WHERE transaction_id IS NULL
   OR transaction_date IS NULL
   OR store_id IS NULL
   OR product_id IS NULL;

-- 3. Outlier detection: negative or zero quantities or prices
SELECT * FROM sales_cleaned
WHERE transaction_qty <= 0 OR unit_price <= 0;

-- 4. Date range check
SELECT MIN(transaction_date) AS min_date, MAX(transaction_date) AS max_date
FROM sales_cleaned;
-- Ensuring dates fall within expected range
