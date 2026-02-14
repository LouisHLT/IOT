
# from dash import dcc, html
# from config import UPDATE_MS

# def build_layout():
#     return html.Div([
#         html.H2("Dashboard Arduino – Environnement"),
#         dcc.Dropdown(
#             id="station-selector",
#             placeholder="Select a station",
#             clearable=False,
#         ),

#         html.Div(id="device-info", style={"padding": "10px", "fontWeight": "bold", "fontSize": "16px"}),

#         html.Div([
#             html.Div(id="value-temp", style={"padding": "10px"}),
#             html.Div(id="value-hum", style={"padding": "10px"}),
#             html.Div(id="value-co2", style={"padding": "10px"}),
#             html.Div(id="value-o2", style={"padding": "10px"}),
#             html.Div(id="value-light",style={"padding": "10px"}),
#         ], style={"display": "flex", "flexWrap": "wrap"}),

#         dcc.Graph(id="graph-temp"),
#         dcc.Graph(id="graph-gas"),
#         dcc.Graph(id="graph-humidity"),
#         dcc.Graph(id="graph-light"),

#         dcc.Interval(
#             id="interval-component",
#             interval=UPDATE_MS,
#             n_intervals=0
#         )
#     ])

from dash import dcc, html
import dash_mantine_components as dmc

from config import UPDATE_MS

def build_layout():
    return dmc.Container(
        size=1200,
        px=24,
        py=32,
        children=[

            # ======================
            # HEADER
            # ======================
            dmc.Stack(
                spacing="xs",
                mb="lg",
                children=[
                    dmc.Title("Environment Dashboard", order=2),
                    dmc.Text(
                        "Live data from connected weather stations",
                        size="sm",
                        color="dimmed",
                    ),
                ],
            ),

            # ======================
            # CONTROLS
            # ======================
            dmc.Group(
                mb="lg",
                children=[
                    dcc.Dropdown(
                        id="station-selector",
                        placeholder="Select a station",
                        clearable=False,
                        style={"minWidth": 280},
                    ),
                ],
            ),

            # ======================
            # KPI CARDS
            # ======================
            dmc.SimpleGrid(
                # cols={"base": 2, "md": 5},
                cols=2,
                spacing="md",
                mb="xl",
                children=[
                    dmc.Card(id="value-temp", withBorder=True, radius="md", p="md"),
                    dmc.Card(id="value-hum", withBorder=True, radius="md", p="md"),
                    dmc.Card(id="value-co2", withBorder=True, radius="md", p="md"),
                    dmc.Card(id="value-o2", withBorder=True, radius="md", p="md"),
                    dmc.Card(id="value-light", withBorder=True, radius="md", p="md"),
                ],
            ),

            # ======================
            # CHARTS
            # ======================
            dmc.Grid(
                gutter="md",
                children=[
                    dmc.Col(
                        span={"base": 12, "md": 6},
                        children=dmc.Card(
                            withBorder=True,
                            radius="md",
                            p="md",
                            children=dcc.Graph(
                                id="graph-temp",
                                config={"displayModeBar": False},
                            ),
                        ),
                    ),
                    dmc.Col(
                        span={"base": 12, "md": 6},
                        children=dmc.Card(
                            withBorder=True,
                            radius="md",
                            p="md",
                            children=dcc.Graph(
                                id="graph-gas",
                                config={"displayModeBar": False},
                            ),
                        ),
                    ),
                    dmc.Col(
                        span={"base": 12, "md": 6},
                        children=dmc.Card(
                            withBorder=True,
                            radius="md",
                            p="md",
                            children=dcc.Graph(
                                id="graph-humidity",
                                config={"displayModeBar": False},
                            ),
                        ),
                    ),
                    dmc.Col(
                        span={"base": 12, "md": 6},
                        children=dmc.Card(
                            withBorder=True,
                            radius="md",
                            p="md",
                            children=dcc.Graph(
                                id="graph-light",
                                config={"displayModeBar": False},
                            ),
                        ),
                    ),
                ],
            ),

            # ======================
            # INTERVAL
            # ======================
            dcc.Interval(
                id="interval-component",
                interval=UPDATE_MS,
                n_intervals=0,
            ),
        ],
    )
