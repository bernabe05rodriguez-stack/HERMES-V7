import sqlite3
import os

DB_NAME = "users.db"

def get_db_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()

    # Create users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            hwid TEXT,
            active BOOLEAN DEFAULT 1,
            expiration_date TEXT
        )
    ''')

    # Create updates table
    c.execute('''
        CREATE TABLE IF NOT EXISTS updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT UNIQUE NOT NULL,
            filename TEXT NOT NULL,
            release_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()

# Initialize DB on import if not exists
if not os.path.exists(DB_NAME):
    init_db()
else:
    init_db() # Run init anyway to ensure tables exist
