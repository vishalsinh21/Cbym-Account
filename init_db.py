import os
import psycopg2
from urllib.parse import urlparse

# Get database URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    print("Error: DATABASE_URL environment variable not set.")
    print("Set it first before running this script.")
    exit(1)

def get_db_connection():
    result = urlparse(DATABASE_URL)
    username = result.username
    password = result.password
    database = result.path[1:]
    hostname = result.hostname
    port = result.port
    conn = psycopg2.connect(
        dbname=database,
        user=username,
        password=password,
        host=hostname,
        port=port
    )
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    # Contributors table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS contributors(
            id SERIAL PRIMARY KEY,
            name TEXT,
            email TEXT,
            amount REAL,
            payment_method TEXT
        )
    """)

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses(
            id SERIAL PRIMARY KEY,
            title TEXT,
            amount REAL
        )
    """)

    # Add default admin if missing
    cursor.execute("SELECT * FROM users WHERE username='admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users(username,password) VALUES('admin','admin')")

    conn.commit()
    cursor.close()
    conn.close()
    print("Database initialized successfully!")

if __name__ == "__main__":
    init_db()
