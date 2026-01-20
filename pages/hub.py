from dash import html, dcc, Input, Output
from datetime import datetime
import dash_mantine_components as dmc

from utils.utils import format_last_seen
from config import STATIONS, STATION_LOCK


OFFLINE_AFTER_SEC = 3.5  # tweak later

def hub_layout():
    return dmc.Container(
        [
            dmc.Group(
                justify="space-between",
                align="center",
                mb="xl",
                children=[
                    dmc.Title(
                        children=[
                            html.Span("Weather Station - ", style={"color": "#595a5c", "fontFamily": "Helvetica"}),
                            html.Span("HUB", style={"color": "#d14024", "fontFamily": "Helvetica"}),
                        ],
                        order=2,
                    ),
                dmc.Space(h=30),
                    dmc.Text("Live overview", size="sm", c="dimmed")
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
    return dmc.Card(
        withBorder=True,
        radius="md",
        p="sm",
        style={
            "borderLeft": f"4px solid {accent}",
            "transition": "transform 120ms ease",
        },
        children=[
            dmc.Stack(
                gap=2,
                children=[
                    dmc.Text(label, size="xs", c="dimmed"),
                    dmc.Text(
                        f"{value}{unit}" if value is not None else "—",
                        size="xl",
                        fw=700,
                    ),
                ],
            )
        ],
    )

def station_card(sid, station, now):
    last_seen = station.get("last_seen")
    online = last_seen and (now - last_seen).total_seconds() < OFFLINE_AFTER_SEC

    temp = station["temp"][-1] if station["temp"] else None
    hum = station["hum"][-1] if station["hum"] else None
    co2 = station["co2"][-1] if station["co2"] else None
    o2 = station["o2"][-1] if station["o2"] else None
    light = station["light"][-1] if station["light"] else None

    return dmc.Card(
        withBorder=True,
        radius="lg",
        px=24,
        py=20,
        shadow="sm",
        children=[
            # ---- HEADER ----
            dmc.Group(
                justify="space-between",
                mb="sm",
                children=[
                    dmc.Group(
                        gap="sm",
                        children=[
                            dmc.Text(f"Station {sid}", fw=600),
                            dmc.Badge(
                                "ONLINE" if online else "OFFLINE",
                                color="green" if online else "red",
                                variant="light",
                            ),
                            dmc.Group(
                                gap=4,
                                children=[
                                    dmc.Loader(size=8, color="green"),
                                    dmc.Text("Live", size="xs", c="dimmed"),
                                ],
                            ) if online else None,
                        ],
                    ),
                    dmc.Anchor(
                        href=f"/station/{sid}",
                        underline=False,
                        children=dmc.Button(
                            "Dashboard",
                            radius="md",
                            size="xs",
                        ),
                    ),
                ],
            ),

            dmc.Divider(my="sm"),

            # ---- BODY ----
            dmc.Grid(
                align="center",
                children=[
                    # ICON COLUMN
                    dmc.GridCol(
                        span={"base": 12, "md": 3},
                        children=dmc.Center(
                            html.Img(
                                src="/assets/weather_stt_icon_nbg.png",
                                style={
                                    "height": "130px",
                                    "filter": "drop-shadow(0 4px 6px rgba(0,0,0,.15))",
                                },
                            )
                        ),
                    ),

                    # METRICS
                    dmc.GridCol(
                        span={"base": 12, "md": 9},
                        children=(
                            dmc.SimpleGrid(
                                cols={"base": 2, "lg": 3},
                                spacing="md",
                                children=[
                                    metric_card("Temperature", f"{temp:.1f}", "°C", "#3b82f6"),
                                    metric_card("Humidity", f"{hum:.1f}", "%", "#14b8a6"),
                                    metric_card("CO₂", f"{co2:.0f}", " ppm", "#64748b"),
                                    metric_card("O₂", f"{o2:.1f}", "%", "#06b6d4"),
                                    metric_card("Light", f"{light:.1f}", "%", "#eab308"),
                                ],
                            )
                            if online
                            else dmc.Text(
                                f"Last seen: {format_last_seen(last_seen)}",
                                c="dimmed",
                                size="sm",
                            )
                        ),
                    ),
                ],
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
            stations = STATIONS.copy()

        if not stations:
            return dmc.Text("No stations connected.", c="dimmed")

        return dmc.Stack(
            gap="md",
            children=[
                station_card(sid, station, now)
                for sid, station in stations.items()
            ],
        )