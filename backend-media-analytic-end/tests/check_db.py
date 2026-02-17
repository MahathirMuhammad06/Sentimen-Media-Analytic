import sqlite3, os
DB = os.path.abspath('database/media_analytics.db')
print('DB path:', DB)
if not os.path.exists(DB):
    print('DB file does not exist')
else:
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    rows = cur.fetchall()
    print('tables:', [r[0] for r in rows])
    conn.close()
