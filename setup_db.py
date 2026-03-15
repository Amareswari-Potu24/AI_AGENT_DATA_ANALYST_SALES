import sqlite3

conn = sqlite3.connect("sales.db")
cursor = conn.cursor()

cursor.executescript("""
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    category TEXT,
    unit_price REAL
);

CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT,
    region TEXT,
    email TEXT
);

CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER,
    customer_id INTEGER,
    quantity INTEGER,
    total_amount REAL,
    order_date TEXT,
    FOREIGN KEY (product_id) REFERENCES products(id),
    FOREIGN KEY (customer_id) REFERENCES customers(id)
);

INSERT INTO products (product_name, category, unit_price) VALUES
('Laptop Pro',     'Electronics', 1299.99),
('Wireless Mouse', 'Accessories',   49.99),
('USB-C Hub',      'Accessories',   79.99),
('Monitor 4K',     'Electronics',  649.99),
('Keyboard Mech',  'Accessories',  129.99);

INSERT INTO customers (customer_name, region, email) VALUES
('Alice Johnson', 'North', 'alice@example.com'),
('Bob Smith',     'South', 'bob@example.com'),
('Carol White',   'East',  'carol@example.com'),
('David Lee',     'West',  'david@example.com');

INSERT INTO orders (product_id, customer_id, quantity, total_amount, order_date) VALUES
(1,1,2,2599.98,'2025-10-05'),(2,2,5,249.95,'2025-10-12'),
(3,3,3,239.97,'2025-10-20'),(4,4,1,649.99,'2025-11-02'),
(1,2,1,1299.99,'2025-11-14'),(5,1,4,519.96,'2025-11-22'),
(2,3,10,499.90,'2025-12-01'),(3,4,2,159.98,'2025-12-09'),
(4,1,2,1299.98,'2025-12-18'),(1,3,3,3899.97,'2026-01-04'),
(5,2,6,779.94,'2026-01-15'),(2,4,8,399.92,'2026-01-25'),
(3,1,4,319.96,'2026-02-03'),(4,2,1,649.99,'2026-02-14'),
(1,4,2,2599.98,'2026-02-20'),(5,3,3,389.97,'2026-03-01'),
(2,1,15,749.85,'2026-03-08'),(4,4,3,1949.97,'2026-03-12');
""")

conn.commit()
conn.close()
print("Database created successfully! sales.db is ready.")