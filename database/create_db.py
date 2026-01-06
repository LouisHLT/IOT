import sqlite3

DB_PATH = "stations.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS stations (
            id INTEGER PRIMARY KEY,
            device_id TEXT NOT NULL UNIQUE,
            location TEXT,
            room TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS readings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            station_id INTEGER NOT NULL,
            timestamp TEXT NOT NULL,
            temperature REAL,
            humidity REAL,
            co2 REAL,
            o2 REAL,
            light REAL,
            FOREIGN KEY (station_id) REFERENCES stations(id)
        )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
