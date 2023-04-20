import sqlite3

conn = sqlite3.connect('sqlite3.db')
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS events_list(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_event TEXT NOT NULL,
    manager_name TEXT NOT NULL,
    manager_id TEXT,
    manager_email TEXT NOT NULL,
    user_count INT, 
    date_register TEXT,
    event_date TEXT);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS past_events_list(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name_event TEXT NOT NULL,
    manager_name TEXT NOT NULL,
    manager_id TEXT,
    manager_email TEXT NOT NULL,
    user_count INT, 
    date_register TEXT,
    event_date TEXT);
""")

cur.execute("""CREATE TABLE IF NOT EXISTS admins(
    username TEXT);
""")

conn.commit()

