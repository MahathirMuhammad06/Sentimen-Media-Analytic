#!/usr/bin/env python3
"""
Migration Script: Add Source Health Tracking Columns
=======================================================

Purpose:
    Adds 5 new columns to news_sources table for tracking source health
    - last_successful_crawl (DateTime): Last time articles were successfully extracted
    - consecutive_failures (Integer): Count of consecutive failed crawls
    - last_crawl_article_count (Integer): Number of articles in last crawl
    - failure_reason (String): Reason why source became inactive
    - inactivity_detected_at (DateTime): When inactivity was detected

Status:
    - Database: SQLite (media_analytics.db)
    - Backward Compatible: YES (all fields nullable or have defaults)
    - Rollback Required: NO (safe to rerun)

Run:
    python migrate_add_source_health_tracking.py
"""

import sqlite3
import os
from datetime import datetime

# Database path
DB_PATH = os.path.join(os.getcwd(), "database", "media_analytics.db")

# Migration definitions
MIGRATIONS = [
    {
        "name": "Add last_successful_crawl column",
        "sql": "ALTER TABLE news_sources ADD COLUMN last_successful_crawl DATETIME DEFAULT NULL;",
        "description": "Track last time articles were successfully extracted"
    },
    {
        "name": "Add consecutive_failures column", 
        "sql": "ALTER TABLE news_sources ADD COLUMN consecutive_failures INTEGER DEFAULT 0;",
        "description": "Count consecutive failed crawls (resets on success)"
    },
    {
        "name": "Add last_crawl_article_count column",
        "sql": "ALTER TABLE news_sources ADD COLUMN last_crawl_article_count INTEGER DEFAULT 0;",
        "description": "Number of articles extracted in last crawl"
    },
    {
        "name": "Add failure_reason column",
        "sql": "ALTER TABLE news_sources ADD COLUMN failure_reason VARCHAR(255) DEFAULT NULL;",
        "description": "Reason why source became inactive"
    },
    {
        "name": "Add inactivity_detected_at column",
        "sql": "ALTER TABLE news_sources ADD COLUMN inactivity_detected_at DATETIME DEFAULT NULL;",
        "description": "Timestamp when inactivity was detected"
    }
]

def column_exists(conn, table_name, column_name):
    """Check if column already exists"""
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT {column_name} FROM {table_name} LIMIT 1")
        return True
    except sqlite3.OperationalError:
        return False

def run_migrations():
    """Run all migrations"""
    if not os.path.exists(DB_PATH):
        print(f"❌ ERROR: Database not found at {DB_PATH}")
        print("   Please ensure media_analytics.db exists before running migration")
        return False
    
    print(f"📦 Database Path: {DB_PATH}")
    print(f"📅 Migration Started: {datetime.now()}")
    print("-" * 70)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total_migrations = len(MIGRATIONS)
    successful = 0
    skipped = 0
    failed = 0
    
    try:
        for i, migration in enumerate(MIGRATIONS, 1):
            name = migration["name"]
            sql = migration["sql"]
            desc = migration["description"]
            column_name = sql.split("ADD COLUMN ")[1].split(" ")[0]
            
            print(f"\n[{i}/{total_migrations}] {name}")
            print(f"    → {desc}")
            
            # Check if column already exists
            if column_exists(conn, "news_sources", column_name):
                print(f"    ✓ SKIPPED (column already exists)")
                skipped += 1
                continue
            
            try:
                cursor.execute(sql)
                conn.commit()
                print(f"    ✓ SUCCESS")
                successful += 1
            except Exception as e:
                print(f"    ✗ FAILED: {str(e)}")
                failed += 1
                continue
        
        print("\n" + "=" * 70)
        print(f"📊 Migration Summary")
        print(f"   ✓ Successful: {successful}/{total_migrations}")
        print(f"   ↷ Skipped:   {skipped}/{total_migrations}")
        print(f"   ✗ Failed:    {failed}/{total_migrations}")
        
        if failed == 0:
            print(f"\n✅ Migration completed successfully!")
            
            # Show table structure
            print("\n📋 Updated news_sources table structure:")
            cursor.execute("PRAGMA table_info(news_sources)")
            columns = cursor.fetchall()
            print("   Columns:")
            for col in columns:
                col_name = col[1]
                col_type = col[2]
                is_pk = "PRIMARY KEY" if col[5] else ""
                is_not_null = "NOT NULL" if col[3] else ""
                
                attrs = " ".join([is_pk, is_not_null]).strip()
                if attrs:
                    attrs = f"({attrs})"
                print(f"     • {col_name}: {col_type} {attrs}".rstrip())
            
            return True
        else:
            print(f"\n⚠️  Migration completed with errors. Please review above.")
            return False
    
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {str(e)}")
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║      SOURCE HEALTH TRACKING - DATABASE MIGRATION                  ║
║                                                                   ║
║  Adds columns to track:                                           ║
║  • Last successful crawl timestamp                               ║
║  • Consecutive failure count (auto-marks inactive at 3)          ║
║  • Articles extracted in last crawl                              ║
║  • Reason for inactivity                                         ║
║  • When inactivity was detected                                  ║
╚═══════════════════════════════════════════════════════════════════╝
    """)
    
    success = run_migrations()
    exit(0 if success else 1)
