-- analysis.sql
-- Business analysis + feature engineering queries

-- 1. Revenue per store
SELECT store_location, SUM(transaction_qty * unit_price) AS total_revenue
FROM sales_cleaned
GROUP BY store_location
ORDER BY total_revenue DESC;

-- 2. Top 5 products by revenue
SELECT product_detail, SUM(transaction_qty * unit_price) AS product_revenue
FROM sales_cleaned
GROUP BY product_detail
ORDER BY product_revenue DESC
LIMIT 5;

-- 3. Daily sales trend
SELECT transaction_date,  SUM(transaction_qty * unit_price) AS daily_revenue
FROM sales_cleaned
GROUP BY transaction_date
ORDER BY transaction_date;

-- 4. Best-selling product per store
WITH ranked_products AS (
    SELECT store_location, product_type,
        SUM(transaction_qty) AS total_qty,
        RANK() OVER (PARTITION BY store_location ORDER BY SUM(transaction_qty) DESC) AS rnk
    FROM sales_cleaned
    GROUP BY store_location, product_type
)
SELECT store_location, product_type, total_qty
FROM ranked_products
WHERE rnk = 1;

-- 5. Time-based feature engineering: sales by day of week
SELECT 
    DAYNAME(transaction_date) AS day_of_week,
    SUM(transaction_qty * unit_price) AS revenue
FROM sales_cleaned
GROUP BY day_of_week
ORDER BY revenue DESC;

-- 6. "Churn-like" metric: inactive products (not sold in the last 90 days)
SELECT DISTINCT product_detail
FROM sales_cleaned
WHERE product_id NOT IN (SELECT
    SELECT DISTINCT product_id
    FROM sales_cleaned
    WHERE transaction_date >= CURDATE() - INTERVAL 90 DAY
);

-- 7. Recommender-style: products frequently bought together
SELECT 
    a.product_detail AS product_a,
    b.product_detail AS product_b,
    COUNT(*) AS times_bought_together
FROM sales_cleaned a
JOIN sales_cleaned b
    ON a.transaction_id = b.transaction_id
    AND a.product_id < b.product_id
GROUP BY a.product_detail, b.product_detail
ORDER BY times_bought_together DESC
LIMIT 10;

-- 8. Customer segmentation: high-value products (top 10% by revenue)
WITH product_revenue AS (
    SELECT product_detail, SUM(transaction_qty * unit_price) AS total_revenue
    FROM sales_cleaned
    GROUP BY product_detail
), ranked_products AS (
    SELECT 
        product_detail, 
        total_revenue,
        NTILE(10) OVER (ORDER BY total_revenue DESC) AS revenue_decile
    FROM product_revenue
)
SELECT product_detail, total_revenue
FROM ranked_products
WHERE revenue_decile = 1
ORDER BY total_revenue DESC;


-- 9. Monthly sales growth rate
WITH monthly_revenue AS (
    SELECT 
        DATE_FORMAT(transaction_date, '%Y-%m') AS month,
        SUM(transaction_qty * unit_price) AS total_revenue
    FROM sales_cleaned
    GROUP BY month
)
SELECT 
    month,
    total_revenue,
    LAG(total_revenue) OVER (ORDER BY month) AS previous_month_revenue,
    CASE 
        WHEN LAG(total_revenue) OVER (ORDER BY month) IS NULL THEN NULL
        ELSE (total_revenue - LAG(total_revenue) OVER (ORDER BY month)) / LAG(total_revenue) OVER (ORDER BY month) * 100
    END AS growth_rate_percentage
FROM monthly_revenue
ORDER BY month;

