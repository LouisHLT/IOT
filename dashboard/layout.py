
from dash import dcc, html
from config import UPDATE_MS

def build_layout():
    return html.Div([
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