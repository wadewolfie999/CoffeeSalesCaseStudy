CREATE DATABASE CoffeeSalesDB;


USE CoffeeSalesDB;


CREATE TABLE Sales (
transaction_id INT PRIMARY KEY,
transaction_date DATE,
transaction_time TIME,
transaction_qty INT,
store_id INT,
store_location VARCHAR(100),
product_id INT,
unit_price FLOAT,
product_category VARCHAR(100),
product_type VARCHAR(100),
product_detail VARCHAR(100)
);



