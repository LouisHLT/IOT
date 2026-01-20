from dash import Input, Output

import dashboard.figures as fig
from utils.utils import empty_dashboard, format_last_seen
from config import STATIONS, STATION_LOCK

def register_callbacks(app):
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
        temp_fig = fig.get_temperature_figure(x, temp)
        gas_fig = fig.get_gas_figure(x, co2, o2)
        hum_fig = fig.get_humidity_figure(x, hum)
        light_fig = fig.get_light_figure(x, light)

        # -------- LAST VALUES --------
        last_seen_str = format_last_seen(station["last_seen"])

        return (
            f"Station ID: {selected_sid} | Last seen: {last_seen_str}",
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