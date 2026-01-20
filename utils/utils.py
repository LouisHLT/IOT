import plotly.graph_objects as go


def empty_dashboard():
    """ 
        Returns empty values and figures for the dashboard when no data is available.

        Returns:
            A tuple containing empty strings and empty figures. 
    """
    empty_text = "waiting for datas..."
    empty_fig = go.Figure()
    return (empty_text, empty_text, empty_text, empty_text, empty_text, empty_text,
            empty_fig, empty_fig, empty_fig, empty_fig)

def format_last_seen(dt):
    if dt is None:
        return "never"
    return dt.strftime("%H:%M:%S %d/%m/%Y")
