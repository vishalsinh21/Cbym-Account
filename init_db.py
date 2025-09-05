# init_db.py
import os
from app import init_db  # Make sure init_db() is defined in app.py

if __name__ == "__main__":
    # Optional: Set environment variable if using DATABASE_URL from Render
    # os.environ["DATABASE_URL"] = "postgres://user:pass@host:port/dbname"

    init_db()
    print("Database initialized successfully!")
