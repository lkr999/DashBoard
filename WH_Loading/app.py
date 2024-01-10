import dash
#from scout_apm.flask import ScoutApm

wh_app = dash.Dash(__name__, suppress_callback_exceptions = True,  url_base_pathname='/wh_transfer/',
    title = 'Warehouse Transfer',
    #update_title=None, 
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)
