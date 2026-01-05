import sys
import time
import serial
import threading
from collections import deque
from datetime import datetime
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

from threading import Lock
from log_values import logger
from data_check import oof_values, threshold_management, format_values

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
MAX_POINTS = 300              
UPDATE_MS = 1000

data_lock = Lock()
timestamps = deque(maxlen=MAX_POINTS)
hum_buf = deque(maxlen=MAX_POINTS)
temp_buf = deque(maxlen=MAX_POINTS)
co2_buf = deque(maxlen=MAX_POINTS)
o2_buf = deque(maxlen=MAX_POINTS)
light_buf = deque(maxlen=MAX_POINTS)

def parse_line(line: str):
    """ 
        Parse a line of serial data into a dictionary.
        Expected format: "humidity,temperature,co2,o2,light
        
        Args:
            line: A string from the serial port
        
        Returns:
            A dictionary with keys: humidity, temperature, co2, o2, light
    """
    parts = line.strip().split(",")
    if len(parts) != 5:
        return None
    try:
        return {
            'humidity': float(parts[0]),
            'temperature': float(parts[1]),
            'co2': float(parts[2]),
            'o2': float(parts[3]),
            'light': float(parts[4])
        }
    except ValueError:
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
                time.sleep(1)  # reset Arduino
                while True:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not raw:
                        continue
                    parsed = parse_line(raw)
                    if parsed is None:
                        continue
                    
                    cleaned, was_corrected, fields = oof_values(parsed)
                    if was_corrected:
                        logger.warning("OOF - " + format_values(parsed))
                        logger.warning("CORRECTED: " + ", ".join(fields))

                    logger.info(format_values(cleaned))
                    
                    with data_lock:
                        hum_buf.append(cleaned['humidity'])
                        temp_buf.append(cleaned['temperature'])
                        co2_buf.append(cleaned['co2'])
                        o2_buf.append(cleaned['o2'])
                        light_buf.append(cleaned['light'])

        except Exception as e:
            logger.error(f"Serial read error: {e}")
            time.sleep(1)

t = threading.Thread(target=serial_reader, daemon=True)
t.start()

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Dashboard Arduino – Environnement"),

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
            return (empty_text, empty_text, empty_text, empty_text, empty_text,
                    empty_fig, empty_fig, empty_fig, empty_fig)

    
    x = list(timestamps)
    temps = list(temp_buf)
    hums = list(hum_buf)
    co2s = list(co2_buf)
    o2s = list(o2_buf)
    lights = list(light_buf)

    print("x:", x)
    print("temps:", temps)
    print("hums:", hums)
    print("co2s:", co2s)
    print("o2s:", o2s)
    print("lights:", lights)

    # TEMP 
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=x, y=temps, mode="lines", name="Temp (°C)"))
    temp_fig.update_layout(
        title="Temperature",
        xaxis_title="Time",
        yaxis=dict(title="Temp (°C)", side="left"),
        legend=dict(orientation="h")
    )


    #02/C02
    gas_fig = go.Figure()
    gas_fig.add_trace(go.Scatter(x=x, y=co2s, mode="lines", name="CO2 ppm"))
    gas_fig.add_trace(go.Scatter(x=x, y=o2s, mode="lines", name="O2 %"))
    gas_fig.update_layout(
        title="O2/CO2 values (simulated)",
        xaxis_title="Temps",
        yaxis_title="Values",
        legend=dict(orientation="h")
    )

    # HUM
    hum_fig = go.Figure()
    hum_fig.add_trace(go.Scatter(x=x, y=hums, mode="lines", name="Humidity"))
    hum_fig.update_layout(
        title="Humididy",
        xaxis_title="Time",
        yaxis=dict(title="Humidity (%)"),
        legend=dict(orientation="h")
    )

    # LIGHT
    light_fig = go.Figure()
    light_fig.add_trace(go.Scatter(x=x, y=lights, mode="lines", name="Light"))
    light_fig.update_layout(
        title="Light",
        xaxis_title="Time",
        yaxis_title="Light (%)",
        legend=dict(orientation="h")
    )

    last_temp  = temp_buf[-1]
    last_hum   = hum_buf[-1]
    last_co2   = co2_buf[-1]
    last_o2    = o2_buf[-1]
    last_light = light_buf[-1]

    return (
        f"=Temperature : {last_temp:.1f} °C",
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