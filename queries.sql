
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone VARCHAR(50) NOT NULL,
    address TEXT NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    order_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INT NOT NULL,
    product_id VARCHAR(50) NOT NULL,
    product_name VARCHAR(255) NOT NULL,
    quantity INT NOT NULL,
    price DECIMAL(10,2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS products (
    product_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    category TEXT
);


INSERT INTO products (product_id, name, price, stock, category) VALUES ('PC001', 'Shampoo (200ml)', 350.0, 50, 'Personal Care');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('PC002', 'Bath Soap (Multipack)', 220.0, 75, 'Personal Care');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('PC003', 'Toothpaste (Large)', 180.0, 60, 'Personal Care');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('PC004', 'Body Lotion (500ml)', 480.0, 40, 'Personal Care');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('PC005', 'Hand Wash (Refill)', 150.0, 90, 'Personal Care');

INSERT INTO products (product_id, name, price, stock, category) VALUES ('SNK001', 'Potato Chips (Large)', 120.0, 100, 'Snacks');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('SNK002', 'Chocolate Bar (King Size)', 90.0, 80, 'Snacks');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('SNK003', 'Assorted Biscuits (Pack)', 175.0, 70, 'Snacks');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('SNK004', 'Cookies (Family Pack)', 250.0, 60, 'Snacks');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('SNK005', 'Microwave Popcorn', 70.0, 120, 'Snacks');

INSERT INTO products (product_id, name, price, stock, category) VALUES ('GRC001', 'Basmati Rice (5kg)', 950.0, 30, 'Groceries');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('GRC002', 'Wheat Flour (10kg)', 800.0, 25, 'Groceries');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('GRC003', 'Cooking Oil (3 Liters)', 1200.0, 20, 'Groceries');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('GRC004', 'White Sugar (1kg)', 150.0, 50, 'Groceries');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('GRC005', 'Red Lentils (1kg)', 320.0, 45, 'Groceries');

INSERT INTO products (product_id, name, price, stock, category) VALUES ('HME001', 'Dishwashing Liquid (1L)', 280.0, 55, 'Home Essentials');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('HME002', 'Laundry Detergent (2kg)', 700.0, 35, 'Home Essentials');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('HME003', 'Paper Tissues (Box)', 110.0, 85, 'Home Essentials');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('HME004', 'Air Freshener Spray', 300.0, 40, 'Home Essentials');

INSERT INTO products (product_id, name, price, stock, category) VALUES ('BEV001', 'Instant Coffee (100g)', 600.0, 30, 'Beverages');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('BEV002', 'Green Tea Bags (50ct)', 450.0, 40, 'Beverages');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('BEV003', 'Orange Juice (1L)', 280.0, 50, 'Beverages');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('BEV004', 'Cola Soft Drink (2L)', 180.0, 70, 'Beverages');
INSERT INTO products (product_id, name, price, stock, category) VALUES ('BEV005', 'Mineral Water (6-pack)', 300.0, 100, 'Beverages');





