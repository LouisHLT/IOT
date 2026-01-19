import os
import sys
import time
import serial
import logging
import requests
import threading
from collections import deque
from datetime import datetime
from dotenv import load_dotenv
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

import data_check as dc
from threading import Lock
import database.utils as dbutils
from input_parsing import parse_line
from logger import logger
from utils import empty_dashboard

STATION_CACHE = {}
STATION_LOCK = Lock()
STATIONS = {}

# SERIAL_PORT = "/dev/ttyACM0"
SERIAL_PORT = "/dev/ttyUSB0"
BAUD_RATE = 9600
MAX_POINTS = 120              
UPDATE_MS = 200

ESP_URL = "http://192.168.1.53/api"
POLL_INTERVAL = 2  # seconds

def get_or_create_station_id(device_id: str) -> int:
    with STATION_LOCK:
        if device_id in STATION_CACHE:
            return STATION_CACHE[device_id]

        station_id = dbutils.add_station(device_id=device_id)
        STATION_CACHE[device_id] = station_id
        return station_id

def make_station_buffers():
    """ 
        Create buffers for storing station data.

        Returns:
            A dictionary containing deques for each sensor value.
    """
    return {
        "timestamps": deque(maxlen=MAX_POINTS),
        "temp": deque(maxlen=MAX_POINTS),
        "hum": deque(maxlen=MAX_POINTS),
        "co2": deque(maxlen=MAX_POINTS),
        "o2": deque(maxlen=MAX_POINTS),
        "light": deque(maxlen=MAX_POINTS),
        "last_seen": None,
    }

def http_reader():
    while True:
        try:
            r = requests.get(ESP_URL, timeout=2)
            r.raise_for_status()
            parsed = r.json()

            parsed = {
                "device_id": parsed.get("id", "esp8266"),
                "temperature": parsed["t"],
                "humidity": parsed["h"],
                "co2": parsed["co2"],
                "o2": parsed["o2"],
                "light": parsed["lux"],
            }

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

#---- DASHBOARD ----#

t = threading.Thread(target=http_reader, daemon=True)
t.start()

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Dashboard Arduino – Environnement"),
    
    dcc.Dropdown(
        id="station-selector",
        placeholder="Select a station",
        clearable=False,
    ),

    html.Div(id="device-info", style={"padding": "10px", "fontWeight": "bold", "fontSize": "16px"}),

    html.Div([
        html.Div(id="value-temp", style={"padding": "10px"}),
        html.Div(id="value-hum", style={"padding": "10px"}),
        html.Div(id="value-co2", style={"padding": "10px"}),
        html.Div(id="value-o2", style={"padding": "10px"}),
        html.Div(id="value-light",style={"padding": "10px"}),
    ], style={"display": "flex", "flexWrap": "wrap"}),

    dcc.Graph(id="graph-temp"),
    dcc.Graph(id="graph-gas"),
    dcc.Graph(id="graph-humidity"),
    dcc.Graph(id="graph-light"),

    dcc.Interval(
        id="interval-component",
        interval=UPDATE_MS,
        n_intervals=0
    )
])

@app.callback(
    Output("station-selector", "options"),
    Input("interval-component", "n_intervals"),
)

def update_dashboard(_):
    with STATION_LOCK:
        return [
            {"label": sid, "value": sid}
            for sid in sorted(STATIONS.keys())
        ]

@app.callback(
    [
        Output("device-info", "children"),
        Output("value-temp", "children"),
        Output("value-hum", "children"),
        Output("value-co2", "children"),
        Output("value-o2", "children"),
        Output("value-light", "children"),
        Output("graph-temp", "figure"),
        Output("graph-gas", "figure"),
        Output("graph-humidity", "figure"),
        Output("graph-light", "figure"),
    ],
    [
        Input("interval-component", "n_intervals"),
        Input("station-selector", "value"),
    ],
)
def update_dashboard(_, selected_sid):

    with STATION_LOCK:
        if not STATIONS:
            return empty_dashboard()

        # if nothing selected yet → pick first station
        if selected_sid not in STATIONS:
            selected_sid = next(iter(STATIONS))

        station = STATIONS[selected_sid]

        if not station["timestamps"]:
            return empty_dashboard()

        x = list(station["timestamps"])
        temp = list(station["temp"])
        hum = list(station["hum"])
        co2 = list(station["co2"])
        o2 = list(station["o2"])
        light = list(station["light"])

    # -------- GRAPHS --------

    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=x, y=temp, mode="lines", name="Temp (°C)"))
    temp_fig.update_layout(
        title="Temperature",
        xaxis_title="Time",
        yaxis_title="Temp (°C)",
    )

    gas_fig = go.Figure()
    gas_fig.add_trace(go.Scatter(x=x, y=co2, mode="lines", name="CO2 ppm"))
    gas_fig.add_trace(go.Scatter(x=x, y=o2, mode="lines", name="O2 %", yaxis="y2"))
    gas_fig.update_layout(
        title="O2 / CO2",
        xaxis_title="Time",
        yaxis=dict(title="CO2 (ppm)"),
        yaxis2=dict(title="O2 (%)", overlaying="y", side="right"),
    )

    hum_fig = go.Figure()
    hum_fig.add_trace(go.Scatter(x=x, y=hum, mode="lines", name="Humidity"))
    hum_fig.update_layout(
        title="Humidity",
        xaxis_title="Time",
        yaxis_title="Humidity (%)",
    )

    light_fig = go.Figure()
    light_fig.add_trace(go.Scatter(x=x, y=light, mode="lines", name="Light"))
    light_fig.update_layout(
        title="Light",
        xaxis_title="Time",
        yaxis_title="Light (%)",
    )

    # -------- LAST VALUES --------

    return (
        f"Station ID: {selected_sid}",
        f"Temperature : {temp[-1]:.1f} °C",
        f"Humidity : {hum[-1]:.1f} %",
        f"CO2 (simulated) : {co2[-1]:.0f} ppm",
        f"O2 (simulated) : {o2[-1]:.2f} %",
        f"Light : {light[-1]:.1f} %",
        temp_fig,
        gas_fig,
        hum_fig,
        light_fig,
    )


debug_mode = True
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    if arg in ['-false', 'false', '0']:
        debug_mode = False
    elif arg in ['-true', 'true', '1']:
        debug_mode = True

if __name__ == "__main__":
    app.run(debug=debug_mode)