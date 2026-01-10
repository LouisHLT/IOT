import sqlite3
from datetime import datetime

DB_PATH = "stations.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def add_station(device_id: str, location: str | None = None, room: str | None = None) -> int:
    """ 
        Add a new station to the database or get existing station ID.

        Args:
            device_id: Unique identifier for the device
            location: Location description
            room: Room name

        Returns:
            The station ID 
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO stations (device_id, location, room) VALUES (?, ?, ?)",
        (device_id, location, room),
    )
    conn.commit()
    
    cur.execute("SELECT id FROM stations WHERE device_id = ?", (device_id,))
    station_id = cur.fetchone()[0]
    
    conn.close()
    return station_id

def list_stations():
    """ 
        List all stations in the database.

        Returns:
            A list of tuples with (id, device_id, location, room)
    """
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
    """ 
        Add a new reading to the database.  

        Args:
            station_id: ID of the station
            temperature: Temperature value
            humidity: Humidity value
            co2: CO2 level
            o2: O2 level
            light: Light level
            ts: Timestamp of the reading (defaults to now if None)

        Returns:
            None 
    """
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
    """ 
        Retrieve the last reading for a given station.

        Args:
            station_id: ID of the station

        Returns:
            A tuple with (timestamp, temperature, humidity, co2, o2, light)
    """
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
