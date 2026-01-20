import plotly.graph_objects as go


def get_temperature_figure(x, temp):
    temp_fig = go.Figure()
    temp_fig.add_trace(go.Scatter(x=x, y=temp, mode="lines", name="Temp (°C)"))
    temp_fig.update_layout(
        title="Temperature",
        xaxis_title="Time",
        yaxis_title="Temp (°C)",
    )
    return temp_fig

def get_gas_figure(x, co2, o2):
    gas_fig = go.Figure()
    gas_fig.add_trace(go.Scatter(x=x, y=co2, mode="lines", name="CO2 ppm"))
    gas_fig.add_trace(go.Scatter(x=x, y=o2, mode="lines", name="O2 %", yaxis="y2"))
    gas_fig.update_layout(
        title="O2 / CO2",
        xaxis_title="Time",
        yaxis=dict(title="CO2 (ppm)"),
        yaxis2=dict(title="O2 (%)", overlaying="y", side="right"),
    )
    return gas_fig

def get_humidity_figure(x, hum):
    hum_fig = go.Figure()
    hum_fig.add_trace(go.Scatter(x=x, y=hum, mode="lines", name="Humidity"))
    hum_fig.update_layout(
        title="Humidity",
        xaxis_title="Time",
        yaxis_title="Humidity (%)",
    )
    return hum_fig

def get_light_figure(x, light):
    light_fig = go.Figure()
    light_fig.add_trace(go.Scatter(x=x, y=light, mode="lines", name="Light"))
    light_fig.update_layout(
        title="Light",
        xaxis_title="Time",
        yaxis_title="Light (%)",
    )
    return light_fig