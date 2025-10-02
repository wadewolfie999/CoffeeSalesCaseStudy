-- analysis.sql
-- Business analysis + feature engineering queries
/*
 analysis.sql
 Coffee Sales Case Study – Business Analysis & Feature Engineering
 
 Modules:
 1. Revenue per store
 2. Top 5 products by revenue
 3. Daily sales trend
 4. Best-selling product per store
 5. Sales by day of week
 6. Inactive products (churn-like metric)
 7. Products frequently bought together
 8. High-value products (top 10% by revenue)
 9. Monthly revenue + MoM growth
 */
-- 1. Revenue per store
SELECT store_location,
    ROUND(SUM(transaction_qty * unit_price)) AS total_revenue
FROM sales_cleaned
GROUP BY store_location
ORDER BY total_revenue DESC;

-- 2. Top 5 products by revenue
SELECT product_detail,
    ROUND(SUM(transaction_qty * unit_price)) AS product_revenue
FROM sales_cleaned
GROUP BY product_detail
ORDER BY product_revenue DESC
LIMIT 5;

-- 3. Daily sales trend
SELECT transaction_date,
    ROUND(SUM(transaction_qty * unit_price)) AS daily_revenue
FROM sales_cleaned
GROUP BY transaction_date
ORDER BY transaction_date;

-- 4. Best-selling product per store
WITH ranked_products AS (
    SELECT store_location,
        product_type,
        ROUND(SUM(transaction_qty), 2) AS total_qty_sold,
        RANK() OVER (
            PARTITION BY store_location
            ORDER BY ROUND(SUM(transaction_qty), 2) DESC
        ) AS rnk
    FROM sales_cleaned
    GROUP BY store_location,
        product_type
)
SELECT store_location,
    product_type,
    total_qty_sold
FROM ranked_products
WHERE rnk = 1;

-- 5. Time-based feature engineering: sales by day of week
SELECT DAYNAME(transaction_date) AS day_of_week,
    ROUND(SUM(transaction_qty * unit_price), 2) AS revenue
FROM sales_cleaned
GROUP BY day_of_week
ORDER BY revenue DESC;

-- 6. "Churn-like" metric: inactive products (not sold in the last 90 days)
WITH product_activity AS (
    SELECT product_id,
        product_detail,
        MAX(transaction_date) AS last_sold_date
    FROM sales_cleaned
    GROUP BY product_id,
        product_detail
),
inactive_products AS (
    SELECT product_id,
        product_detail,
        last_sold_date,
        DATEDIFF(CURDATE(), last_sold_date) AS days_since_sold
    FROM product_activity
    WHERE last_sold_date < CURDATE() - INTERVAL 90 DAY
        OR last_sold_date IS NULL
)
SELECT *
FROM inactive_products
ORDER BY days_since_sold DESC;

-- 7. Recommender-style: products frequently bought together
SELECT a.product_detail AS product_a,
    b.product_detail AS product_b,
    COUNT(*) AS times_bought_together
FROM sales_cleaned a
    JOIN sales_cleaned b ON a.transaction_id = b.transaction_id
    AND a.product_id < b.product_id
GROUP BY a.product_detail,
    b.product_detail
ORDER BY times_bought_together DESC
LIMIT 10;

-- 8. Customer segmentation: high-value products (top 10% by revenue)
WITH product_revenue AS (
    SELECT product_detail,
        SUM(transaction_qty * unit_price) AS total_revenue
    FROM sales_cleaned
    GROUP BY product_detail
),
ranked_products AS (
    SELECT product_detail,
        total_revenue,
        NTILE(10) OVER (
            ORDER BY total_revenue DESC
        ) AS revenue_decile
    FROM product_revenue
)
SELECT product_detail,
    total_revenue
FROM ranked_products
WHERE revenue_decile = 1
ORDER BY total_revenue DESC;

-- 9. Monthly revenue + month-over-month growth (professional style)
WITH monthly_revenue AS (
    SELECT DATE_FORMAT(transaction_date, '%b %Y') AS month_label,
        STR_TO_DATE(
            CONCAT(DATE_FORMAT(transaction_date, '%Y-%m'), '-01'),
            '%Y-%m-%d'
        ) AS month_start,
        ROUND(SUM(transaction_qty * unit_price), 2) AS total_revenue_raw
    FROM sales_cleaned
    GROUP BY month_label,
        month_start
)
SELECT month_label,
    month_start,
    ROUND(total_revenue_raw, 2) AS total_revenue,
    ROUND(previous_month_revenue_raw, 2) previous_month_revenue,
    ROUND(
        (total_revenue_raw - previous_month_revenue_raw) / NULLIF(previous_month_revenue_raw, 0) * 100,
        2
    ) AS growth_rate_percentage
FROM (
        SELECT mr.*,
            LAG(total_revenue_raw) OVER (
                ORDER BY month_start
            ) AS previous_month_revenue_raw
        FROM monthly_revenue mr
    ) t
ORDER BY month_start;