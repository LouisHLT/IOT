from dash import dcc, html

from config import STATIONS, STATION_LOCK
import dashboard.figures as figs


def station_layout(station_id):
    with STATION_LOCK:
        station = STATIONS.get(station_id)

    if not station:
        return html.Div([
            html.H3("Station not found"),
            html.A("← Back to hub", href="/hub")
        ])

    x = list(station["timestamps"])
    temp = list(station["temp"])
    co2 = list(station["co2"])
    o2 = list(station["o2"])
    humidity = list(station["hum"])
    light = list(station["light"])

    # Get the latest values (last element from each list)
    latest_temp = temp[-1] if temp else 0
    latest_hum = humidity[-1] if humidity else 0
    latest_o2 = o2[-1] if o2 else 0
    latest_co2 = co2[-1] if co2 else 0
    latest_light = light[-1] if light else 0

    return html.Div([
        html.A("← Back to hub", href="/hub"),
        html.H2(f"Station: {station_id}"),

        html.Div([
            html.P(f"Temperature (°C): {latest_temp:.1f}", style={'display': 'inline-block', 'margin': '0 15px'}),
            html.P(f"Humidity (%): {latest_hum:.1f}", style={'display': 'inline-block', 'margin': '0 15px'}),
            html.P(f"O2 (%): {latest_o2:.1f}", style={'display': 'inline-block', 'margin': '0 15px'}),
            html.P(f"CO2 (ppm): {latest_co2:.0f}", style={'display': 'inline-block', 'margin': '0 15px'}),
            html.P(f"Light (%): {latest_light:.1f}", style={'display': 'inline-block', 'margin': '0 15px'}),
        ]),

        dcc.Graph(figure=figs.get_temperature_figure(x, temp), style={'height': '90vh'}),
        dcc.Graph(figure=figs.get_gas_figure(x, co2, o2), style={'height': '90vh'}),
        dcc.Graph(figure=figs.get_humidity_figure(x, humidity), style={'height': '90vh'}),
        dcc.Graph(figure=figs.get_light_figure(x, light), style={'height': '90vh'}),
    ], style={'width': '100%', 'margin': '0 auto'})
