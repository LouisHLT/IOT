import sys
import threading
import dash
dash._dash_renderer._set_react_version('18.2.0')

import dash_mantine_components as dmc
from dash import Dash, dcc, html, Input, Output

from pages.hub import hub_layout, register_hub_callbacks
from pages.station import station_layout, register_station_callbacks
from get_server import ingest_app


def run_ingest():
    print("[INGEST] Flask starting on 0.0.0.0:5050", flush=True)
    ingest_app.run(host="0.0.0.0", port=5050, debug=False, use_reloader=False)

t = threading.Thread(target=run_ingest, daemon=True)
t.start()

app = Dash(__name__, suppress_callback_exceptions=True)

register_hub_callbacks(app)
register_station_callbacks(app)

app.layout = dmc.MantineProvider(
    children=[
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content"),
    ]
)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    print(f"[ROUTING] pathname={repr(pathname)}", flush=True)
    if not pathname or pathname in ["/", "/hub"]:
        return hub_layout()
    if pathname.startswith("/station/"):
        station_id = pathname.split("/station/")[1]
        return station_layout(station_id)
    return html.H3(f"404 - not found: {pathname}")


if __name__ == "__main__":
    debug_mode = False  # default to False since True breaks the Flask thread
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['-true', 'true', '1']:
            debug_mode = True
        elif arg in ['-false', 'false', '0']:
            debug_mode = False

    app.run(host="0.0.0.0", debug=debug_mode, use_reloader=False)