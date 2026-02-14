from dash import dcc, html, Input, Output
import dash_mantine_components as dmc
from dash.exceptions import PreventUpdate

from config import STATIONS, STATION_LOCK
import dashboard.figures as figs


def kpi_card(label, value, unit, accent, id=None):
    return dmc.Card(
        withBorder=True,
        radius="md",
        p="md",
        style={"borderTop": f"4px solid {accent}"},
        children=[
            dmc.Text(label, size="xs", c="dimmed"),
            dmc.Text(f"{value}{unit}", size="xl", fw=700, id=id),
        ],
    )


def station_layout(station_id):
    return dmc.Container(
        size=1200,
        px=24,
        py=32,
        children=[
            dcc.Store(id="station-id-store", data=station_id),
            dcc.Interval(id="station-interval", interval=1000, n_intervals=0),

            dmc.Stack(
                gap="md",
                mb="xl",
                children=[
                    dmc.Anchor(
                        href="/hub",
                        underline=False,
                        children=dmc.Button(
                            "← Back to hub",
                            variant="subtle",
                            color="gray",
                            size="sm",
                            radius="md",
                        ),
                    ),
                    dmc.Title(f"Station {station_id}", order=2),
                ],
            ),

            dmc.SimpleGrid(
                cols=5,
                mb="xl",
                children=[
                    kpi_card("Temperature", "—", "°C",   "#3b82f6", id="station-value-temp"),
                    kpi_card("Humidity",    "—", "%",    "#14b8a6", id="station-value-hum"),
                    kpi_card("O2",          "—", "%",    "#06b6d4", id="station-value-o2"),
                    kpi_card("CO2",         "—", " ppm", "#64748b", id="station-value-co2"),
                    kpi_card("Light",       "—", "%",    "#eab308", id="station-value-light"),
                ],
            ),

            dmc.Grid(
                gutter="md",
                children=[
                    dmc.GridCol(span=6, children=dmc.Card(withBorder=True, p="md", children=dcc.Graph(id="station-temp-graph"))),
                    dmc.GridCol(span=6, children=dmc.Card(withBorder=True, p="md", children=dcc.Graph(id="station-gas-graph"))),
                    dmc.GridCol(span=6, children=dmc.Card(withBorder=True, p="md", children=dcc.Graph(id="station-humidity-graph"))),
                    dmc.GridCol(span=6, children=dmc.Card(withBorder=True, p="md", children=dcc.Graph(id="station-light-graph"))),
                ],
            ),
        ],
    )


def register_station_callbacks(app):

    @app.callback(
        [
            Output("station-value-temp",     "children"),
            Output("station-value-hum",      "children"),
            Output("station-value-o2",       "children"),
            Output("station-value-co2",      "children"),
            Output("station-value-light",    "children"),
            Output("station-temp-graph",     "figure"),
            Output("station-gas-graph",      "figure"),
            Output("station-humidity-graph", "figure"),
            Output("station-light-graph",    "figure"),
        ],
        Input("station-interval", "n_intervals"),
        Input("station-id-store", "data"),
    )
    def update_station(_, station_id):
        print(f"[STATION CB] id={repr(station_id)} keys={list(STATIONS.keys())}", flush=True)

        with STATION_LOCK:
            station = STATIONS.get(station_id)

        if not station or not station["temp"]:
            raise PreventUpdate

        x     = list(station["timestamps"])
        temp  = list(station["temp"])
        hum   = list(station["hum"])
        co2   = list(station["co2"])
        o2    = list(station["o2"])
        light = list(station["light"])

        return (
            f"{temp[-1]:.1f}",
            f"{hum[-1]:.1f}",
            f"{o2[-1]:.1f}",
            f"{co2[-1]:.0f}",
            f"{light[-1]:.1f}",
            figs.get_temperature_figure(x, temp),
            figs.get_gas_figure(x, co2, o2),
            figs.get_humidity_figure(x, hum),
            figs.get_light_figure(x, light),
        )