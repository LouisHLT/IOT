import sys
import threading
import dash_mantine_components as dmc
from dash import Dash, dcc, html, Input, Output

from api_reader import http_reader
import dashboard.layout as lyt
import dashboard.callbacks as clbk

from api_reader import http_reader
from pages.hub import hub_layout
from pages.station import station_layout

t = threading.Thread(target=http_reader, daemon=True)
t.start()

app = Dash(__name__)

app.layout = dmc.MantineProvider(
    children=[
        dcc.Location(id="url", refresh=False),
        html.Div(id="page-content")
    ]
)

@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname in ["/", "/hub"]:
        return hub_layout()

    if pathname.startswith("/station/"):
        station_id = pathname.split("/station/")[1]
        return station_layout(station_id)

    return html.H3("404 – Page not found")


debug_mode = True
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    if arg in ['-false', 'false', '0']:
        debug_mode = False
    elif arg in ['-true', 'true', '1']:
        debug_mode = True

if __name__ == "__main__":
    app.run(debug=debug_mode)