import sqlite3
import os

DB_PATH = os.path.join(os.getcwd(), "database", "media_analytics.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # biar hasilnya dict-like
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS articles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        source TEXT,
        url TEXT,
        published_date TEXT,
        crawled_date TEXT DEFAULT CURRENT_TIMESTAMP,
        keywords_flagged TEXT,
        sentiment TEXT,
        confidence FLOAT,
        prob_negative FLOAT,
        prob_neutral FLOAT,
        prob_positvie FLOAT,
        category TEXT,
        author TEXT
    );
    """)
    
    conn.commit()
    conn.close()
