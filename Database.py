import sqlite3

DB_NAME = "booking.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS movies (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    duration INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS buses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    route TEXT,
                    seats INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS bookings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user TEXT,
                    type TEXT,
                    ref_id INTEGER)''')
    conn.commit()
    conn.close()
