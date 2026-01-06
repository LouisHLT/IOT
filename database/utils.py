import sqlite3
from datetime import datetime

DB_PATH = "stations.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def add_station(device_id: str, location: str | None = None, room: str | None = None) -> int:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO stations (device_id, location, room) VALUES (?, ?, ?)",
        (device_id, location, room),
    )
    conn.commit()
    
    # Get the station_id (either just inserted or already exists)
    cur.execute("SELECT id FROM stations WHERE device_id = ?", (device_id,))
    station_id = cur.fetchone()[0]
    
    conn.close()
    return station_id

def list_stations():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, device_id, location, room FROM stations")
    rows = cur.fetchall()
    conn.close()
    return rows

def add_reading(
    station_id: int,
    temperature: float | None = None,
    humidity: float | None = None,
    co2: float | None = None,
    o2: float | None = None,
    light: float | None = None,
    ts: datetime | None = None,
):
    if ts is None:
        ts = datetime.now()
    ts_str = ts.isoformat()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO readings (
            station_id, timestamp, temperature, humidity, co2, o2, light
        ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (station_id, ts_str, temperature, humidity, co2, o2, light),
    )
    conn.commit()
    conn.close()

def get_last_reading(station_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT timestamp, temperature, humidity, co2, o2, light
        FROM readings
        WHERE station_id = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (station_id,),
    )
    row = cur.fetchone()
    conn.close()
    return row
