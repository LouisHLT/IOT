import os
import sys
import time
import serial
import logging
import threading
from collections import deque
from datetime import datetime
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

from threading import Lock
from data_check import oof_values, threshold_management, format_values


LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)
# Configure logging
log_filename = os.path.join(LOG_DIR, f"arduino_data_{datetime.now().strftime('%Y%m%d')}.log")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
MAX_POINTS = 120              
UPDATE_MS = 200

data_lock = Lock()
timestamps = deque(maxlen=MAX_POINTS)
device_ids = deque(maxlen=MAX_POINTS)
hum_buf = deque(maxlen=MAX_POINTS)
temp_buf = deque(maxlen=MAX_POINTS)
co2_buf = deque(maxlen=MAX_POINTS)
o2_buf = deque(maxlen=MAX_POINTS)
light_buf = deque(maxlen=MAX_POINTS)

def parse_line(line: str):
    """ 
        Parse a line of serial data into a dictionary.
        Expected format: "device_id,humidity,temperature,co2,o2,light" (with device_id)
        or "humidity,temperature,co2,o2,light" (legacy format without device_id)
        
        Args:
            line: A string from the serial port
        
        Returns:
            A dictionary with keys: device_id, humidity, temperature, co2, o2, light
    """
    parts = line.strip().split(",")
    
    # Handle format with device_id (6 parts)
    if len(parts) == 6:
        try:
            return {
                'device_id': parts[0],
                'humidity': float(parts[1]),
                'temperature': float(parts[2]),
                'co2': float(parts[3]),
                'o2': float(parts[4]),
                'light': float(parts[5])
            }
        except ValueError:
            return None
    
    # Handle legacy format without device_id (5 parts)
    elif len(parts) == 5:
        try:
            return {
                'device_id': 'arduino_wired',  # Default ID for wired Arduino
                'humidity': float(parts[0]),
                'temperature': float(parts[1]),
                'co2': float(parts[2]),
                'o2': float(parts[3]),
                'light': float(parts[4])
            }
        except ValueError:
            return None
    else:
        return None
    
def serial_reader():
    """ 
        Thread function to read from serial port continuously.
        Parses data and appends to buffers.

        Args:
            None

        Returns: 
            None
    """
    while True:
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                time.sleep(2)  # reset Arduino
                while True:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not raw:
                        continue
                    parsed = parse_line(raw)
                    if parsed is None:
                        continue
                    
                    parsed = parsed.copy()
                    cleaned, was_corrected, fields = oof_values(parsed)
                    # cleaned = oof_values(parsed)
                    if was_corrected:
                        logger.warning("OOF - " + format_values(parsed))
                        logger.warning("CORRECTED: " + ", ".join(fields))

                    logger.info(format_values(cleaned))
                    
                    now = datetime.now()
                    timestamps.append(now)
                    device_ids.append(cleaned['device_id'])
                    hum_buf.append(cleaned['humidity'])
                    temp_buf.append(cleaned['temperature'])
                    co2_buf.append(cleaned['co2'])
                    o2_buf.append(cleaned['o2'])
                    light_buf.append(cleaned['light'])

        except Exception as e:
            logger.warning(f"Serial read error: {e}")
            time.sleep(1)

t = threading.Thread(target=serial_reader, daemon=True)
t.start()

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Dashboard Arduino – Environnement"),
    
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
    Input("interval-component", "n_intervals")
)

def update_dashboard(n: int):
    """ 
        Update dashboard values and graphs.
        
        Args:
            n: Number of intervals passed (not used)

        Returns:
            Updated values and figures for the dashboard
    """
    with data_lock:
        if not timestamps:
            empty_text = "waiting for datas..."
            empty_fig = go.Figure()
            return (empty_text, empty_text, empty_text, empty_text, empty_text, empty_text,
                    empty_fig, empty_fig, empty_fig, empty_fig)

    
    x = list(timestamps)

    # TEMP 
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=x, y=list(temp_buf), mode="lines", name="Temp (°C)"))
    temp_fig.update_layout(
        title="Temperature",
        xaxis_title="Time",
        yaxis=dict(title="Temp (°C)", side="left"),
        legend=dict(orientation="h"),
        transition={'duration': 100}
    )


    #02/C02
    gas_fig = go.Figure()
    gas_fig.add_trace(go.Scatter(x=x, y=list(co2_buf), mode="lines", name="CO2 ppm", yaxis="y"))
    gas_fig.add_trace(go.Scatter(x=x, y=list(o2_buf), mode="lines", name="O2 %", yaxis="y2"))
    gas_fig.update_layout(
        title="O2/CO2 values (simulated)",
        xaxis_title="Temps",
        yaxis=dict(title="CO2 (ppm)", side="left"),
        yaxis2=dict(title="O2 (%)", side="right", overlaying="y"),
        legend=dict(orientation="h"),
        transition={'duration': 100}
    )

    # HUM
    hum_fig = go.Figure()
    hum_fig.add_trace(go.Scatter(x=x, y=list(hum_buf), mode="lines", name="Humidity"))
    hum_fig.update_layout(
        title="Humididy",
        xaxis_title="Time",
        yaxis=dict(title="Humidity (%)"),
        legend=dict(orientation="h")
    )

    # LIGHT
    light_fig = go.Figure()
    light_fig.add_trace(go.Scatter(x=x, y=list(light_buf), mode="lines", name="Light"))
    light_fig.update_layout(
        title="Light",
        xaxis_title="Time",
        yaxis_title="Light (%)",
        legend=dict(orientation="h"),
        transition={'duration': 100}
    )

    last_device_id = device_ids[-1]
    last_temp  = temp_buf[-1]
    last_hum   = hum_buf[-1]
    last_co2   = co2_buf[-1]
    last_o2    = o2_buf[-1]
    last_light = light_buf[-1]

    return (
        f"📡 Device ID: {last_device_id}",
        f"Temperature : {last_temp:.1f} °C",
        f"Humidity : {last_hum:.1f} %",
        f"CO2 (simulated) : {last_co2} ppm",
        f"O2 (simulated) : {last_o2} %",
        f"Light : {last_light} %",
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