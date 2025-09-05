import os
import psycopg2
from urllib.parse import urlparse
from app import init_db  # import the function from app.py

os.environ["DATABASE_URL"] = "postgres://cbym_account_user:Mu1ZKfWPcET3LMXDGIZPhu39tRd71AMX@dpg-d2t5tkje5dus73dgu1b0-a/cbym_account"

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
