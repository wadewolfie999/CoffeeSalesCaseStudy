-- optimization.sql additions (master-level)
-- 1. Store-level queries (modules 1,4)
CREATE INDEX idx_store_location ON sales_cleaned(store_location(50));

CREATE INDEX idx_store_type ON sales_cleaned(store_location(50), product_type(50));

-- 2. Product-level queries (modules 2,4,8)
CREATE INDEX idx_product_detail ON sales_cleaned(product_detail(50));

CREATE INDEX idx_product_type ON sales_cleaned(product_type(50));

-- 3. Date-level queries (modules 3,5,6,9)
CREATE INDEX idx_transaction_date ON sales_cleaned(transaction_date);

CREATE INDEX idx_product_date ON sales_cleaned(product_id, transaction_date);

-- 4. Join-related queries (module 7)
CREATE INDEX idx_transaction_id ON sales_cleaned(transaction_id);

CREATE INDEX idx_transaction_product ON sales_cleaned(transaction_id, product_id);