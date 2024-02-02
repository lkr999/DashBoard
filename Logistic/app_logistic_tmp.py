import dash
#from scout_apm.flask import ScoutApm

app_logistic = dash.Dash(__name__, suppress_callback_exceptions = True,  url_base_pathname='/logistic_analyze_01/',
    title = 'Logistic Analyze',
    #update_title=None,
    meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1"}],
)


