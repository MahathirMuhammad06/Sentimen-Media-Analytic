#!/usr/bin/env python3
"""
Migration Script: Add cleanup_schedules table
"""
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.getcwd(), "database", "media_analytics.db")

SQL_CREATE = """
CREATE TABLE IF NOT EXISTS cleanup_schedules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200),
    days_threshold INTEGER NOT NULL DEFAULT 30,
    interval_minutes INTEGER NOT NULL DEFAULT 1440,
    last_run DATETIME,
    active BOOLEAN DEFAULT 1,
    created_at DATETIME DEFAULT (datetime('now')),
    updated_at DATETIME DEFAULT (datetime('now'))
);
"""


def run():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return 1
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(SQL_CREATE)
    conn.commit()
    conn.close()
    print("Migration completed: cleanup_schedules table created or exists")
    return 0

if __name__ == '__main__':
    exit(run())
