from flask import Flask, request, jsonify
from datetime import datetime

import data_check as dc
from logger import logger
import database.utils as dbutils
from data_buffer import make_station_buffers
from threshold import check_threshold, manage_alert
from config import STATION_CACHE, STATION_LOCK, STATIONS

ingest_app = Flask(__name__)

def _process(parsed: dict):
    parsed = {
        "device_id":   str(parsed.get("id", "esp8266")),
        "temperature": parsed["t"],
        "humidity":    parsed["h"],
        "co2":         parsed["co2"],
        "o2":          parsed["o2"],
        "light":       parsed["lux"],
    }

    cleaned, was_corrected, fields = dc.oof_values(parsed)
    sid = cleaned["device_id"]

    # Single lock block for all shared-state access
    with STATION_LOCK:
        if sid not in STATIONS:
            STATIONS[sid] = make_station_buffers()
        station = STATIONS[sid]

        if sid not in STATION_CACHE:
            STATION_CACHE[sid] = dbutils.add_station(device_id=sid)
        station_id = STATION_CACHE[sid]

    # Logging and alerting outside the lock (no shared state touched)
    if was_corrected:
        logger.warning("OOF - " + dc.format_values(parsed))
        logger.warning("CORRECTED: " + ", ".join(fields))
    logger.info(dc.format_values(cleaned))

    values_obj = {
        "temp":  cleaned["temperature"],
        "hum":   cleaned["humidity"],
        "co2":   cleaned["co2"],
        "o2":    cleaned["o2"],
        "light": cleaned["light"],
    }
    alert_key, subject, contents = check_threshold(values_obj)
    now = datetime.now()
    manage_alert(sid, alert_key, subject, contents, now)

    # DB write (SQLite has its own internal locking)
    dbutils.add_reading(
        station_id=station_id,
        temperature=cleaned["temperature"],
        humidity=cleaned["humidity"],
        co2=cleaned["co2"],
        o2=cleaned["o2"],
        light=cleaned["light"],
        ts=now,
    )

    # Buffer writes — station ref is local, safe without lock
    station["timestamps"].append(now)
    station["temp"].append(cleaned["temperature"])
    station["hum"].append(cleaned["humidity"])
    station["co2"].append(cleaned["co2"])
    station["o2"].append(cleaned["o2"])
    station["light"].append(cleaned["light"])
    station["last_seen"] = now


@ingest_app.route("/ingest", methods=["POST"])
def ingest():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "bad json"}), 400
    try:
        _process(data)
        return jsonify({"ok": True}), 200
    except Exception as e:
        logger.warning(f"Ingest error: {e}")
        return jsonify({"error": str(e)}), 500