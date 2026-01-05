import time
import threading
from collections import deque
from datetime import datetime

import serial
import plotly.graph_objs as go
from dash import Dash, dcc, html, Input, Output

from log_values import log_arduino_value

SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
MAX_POINTS = 300              
UPDATE_MS = 1000

timestamps = deque(maxlen=MAX_POINTS)
hum_buf = deque(maxlen=MAX_POINTS)
temp_buf = deque(maxlen=MAX_POINTS)
co2_buf = deque(maxlen=MAX_POINTS)
o2_buf = deque(maxlen=MAX_POINTS)
light_buf = deque(maxlen=MAX_POINTS)

def parse_line(line: str):
    parts = line.strip().split(",")
    if len(parts) != 5:
        return None
    try:
        return {
            'humidity': float(parts[0]),
            'temperature': float(parts[1]),
            'co2': int(parts[2]),
            'o2': int(parts[3]),
            'light': int(parts[4])
        }
    except ValueError:
        return None
    
def serial_reader():
    while True:
        try:
            with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as ser:
                time.sleep(0.5)  # reset Arduino
                while True:
                    raw = ser.readline().decode("utf-8", errors="ignore").strip()
                    if not raw:
                        continue
                    # print(f"Raw datas: {raw}")
                    parsed = parse_line(raw)
                    if parsed is None:
                        continue

                    now = datetime.now()
                    timestamps.append(now)
                    hum_buf.append(parsed['humidity'])
                    temp_buf.append(parsed['temperature'])
                    co2_buf.append(parsed['co2'])
                    o2_buf.append(parsed['o2'])
                    light = (parsed['light'] / 1023) * 100
                    light_buf.append(light)

                    # log the values
                    log_arduino_value(parsed)

        except Exception as e:
            print("Serial error:", e)
            time.sleep(1)

t = threading.Thread(target=serial_reader, daemon=True)
t.start()

app = Dash(__name__)

app.layout = html.Div([
    html.H2("Dashboard Arduino – Environnement"),

    # Affichage des valeurs instantanées
    html.Div([
        html.Div(id="value-temp", style={"padding": "10px"}),
        html.Div(id="value-hum", style={"padding": "10px"}),
        html.Div(id="value-co2", style={"padding": "10px"}),
        html.Div(id="value-o2", style={"padding": "10px"}),
        html.Div(id="value-light",style={"padding": "10px"}),
    ], style={"display": "flex", "flexWrap": "wrap"}),

    dcc.Graph(id="graph-temp"),
    dcc.Graph(id="graph-gas-light"),
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
        Output("graph-gas-light", "figure"),
        Output("graph-humidity", "figure"),
        Output("graph-light", "figure"),
    ],
    Input("interval-component", "n_intervals")
)
def update_dashboard(n):
    if not timestamps:
        empty_text = "waiting for datas..."
        empty_fig = go.Figure()
        return (empty_text,)*5 + (empty_fig, empty_fig)

    x = list(timestamps)


    # TEMP 
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=x, y=list(temp_buf), mode="lines", name="Temp (°C)"))
    temp_fig.update_layout(
        title="Temperature",
        xaxis_title="Time",
        yaxis=dict(title="Temp (°C)", side="left"),
        legend=dict(orientation="h")
    )


    #02/C02
    gas_fig = go.Figure()
    gas_fig.add_trace(go.Scatter(x=x, y=list(co2_buf), mode="lines", name="CO2 sim"))
    gas_fig.add_trace(go.Scatter(x=x, y=list(o2_buf), mode="lines", name="O2 sim"))
    gas_fig.update_layout(
        title="O2/CO2 values (simulated)",
        xaxis_title="Temps",
        yaxis_title="Values",
        legend=dict(orientation="h")
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
        yaxis_title="Values",
        legend=dict(orientation="h")
    )

    last_temp  = temp_buf[-1]
    last_hum   = hum_buf[-1]
    last_co2   = co2_buf[-1]
    last_o2    = o2_buf[-1]
    last_light = light_buf[-1]

    return (
        f"Température actuelle : {last_temp:.1f} °C",
        f"Humidité actuelle : {last_hum:.1f} %",
        f"CO2 (sim) : {last_co2}",
        f"O2 (sim) : {last_o2}",
        f"Lumière : {last_light}",
        temp_fig,
        gas_fig,
        hum_fig,
        light_fig,     
    )

if __name__ == "__main__":
    app.run(debug=True)
