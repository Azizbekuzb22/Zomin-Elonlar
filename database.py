import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'zomin_market.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()

if __name__ == '__main__':
    # Initialize DB when run standalone
    if not os.path.exists(DB_PATH):
        init_db()
        print("Database initialized.")
