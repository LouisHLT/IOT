from dash import html, dcc, Input, Output
from datetime import datetime
import dash_mantine_components as dmc

from utils.utils import format_last_seen
from config import STATIONS, STATION_LOCK

OFFLINE_AFTER_SEC = 3.5


def hub_layout():
    return dmc.Container(
        children=[
            dmc.Group(
                justify="space-between",
                align="center",
                mb="xl",
                children=[
                    dmc.Title(
                        children=[
                            html.Span("Weather Station - ", style={"color": "#595a5c"}),
                            html.Span("HUB", style={"color": "#d14024"}),
                        ],
                        order=2,
                    ),
                    dmc.Text("Live overview", size="sm", c="dimmed"),
                ],
            ),
            dcc.Interval(id="hub-interval", interval=1000, n_intervals=0),
            dmc.Stack(id="hub-cards", gap="md"),
        ],
        size="xl",
        px=24,
        py=32,
    )


def metric_card(label, value, unit, accent):
    display = f"{value}{unit}" if value is not None else "—"
    return dmc.Card(
        withBorder=True,
        radius="md",
        p="sm",
        style={"borderLeft": f"4px solid {accent}"},
        children=[
            dmc.Stack(
                gap=4,
                children=[
                    dmc.Text(label, size="xs", c="dimmed"),
                    dmc.Text(display, size="xl", fw=700),
                ],
            )
        ],
    )


def station_card(sid, station, now):
    last_seen = station.get("last_seen")
    online = last_seen and (now - last_seen).total_seconds() < OFFLINE_AFTER_SEC

    temp  = round(station["temp"][-1],  1) if station["temp"]  else None
    hum   = round(station["hum"][-1],   1) if station["hum"]   else None
    co2   = round(station["co2"][-1],   0) if station["co2"]   else None
    o2    = round(station["o2"][-1],    1) if station["o2"]    else None
    light = round(station["light"][-1], 1) if station["light"] else None

    return dmc.Card(
        withBorder=True,
        radius="lg",
        px=24,
        py=20,
        shadow="sm",
        children=[
            dmc.Group(
                justify="space-between",
                mb="sm",
                children=[
                    dmc.Group(
                        gap="sm",
                        children=[
                            html.Img(src="/assets/weather_stt_icon_nbg.png", style={"height": "72px"}),
                            dmc.Text(f"Station: {sid}", fw=600),
                            dmc.Badge(
                                "ONLINE" if online else "OFFLINE",
                                color="green" if online else "red",
                                variant="light",
                            ),
                        ],
                    ),
                    dmc.Anchor(
                        href=f"/station/{sid}",
                        underline=False,
                        children=dmc.Button("Dashboard", radius="md", size="xs"),
                    ),
                ],
            ),

            dmc.Divider(my="sm"),

            dmc.SimpleGrid(
                cols=3,
                children=[
                    metric_card("Temperature", temp,  "°C",   "#3b82f6"),
                    metric_card("Humidity",    hum,   "%",    "#14b8a6"),
                    metric_card("CO2",         co2,   " ppm", "#64748b"),
                    metric_card("O2",          o2,    "%",    "#06b6d4"),
                    metric_card("Light",       light, "%",    "#eab308"),
                ],
            ) if online else dmc.Text(
                f"Last seen: {format_last_seen(last_seen)}",
                c="dimmed",
                size="sm",
            ),
        ],
    )


def register_hub_callbacks(app):

    @app.callback(
        Output("hub-cards", "children"),
        Input("hub-interval", "n_intervals"),
    )
    def update_hub(_):
        now = datetime.now()
        with STATION_LOCK:
            stations = dict(STATIONS)

        if not stations:
            return dmc.Text("No stations connected yet.", c="dimmed")

        return [station_card(sid, station, now) for sid, station in stations.items()]