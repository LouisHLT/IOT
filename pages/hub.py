from dash import html, dcc
from datetime import datetime
import dash_mantine_components as dmc

from utils.utils import format_last_seen
from config import STATIONS, STATION_LOCK


OFFLINE_AFTER_SEC = 10  # tweak later


def hub_layout():
    now = datetime.now()

    with STATION_LOCK:
        stations = STATIONS.copy()

    return dmc.Container(
        [
            # ---- TITLE ----
            dmc.Title(
                children=[
                    html.Span("Weather Station - ", style={"color": "#595a5c", "fontFamily": "Helvetica"}),
                    html.Span("HUB", style={"color": "#d14024", "fontFamily": "Helvetica"}),
                ],
                order=2,
            ),
            dmc.Space(h=30),

            # ---- STATION CARDS ----
            dmc.Stack(
                gap="md",
                children=[
                    station_card(sid, station, now)
                    for sid, station in stations.items()
                ],
            ),
        ],
        size="xl",
        pt="xl",
    )


def station_card(sid, station, now):
    last_seen = station.get("last_seen")

    online = (
        last_seen is not None
        and (now - last_seen).total_seconds() < OFFLINE_AFTER_SEC
    )

    # Latest values (safe)
    temp = station["temp"][-1] if station["temp"] else None
    hum = station["hum"][-1] if station["hum"] else None
    o2 = station["o2"][-1] if station["o2"] else None
    co2 = station["co2"][-1] if station["co2"] else None
    light = station["light"][-1] if station["light"] else None

    return dmc.Card(
        withBorder=True,
        radius="md",
        p="lg",
        children=[
            dmc.Group(
                justify="space-between",
                align="center",
                children=[
                    # ---- LEFT ICON ----
                    html.Img(src="/assets/weather_stt_icon_nbg.png", style={"width": "54px", "height": "113px"}),

                    # ---- CENTER INFO ----
                    dmc.Stack(
                        gap=6,
                        children=[
                            dmc.Group(
                                gap="md",
                                children=[
                                    dmc.Text(f"Station ID: {sid}", fw=600),
                                    dmc.Badge(
                                        "ONLINE" if online else "OFFLINE",
                                        c="green" if online else "red",
                                        variant="light",
                                    ),
                                ],
                            ),

                            dmc.SimpleGrid(
                                cols={"base": 1, "sm": 2, "md": 3, "lg": 5},
                                spacing="xs",
                                children=[
                                    dmc.Text(f"Temperature (°C): {temp:.1f}", size="sm", c="black"),
                                    dmc.Text(f"Humidity (%): {hum:.1f}", size="sm", c="black"),
                                    dmc.Text(f"O2 (%): {o2:.1f}", size="sm", c="black"),
                                    dmc.Text(f"CO2 (ppm): {co2:.0f}", size="sm", c="black"),
                                    dmc.Text(f"Light (%): {light:.1f}", size="sm", c="black"),
                                ]
                            ) if online else dmc.Text(
                                f"Last seen: {format_last_seen(last_seen)}",
                                size="sm",
                                c="black",
                            ),
                        ],
                    ),

                    # ---- RIGHT BUTTON ----
                    dmc.Anchor(
                        href=f"/station/{sid}",
                        underline=False,
                        children=[
                            dmc.Button(
                                "Dashboard",
                                radius="md",
                            )
                        ],
                    )
                ],
            ),
        ],
        style={
            "minHeight": "157px",
            "backgroundColor": "#e9e9e9",
            "border": "1px solid black",
        },
    )

