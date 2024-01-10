import dash
from dash import Input, Output, State, html, dcc, dash_table, MATCH, ALL, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
from datetime import date

from DashBoard.Logistic_Local.app import logistic_app
import pages

server = logistic_app.server

def create_main_nav_link(icon, label, href):
    return dcc.Link(
        dmc.Group(
            display='row',
            position='center',
            spacing=10,
            style={'margin-bottom':5},
            children=[
                dmc.ThemeIcon(
                    DashIconify(icon=icon, width=18),
                    size=25,
                    radius=5,
                    color='indigo',
                    variant="filled",
                    style={'margin-left':10}
                ),
                dmc.Text(label, size="sm", color="gray", style={'font-family':'IntegralCF-Regular'}),
            ]
        ),
        href=href,
        style={"textDecoration": "none"},
    )

def create_accordianitem(icon, label, href):
    return dcc.Link(
        dmc.Group(
            direction='row',
            position='left',
            spacing=10,
            style={'margin-bottom':10},
            children=[
                dmc.ThemeIcon(
                    DashIconify(icon=icon, width=18),
                    size=30,
                    radius=30,
                    color='indigo',
                    variant="light",
                ),
                dmc.Text(label, size="sm", color="gray", style={'font-family':'IntegralCF-Regular'}),
            ]
        ),
        href=href,
        style={"textDecoration": "none"},
    )

Period_radio_data = ['Daily', 'Weekly', 'Monthly', 'Quarterly','Yearly']
Unit_radio_data = ['Qty_sqm', 'Qty_pcs', 'Qty_pt']

logistic_app.layout = dmc.MantineProvider(
    id = 'dark-moder',
    withGlobalStyles=False,
    children = [
        # dmc.Header(height=50, children=[dmc.Text("Logistic Analyze")], style={'font-size':30, 'font-family': 'IntegralCF-ExtraBold', 'text-align': 'center', 'color': 'slategray', 'background-color': 'skyblue'}),
        dmc.Title(children='G Factory Logistic Status', order=1, style={'font-family': 'IntegralCF-ExtraBold', 'text-align': 'center', 'color': 'slategray', 'background-color': 'skyblue'}),
        # dmc.Divider(label = 'Overview',  labelPosition='center', size='xl'),
        html.Div(
            children = [

                dmc.Navbar(
                    fixed=True, top=50,
                    width={"base": 300},
                    pl='sm',
                    pr='xs',
                    pt=0,
                    hidden=True,
                    hiddenBreakpoint='sm',
                    children=[
                        dmc.ScrollArea(
                            offsetScrollbars=True,
                            type="scroll",
                            children=[
                                dmc.Divider(label='Exploration', style={"marginBottom": 20, "marginTop": 5}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.Button(
                                            "Refresh",
                                            id='refresh',
                                            variant="outline",
                                            leftIcon=DashIconify(icon="material-symbols:refresh"),
                                            style={"width": 250, "marginBottom": 10, "marginTop": 10},
                                        ),
                                        create_main_nav_link(
                                            icon="icon-park:ad-product",
                                            label="Board Status",
                                            href=logistic_app.get_relative_path("/"),
                                        ),
                                        create_main_nav_link(
                                            icon="carbon:accessibility-alt",
                                            label="Material Status",
                                            href=logistic_app.get_relative_path("/Material_Status"),
                                        ),

                                    ],
                                ),

                                #Base Date of Inventory ----
                                dmc.Divider(label='Base Date of Inventory', style={"marginBottom": 10, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.Switch(
                                            id='oneday_range',
                                            radius="xs",
                                            label="One day as Date Range",
                                            checked=False
                                        ),
                                        dmc.DatePicker(
                                            id="baseInventory_date",
                                            # label="Start Date",
                                            # description="You can also provide a description",
                                            minDate=date(2022, 1, 1),
                                            value=datetime.now().date(),
                                            style={"width": 250},
                                        ),

                                    ],
                                ),

                                #Date Range ----
                                dmc.Divider(label='Date Range', style={"marginBottom": 10, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.DateRangePicker(
                                            id="date_range",
                                            # label="Date Range",
                                            # description="You can also provide a description",
                                            # minDate=date(2023, 1, 1),
                                            value=[date(datetime.now().year,datetime.now().month,1), datetime.now().date()], # + timedelta(days=5)
                                            style={"width": 250},
                                        ),
                                    ],
                                ),

                                #Period ----
                                dmc.Divider(label='Period Select', style={"marginBottom": 0, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.RadioGroup(
                                            [dmc.Radio(k,value=k) for k in Period_radio_data],
                                            id="radio_period",
                                            value="Daily",
                                            # label="Select your favorite framework/library",
                                            size="sm",
                                            mt=10, style={'width': 280},
                                        ),
                                    ],
                                ),

                                #Board Level Select ----
                                dmc.Divider(label='Board Level Select', style={"marginBottom": 10, "marginTop": 30}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.ChipGroup(
                                            [dmc.Chip(x, value=x, variant="outline", ) for x in ['LV_1', 'LV_2', 'LV_3', 'Cut']],
                                            id="level_checkList",
                                            value=['LV_1', 'LV_2', 'LV_3', 'Cut'],
                                            multiple=True, mb=10,
                                        ),

                                    ],
                                ),

                                #Board Units ----
                                dmc.Divider(label='Units of Board', style={"marginBottom": 0, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.RadioGroup(
                                            [dmc.Radio(k, value=k) for k in Unit_radio_data],
                                            id="unit_Analyze",
                                            value="Qty_sqm",
                                            # label="Select your favorite framework/library",
                                            size='sm',
                                            mt=10, style={"width": 280, "marginBottom": 10},
                                        ),
                                    ],
                                ),

                            ],

                        )
                    ],
                ),

                dcc.Location(id='url'),
                dmc.MediaQuery(
                    largerThan= "xs",
                    styles={'height':'100%', 'margin-left':'300px', 'margin-top':10},
                    children = [
                        html.Div(
                            id='content',
                            style={'margin-top':'10px'}
                        )
                    ],
                ),

            ]
        )
    ]
)
@logistic_app.callback(
    Output('content', 'children'),
    Input('url', 'pathname'),
)
def display_update(pathname):
    page_name = logistic_app.strip_relative_path(pathname)
    print('CHK ok:', pathname, page_name)
    if not page_name:  # None or ''
        return pages.Board_Status.layout
    if pathname=='/logistic_analyze_01/Material_Status':
        return pages.Material_Status.layout
    else: return pages.Board_Status.layout


if __name__ == '__main__':
    logistic_app.run_server(debug=True)
    # logistic_app.run_server(debug=False, host='10.50.3.152', port=56032)
