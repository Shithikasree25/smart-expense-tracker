import sqlite3

DB_NAME = "expense.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    # Users table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    # Expenses table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        amount REAL,
        category TEXT,
        date TEXT
    )
    """)

    conn.commit()
    conn.close()
    print("Database Initialized Successfully!")

if __name__ == "__main__":
    init_db()
