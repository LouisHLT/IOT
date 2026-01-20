import sys
import threading
from dash import Dash

from api_reader import http_reader
import dashboard.layout as lyt
import dashboard.callbacks as clbk

t = threading.Thread(target=http_reader, daemon=True)
t.start()

app = Dash(__name__)
app.layout = lyt.build_layout()
clbk.register_callbacks(app)

debug_mode = True
if len(sys.argv) > 1:
    arg = sys.argv[1].lower()
    if arg in ['-false', 'false', '0']:
        debug_mode = False
    elif arg in ['-true', 'true', '1']:
        debug_mode = True

if __name__ == "__main__":
    app.run(debug=debug_mode)