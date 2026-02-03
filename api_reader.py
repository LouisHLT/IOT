import time
import requests
from datetime import datetime
from collections import deque

import data_check as dc
from logger import logger
import database.utils as dbutils
from data_buffer import make_station_buffers
from threshold import check_threshold, manage_alert
from config import STATION_CACHE, STATION_LOCK, STATIONS, ESP_URL, POLL_INTERVAL


def get_or_create_station_id(device_id: str) -> int:
    with STATION_LOCK:
        if device_id in STATION_CACHE:
            return STATION_CACHE[device_id]

        station_id = dbutils.add_station(device_id=device_id)
        STATION_CACHE[device_id] = station_id
        return station_id



def http_reader():
    while True:
        try:
            # Read from ESP8266 via HTTP
            r = requests.get(ESP_URL, timeout=2)
            r.raise_for_status()
            parsed = r.json()

            # Data validation
            parsed = {
                "device_id": parsed.get("id", "esp8266"),
                "temperature": parsed["t"],
                "humidity": parsed["h"],
                "co2": parsed["co2"],
                "o2": parsed["o2"],
                "light": parsed["lux"],
            }

            # Check for out-of-range values
            cleaned, was_corrected, fields = dc.oof_values(parsed)

            sid = cleaned["device_id"]
            with STATION_LOCK: # ensure thread-safe access to STATIONS
                if sid not in STATIONS: # create buffers if new station
                    STATIONS[sid] = make_station_buffers() # initialize buffers; store the station datas
                station = STATIONS[sid]

            if was_corrected:
                logger.warning("OOF - " + dc.format_values(parsed))
                logger.warning("CORRECTED: " + ", ".join(fields))
            logger.info(dc.format_values(cleaned))

            # Send Notifications/Warning/Danger
            values_obj = {
                "temp": cleaned["temperature"],
                "hum": cleaned["humidity"],
                "co2": cleaned["co2"],
                "o2": cleaned["o2"],
                "light": cleaned["light"]
            }

            alert_key, subject, contents = check_threshold(values_obj)
            now = datetime.now()
            device_id = cleaned["device_id"]

            manage_alert(device_id, alert_key, subject, contents, now)

            # Store in DB and update buffers
            station_id = get_or_create_station_id(cleaned["device_id"]) # get or create station in DB
            now = datetime.now()
            
            dbutils.add_reading(
                station_id=station_id,
                temperature=cleaned["temperature"],
                humidity=cleaned["humidity"],
                co2=cleaned["co2"],
                o2=cleaned["o2"],
                light=cleaned["light"],
                ts=now,
            )
            station["timestamps"].append(now)
            station["temp"].append(cleaned["temperature"])
            station["hum"].append(cleaned["humidity"])
            station["co2"].append(cleaned["co2"])
            station["o2"].append(cleaned["o2"])
            station["light"].append(cleaned["light"])
            station["last_seen"] = now

        except Exception as e:
            logger.warning(f"Serial read error: {e}")
            time.sleep(1)

        time.sleep(POLL_INTERVAL)
