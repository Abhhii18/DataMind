import sqlite3
from pathlib import Path
from faker import Faker
import random
from datetime import datetime, timedelta

# Initialize Faker
fake = Faker()

# Always create the database in the same folder as this script.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "ecommerce.db"

# Connect to database
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# --- 1. Create Tables ---
cursor.execute("DROP TABLE IF EXISTS orders")
cursor.execute("DROP TABLE IF EXISTS products")
cursor.execute("DROP TABLE IF EXISTS customers")

cursor.execute("""
    CREATE TABLE customers (
        customer_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT,
        city TEXT,
        signup_date TEXT
    )
""")

cursor.execute("""
    CREATE TABLE products (
        product_id INTEGER PRIMARY KEY,
        product_name TEXT NOT NULL,
        category TEXT,
        price REAL
    )
""")

cursor.execute("""
    CREATE TABLE orders (
        order_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        product_id INTEGER,
        quantity INTEGER,
        order_date TEXT,
        FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
        FOREIGN KEY (product_id) REFERENCES products(product_id)
    )
""")

# --- 2. Generate Realistic Data with Faker ---

print("🔄 Generating customers...")
customers = []
cities = ["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Seattle", "Austin"]
for i in range(1, 101):  # Generate 100 customers
    customers.append((
        i,
        fake.name(),
        fake.email(),
        random.choice(cities),
        fake.date_between(start_date='-2y', end_date='today').isoformat()
    ))
cursor.executemany("INSERT INTO customers VALUES (?, ?, ?, ?, ?)", customers)

print("🔄 Generating products...")
products = [
    (1, "MacBook Pro", "Electronics", 1999.99),
    (2, "Sony Headphones", "Electronics", 249.99),
    (3, "Ergonomic Mouse", "Electronics", 79.99),
    (4, "Ceramic Coffee Mug", "Kitchen", 14.99),
    (5, "Stainless Steel Water Bottle", "Kitchen", 24.99),
    (6, "Yoga Mat", "Fitness", 29.99),
    (7, "Dumbbell Set (20lb)", "Fitness", 89.99),
    (8, "Canvas Backpack", "Accessories", 49.99),
    (9, "LED Desk Lamp", "Home", 39.99),
    (10, "Mechanical Keyboard", "Electronics", 129.99),
]
cursor.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)

print("🔄 Generating orders...")
orders = []
start_date = datetime.now() - timedelta(days=180) # Last 6 months
for i in range(1, 501):  # Generate 500 orders
    order_date = fake.date_time_between(start_date=start_date, end_date='now')
    orders.append((
        i,
        random.randint(1, 100),   # Random customer_id
        random.randint(1, 10),    # Random product_id
        random.randint(1, 5),     # Quantity between 1 and 5
        order_date.strftime('%Y-%m-%d')
    ))
cursor.executemany("INSERT INTO orders VALUES (?, ?, ?, ?, ?)", orders)

# --- 3. Save and Close ---
conn.commit()
conn.close()

print("✅ Success! Database 'ecommerce.db' created with:")
print("   - 100 Customers")
print("   - 10 Products")
print("   - 500 Orders")
print("🚀 Try asking: 'What is the total revenue from Electronics?' or 'Which city has the most orders?'")