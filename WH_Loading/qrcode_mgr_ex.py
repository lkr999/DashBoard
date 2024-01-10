import dash_qr_manager as dqm
import dash
from dash.dependencies import Input, Output
import dash_html_components as html

app = dash.Dash(__name__)

app.run_server(debug=False, host='10.50.3.152', port=59280)