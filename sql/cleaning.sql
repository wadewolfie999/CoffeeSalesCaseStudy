-- cleaning.sql
-- Create a cleaned view from raw sales table

CREATE OR REPLACE VIEW sales_cleaned AS
SELECT
    transaction_id,
    transaction_date,
    transaction_time,
    COALESCE(transaction_qty, 0) AS transaction_qty,
    store_id,
    TRIM(COALESCE(store_location, 'Unknown')) AS store_location,
    product_id,
    UPPER(TRIM(COALESCE(product_category, 'Unknown'))) AS product_category,
    UPPER(TRIM(COALESCE(product_type, 'Unknown'))) AS product_type,
    TRIM(COALESCE(product_detail, 'Unknown')) AS product_detail
FROM sales;
