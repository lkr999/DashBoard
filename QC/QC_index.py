import colorsys

import dash
from dash import Input, Output, State, html, dcc, dash_table, MATCH, ALL, ctx
import dash_mantine_components as dmc
from dash_iconify import DashIconify
import plotly.graph_objects as go
from datetime import datetime, time, timedelta
from datetime import date
import time as time_pck
import os
import dash_daq as daq

from DashBoard.QC.app import qc_app
import pages

server = qc_app.server

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
                    style={'margin-left':10,}
                ),
                dmc.Text(label, size="sm", color="white", style={'font-family':'IntegralCF-Regular'}),
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
                dmc.Text(label, size="sm", color="white", style={'font-family':'IntegralCF-Regular'}),
            ]
        ),
        href=href,
        style={"textDecoration": "none"},
    )

Period_radio_data = ['Daily', 'Weekly', 'Monthly', 'Quarterly']
Unit_radio_data = ['Qty_sqm','Qty_pcs','Qty_pt']


#analytics = dash_user_analytics.DashUserAnalytics(app, automatic_routing=False)
qc_app.layout = dmc.MantineProvider(
    id = 'dark-moder2',
    theme={"colorScheme": "dark"},
    inherit=True,
    withNormalizeCSS=True,
    withGlobalStyles=True,
    children = [

        dmc.Title(children='G Factory Dash Board', order=1, style={'font-family': 'IntegralCF-ExtraBold', 'text-align': 'center', 'color': 'black', 'background-color': 'skyblue'}),
        html.Div(
            children = [

                dmc.Modal(
                    opened = False
                ),

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

                                #html.Img(src='https://plotly.chiefs.work/ticketing/assets/SA.svg', id  = 'sa-logo', style={'width':160, 'margin-left':50}),
                                dmc.Divider(label='Exploration', style={"marginBottom": 10, "marginTop": 10, "color":'orange'}),
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
                                        dmc.Divider(label='QC Page',size=5,color='orange', variant='solid', style={'width':250,"marginBottom": 5, "marginTop": 5, "color": 'orange'}),

                                        create_main_nav_link(
                                            icon="carbon:inspection",
                                            label="Takeoff Inspection Status",
                                            href=qc_app.get_relative_path("/"),
                                        ),
                                        create_main_nav_link(
                                            icon="carbon:accessibility-alt",
                                            label="Board Quality",
                                            href=qc_app.get_relative_path("/qc_property"),
                                        ),

                                        dmc.Divider(label='Logistic Page',color='orange', size=5, variant='solid', style={'width':250, "marginBottom": 5, "marginTop": 5}),
                                        create_main_nav_link(
                                            icon="bi:dash",
                                            label="Board Inventory Status",
                                            href=qc_app.get_relative_path("/board_status"),
                                        ),
                                    ],
                                ),

                                #Base Date of Inventory ----
                                dmc.Divider(label='Base Date',labelPosition='center' ,color='white',size=5, style={"marginBottom": 10, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.Switch(
                                            id='oneday_range',
                                            radius="xs",
                                            label="One day as Date Range",
                                            checked=True
                                        ),
                                        dmc.DatePicker(
                                            id="baseInventory_date",
                                            # label="Start Date",
                                            # description="You can also provide a description",
                                            # minDate=date(2022, 1, 1),
                                            value=datetime.now().date(),
                                            style={"width": 250},
                                        ),

                                    ],
                                ),

                                # Date Range ----
                                dmc.Divider(label='Date Range',labelPosition='center' ,color='white',size=5, style={"marginBottom": 10, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.DateRangePicker(
                                            id="date_range",
                                            # minDate=date(2023, 1, 1),
                                            # value=[date(datetime.now().year,datetime.now().month,1), datetime.now().date()], # + timedelta(days=5)
                                            value=[date(datetime.now().date().year, datetime.now().date().month, 1), datetime.now().date()],  # + timedelta(days=5)
                                            style={"width": 250},
                                        ),
                                    ],
                                ),

                                #Period ----
                                dmc.Divider(label='Period Select',labelPosition='center' ,color='white',size=5, style={"marginBottom": 0, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.RadioGroup(
                                            [dmc.Radio(k,value=k) for k in Period_radio_data],
                                            id="radio_period",
                                            value="Daily",
                                            # label="Select your favorite framework/library",
                                            size='sm',
                                            mt='xs', style={'width': 250},
                                        ),
                                    ],
                                ),

                                #Board Level Select ----
                                dmc.Divider(label='Evaluate Select',labelPosition='center' ,color='white',size=5, style={"marginBottom": 10, "marginTop": 30}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.ChipGroup(
                                            [dmc.Chip(x, value=x, variant="outline",) for x in ['G','G2','G3','S','NG','X']],
                                            id="chip_evaluate",
                                            value=['G','G2','G3','S','NG','X'],
                                            multiple=True, mb=10,
                                        ),
                                    ],
                                ),

                                #Board Units ----
                                dmc.Divider(label='Units of Board',labelPosition='center' ,color='white',size=5, style={"marginBottom": 0, "marginTop": 20}),
                                dmc.Group(
                                    display="column",
                                    children=[
                                        dmc.RadioGroup(
                                            [dmc.Radio(k, value=k) for k in Unit_radio_data],
                                            id="unit_Analyze",
                                            value="Qty_sqm",
                                            # label="Select your favorite framework/library",
                                            size='xs',
                                            mt='xs', style={"width": 280, "marginBottom": 10},

                                        ),
                                    ],
                                ),

                                #Board Level ----
                                dmc.Divider(label='Board Level',labelPosition='center' ,color='white',size=5, style={"marginBottom": 0, "marginTop": 20}),
                                dmc.Group(
                                    children=[
                                        dmc.ChipGroup(
                                            [dmc.Chip(x, value=x, variant="outline", ) for x in ['LV_1', 'LV_2', 'LV_3', 'Cut']],
                                            id="level_checkList",
                                            value=['LV_1', 'LV_2', 'LV_3', 'Cut'],
                                            multiple=True, mb=10,
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

@qc_app.callback(Output('content', 'children'),
                [Input('url', 'pathname')])
def display_content(pathname):
    page_name = qc_app.strip_relative_path(pathname)
    print('CHK ok:', pathname)
    if not page_name:  # None or ''
        # return pages.Board_Status_tmp.layout
        return pages.qc_takeoff.layout
    elif pathname=='/qc_takeoff/qc_property':
        return pages.qc_property.layout
    # elif pathname=='/qc_takeoff/board_status':
    #     return pages.board_status.layout
    else: return pages.qc_takeoff.layout


if __name__ == '__main__':
    # qc_app.run_server(debug=True)
    qc_app.run_server(debug=False, host='10.50.3.152', port=61024)
