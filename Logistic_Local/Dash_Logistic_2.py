import dash
import flask
import numpy as np
import xlwings as xl
import dash_mantine_components as dmc

import plotly.express as px
import pandas as pd
import pymysql
import mariadb
import dash_pivottable
import mysql.connector
import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_ag_grid as dag

from dash_iconify import DashIconify
from datetime import date
from dash import Dash, Input, Output, ctx, dcc, html, dash_table
from sqlalchemy import create_engine
from pymsgbox import alert, confirm, password, prompt

HOST     = '10.50.3.163'
DB       = 'gfactoryDB'
USER = 'leekr'
PASSWORD = 'g1234'

NOW = datetime.datetime.now()
TODAY = datetime.date.today()

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

# Position Design -----------------
TOP_0 = 2500
TOP_1 = TOP_0 + 1100
TOP_2 = TOP_1 + 1100

LEFT_0 = 10
LEFT_1 = int(1900/4*1)
LEFT_2 = int(1900/4*2)
LEFT_3 = int(1900/4*3)

try:
    # self.conn = pymysql.connect(host='192.168.1.95', user=USER, password=PASSWORD, db='zeitgypsumdb', charset='utf8')
    pymysql.install_as_MySQLdb()
    engine = create_engine("mysql://{user}:{password}@{host}/{db}".format(user=USER, password=PASSWORD, host=HOST, db=DB))
    # conn = mysql.connector.connect(**config)
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8')

    cur = conn.cursor()
except mariadb.Error as e: alert(e)

application = flask.Flask(__name__)
# app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
logistic_app = dash.Dash(__name__, url_base_pathname='/logistic_analyze_01/')
logistic_app.title = "Logistic Analyze"

logistic_app.layout = dmc.MantineProvider(
    id = 'dark-moder',
    withGlobalStyles=True,
    children=[
        dmc.Title(children='Logistic Analyze', order=1, style={'font-family': 'IntegralCF-ExtraBold', 'text-align': 'center', 'color': 'slategray', 'background-color': 'skyblue'}),
        dmc.Divider(label = 'Overview',  labelPosition='center', size='xl'),
        dmc.Group(
            display ='column',
            grow=False,
            children=[
                # dmc.Space(),
                # dmc.Space(),
                dcc.Graph(id="indi_1",style={'width':200, 'height': 100}),
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'height': 100},
                    children = [
                        dmc.Text('Total Inventory', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='totalcust', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                        dmc.Text('Churn Rate', id='churn_rate', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                    ]
                ),
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'height': 100},
                    children = [
                        dmc.Text('Total Inventory2', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='totalcust2', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                        dmc.Text('Churn Rate', id='churn_rate2', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                    ]
                ),
                ]
        ),

        dmc.Divider(label = 'Inventory',  labelPosition='center', size='xl'),
        dmc.Title(children = 'Inventory Status', order = 3, style = {'font-family':'IntegralCF-ExtraBold', 'text-align':'center', 'color' :'slategray'}),
        dmc.Modal(
            id = 'info-ml',
            size = '75%',
            overflow="inside",
            title = [dmc.Title('Model Info', order = 3)],
            children = [
                dmc.Divider(label = 'AUC Curves and Model Performance', labelPosition = 'center'),
                dmc.SimpleGrid(
                    cols = 2,
                    children = [
                        dmc.Title('AUC - Original Data', order = 4, style = {'text-align':'center'}),
                        dmc.Title('AUC- Balanced Data', order = 4, style = {'text-align':'center'}),
                        html.Img(
                            src = logistic_app.get_asset_url('ml images/auc output.png'),
                            style = {'width':'25vw','justify-self':'center'},
                        ),
                        html.Img(
                            src = logistic_app.get_asset_url('ml images/auc balanced output.png'),
                            style = {'width':'25vw','justify-self':'center'}
                        ),
                        dmc.Text('We had a Yes-No ratio of approx. 4:1. This was the model generated with that data.', style= {'justify-self':'center'}),
                        dmc.Text('I balanced the Yes-No ratio to 1:1 with SMOTE. This is the new model. It performs better', style= {'justify-self':'center'}),
                    ]
                ),
                dmc.Divider(label = 'Confusion Matrix', labelPosition='center'),
                dmc.Stack(
                    align = 'center',
                    children = [
                        dmc.Title('Random Forest Confusion Matrix', order = 4, style = {'text-align':'center'}),
                        html.Img(
                            src = logistic_app.get_asset_url('ml images/confusion matrix rfc.png'),
                            style = {'width':'25vw','justify-self':'center'},
                        ),
                        dmc.Text('I choose the random forest classifier model from above. This is the confusion matrix for said model.', style = {'justify-self':'center'})
                    ]
                )
            ]
        ),

        dmc.Navbar(
            fixed=False,
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
                    top=0,
                    children=[
                        # dmc.Group(
                        #     display='column',
                        #     align='center',
                        #     position='center',
                        #     spacing='xs',
                        #     children=[
                        #         dmc.Text('Built By: Andrew Schutte', style={'font-family': 'IntegralCF-RegularOblique'}, size='sm'),
                        #         dmc.Text('Kansas City, USA', style={'font-family': 'IntegralCF-RegularOblique'}, size='sm')
                        #     ]
                        # ),

                        # html.Img(src='https://plotly.chiefs.work/ticketing/assets/SA.svg', id  = 'sa-logo', style={'width':160, 'margin-left':50}),
                        dmc.Divider(label='Customer Exploration', style={"marginBottom": 10, "marginTop": 10}),
                        dmc.Group(
                            display="column",
                            children=[
                                create_main_nav_link(
                                    icon="mdi:people-group",
                                    label="Inventory Status",
                                    href=logistic_app.get_relative_path("/"),
                                ),
                                create_main_nav_link(
                                    icon="mdi:magnify",
                                    label="Churn Investigation",
                                    href=logistic_app.get_relative_path("/churn"),
                                ),
                                create_main_nav_link(
                                    icon="ooui:text-summary-ltr",
                                    label="Churn Prediction",
                                    href=logistic_app.get_relative_path("/summary"),
                                ),
                            ],
                        ),
                        # dmc.Divider(label='Ticket Sales', style={"marginBottom": 15, "marginTop": 10}),

                        # dmc.Group(
                        #     direction="column",
                        #     children=[
                        #         create_main_nav_link(
                        #             icon="mdi:people-group",
                        #             label="Single Game Sales",
                        #             href=app.get_relative_path("/singlegame-sales"),
                        #         ),

                        #         create_main_nav_link(
                        #             icon="bi:people",
                        #             label="New Season Ticket Sales",
                        #             href=app.get_relative_path("/newstm-sales"),
                        #         ),

                        #         create_main_nav_link(
                        #             icon="fa:refresh",
                        #             label="Renewal",
                        #             href=app.get_relative_path("/renewal"),
                        #         ),
                        #         create_main_nav_link(
                        #             icon="material-symbols:sports-football-rounded",
                        #             label="Playoffs",
                        #             href=app.get_relative_path("/playoff_tickets"),
                        #         ),
                        #     ]
                        # ),

                        # dmc.Divider(style={"marginBottom": 0, "marginTop": 10}),

                        # dmc.Accordion(
                        #     #iconPosition='right',
                        #     multiple=True,
                        #     style={'font-family':'IntegralCF-Regular'},
                        #     children=[
                        #         dmc.AccordionItem(
                        #             icon=[DashIconify(icon='bi:people', width=18)],
                        #             label="Sales Rep Tracking",
                        #             children=[
                        #                 create_accordianitem(
                        #                     icon="iconoir:leaderboard-star",
                        #                     label="Sales Leaderboard",
                        #                     href=app.get_relative_path("/salesrep-leaderboard"),
                        #                 ),
                        #                 create_accordianitem(
                        #                     icon="iconoir:leaderboard-star",
                        #                     label="Deposit Leaderboard",
                        #                     href=app.get_relative_path("/salesrep-deposits"),
                        #                 ),
                        #             ]
                        #         ),
                        #         dmc.AccordionItem(
                        #             icon=[DashIconify(icon='bx:party', width=18)],
                        #             label="Season Ticket Member Events",
                        #             children=[

                        #                 create_accordianitem(
                        #                     icon="fa:refresh",
                        #                     label="Draft Fest",
                        #                     href=app.get_relative_path("/stmevents-draftfest"),
                        #                 ),

                        #                 create_accordianitem(
                        #                     icon="fluent:tent-16-filled",
                        #                     label="Training Camp",
                        #                     href=app.get_relative_path("/stmevents-training-camp"),
                        #                 ),

                        #             ]
                        #         ),
                        #         dmc.AccordionItem(
                        #             icon=[DashIconify(icon='bi:file-earmark-bar-graph', width=18)],
                        #             label="Reporting",
                        #             children=[
                        #                 create_accordianitem(
                        #                     icon="fa:refresh",
                        #                     label="Box Office",
                        #                     href=app.get_relative_path("/reporting-boxoffice"),
                        #                 ),
                        #             ]
                        #         ),
                        #     ],
                        # ),
                    ],
                )
            ],
        ),
        dcc.Location(id='url'),
        dmc.MediaQuery(
            largerThan="xs",
            styles={'height':'100%', 'margin-left':'300px', 'margin-top':70},
            children = [
                html.Div(
                    id='content',
                    style={'margin-top':'70px'}
                )
            ],
        ),


                                     # dmc.Group(
                #     direction='row',
                #     grow=True,
                #     children=[
                #         dmc.Paper(
                #             radius="md",  # or p=10 for border-radius of 10px
                #             withBorder=True,
                #             shadow='xs',
                #             p='sm',
                #             style={'height': '175px'},
                #             children=[
                #                 dmc.Center(
                #                     dmc.ThemeIcon(
                #                         size=50,
                #                         radius="xl",
                #                         color="violet",
                #                         variant="light",
                #                         children=[DashIconify(icon="fluent:people-community-20-filled", width=30)]
                #                     )
                #                 ),
                #                 dmc.Group(
                #                     direction='column',
                #                     position='center',
                #                     spacing='xs',
                #                     style={'margin-top': 10},
                #                     children=[
                #                         dmc.Text('Current Number of Customers', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                #                         dmc.Text(id='totalcust', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                #                         dmc.Text('Churn Rate', id='churn_rate', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                #                     ]
                #                 )
                #             ],
                #         ),
                #         dmc.Paper(
                #             radius="md",  # or p=10 for border-radius of 10px
                #             withBorder=True,
                #             shadow='xs',
                #             p='sm',
                #             style={'height': '175px'},
                #             children=[
                #                 dmc.Center(
                #                     dmc.ThemeIcon(
                #                         size=50,
                #                         radius="xl",
                #                         color="yellow",
                #                         variant="light",
                #                         children=[DashIconify(icon="mdi:recurring-payment", width=30)]
                #                     )
                #                 ),
                #                 dmc.Group(
                #                     direction='column',
                #                     position='center',
                #                     spacing='xs',
                #                     style={'margin-top': 10},
                #                     children=[
                #                         dmc.Text('Monthly Revenue', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                #                         dmc.Text(id='revenue', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                #                         dmc.Text('*from current customers only', id='totalrev', size='xs', color='green', style={'font-family': 'IntegralCF-RegularOblique'})
                #                     ]
                #                 )
                #             ],
                #         ),
                #         dmc.Paper(
                #             radius="md",  # or p=10 for border-radius of 10px
                #             withBorder=True,
                #             shadow='xs',
                #             p='sm',
                #             style={'height': '175px'},
                #             children=[
                #                 dmc.Center(
                #                     dmc.ThemeIcon(
                #                         size=50,
                #                         radius="xl",
                #                         color="green",
                #                         variant="light",
                #                         children=[DashIconify(icon="mdi:ecology", width=30)]
                #                     )
                #                 ),
                #                 dmc.Group(
                #                     direction='column',
                #                     position='center',
                #                     spacing='xs',
                #                     style={'margin-top': 10},
                #                     children=[
                #                         dmc.Text('Paperless Billing Accounts', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                #                         dmc.Text(id='paperless', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                #                         dmc.Text('Reams Saved', id='reams_saved', size='xs', color='green', style={'font-family': 'IntegralCF-RegularOblique'})
                #                     ]
                #                 )
                #             ],
                #         ),
            #         ]
            #     ),
            #     dmc.Divider(label='Demographics', labelPosition='center', size='xl'),
            #     dmc.Group(
            #         direction='row',
            #         grow=True,
            #         children=[
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '350px'},
            #                 children=[
            #                     dmc.Title('Gender', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='gender'),
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '350px'},
            #                 children=[
            #                     dmc.Title('Household', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='household')
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '350px'},
            #                 children=[
            #                     dmc.Title('Senior Citizen Status', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='age')
            #                 ]
            #             ),
            #         ]
            #     ),
            #     dmc.Group(
            #         direction='row',
            #         grow=True,
            #         children=[
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '500px'},
            #                 children=[
            #                     dmc.Title('Customer Density', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='locations_map')
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '500px'},
            #                 children=[
            #                     dmc.Title('Customers W/O Phone Service', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='locations_map1')
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '500px'},
            #                 children=[
            #                     dmc.Title('Customers W/O Internet Service', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='locations_map2')
            #                 ]
            #             ),
            #         ]
            #     ),
            #
            #     dmc.Space(h=50)

                # dmc.Group(
                #     direction='row',
                #     grow=True,
                #     children=[
                #         dmc.Paper(
                #             radius="md",  # or p=10 for border-radius of 10px
                #             withBorder=True,
                #             shadow='xs',
                #             p='sm',
                #             style={'height': '175px'},
                #             children=[
                #                 dmc.Center(
                #                     dmc.ThemeIcon(
                #                         size=50,
                #                         radius="xl",
                #                         color="violet",
                #                         variant="light",
                #                         children=[DashIconify(icon="fluent:people-community-20-filled", width=30)]
                #                     )
                #                 ),
                #                 dmc.Group(
                #                     direction='column',
                #                     position='center',
                #                     spacing='xs',
                #                     style={'margin-top': 10},
                #                     children=[
                #                         dmc.Text('Current Number of Customers', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                #                         dmc.Text(id='totalcust', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                #                         dmc.Text('Churn Rate', id='churn_rate', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                #                     ]
                #                 )
                #             ],
                #         ),
                #         dmc.Paper(
                #             radius="md",  # or p=10 for border-radius of 10px
                #             withBorder=True,
                #             shadow='xs',
                #             p='sm',
                #             style={'height': '175px'},
                #             children=[
                #                 dmc.Center(
                #                     dmc.ThemeIcon(
                #                         size=50,
                #                         radius="xl",
                #                         color="yellow",
                #                         variant="light",
                #                         children=[DashIconify(icon="mdi:recurring-payment", width=30)]
                #                     )
                #                 ),
                #                 dmc.Group(
                #                     direction='column',
                #                     position='center',
                #                     spacing='xs',
                #                     style={'margin-top': 10},
                #                     children=[
                #                         dmc.Text('Monthly Revenue', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                #                         dmc.Text(id='revenue', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                #                         dmc.Text('*from current customers only', id='totalrev', size='xs', color='green', style={'font-family': 'IntegralCF-RegularOblique'})
                #                     ]
                #                 )
                #             ],
                #         ),
                #         dmc.Paper(
                #             radius="md",  # or p=10 for border-radius of 10px
                #             withBorder=True,
                #             shadow='xs',
                #             p='sm',
                #             style={'height': '175px'},
                #             children=[
                #                 dmc.Center(
                #                     dmc.ThemeIcon(
                #                         size=50,
                #                         radius="xl",
                #                         color="green",
                #                         variant="light",
                #                         children=[DashIconify(icon="mdi:ecology", width=30)]
                #                     )
                #                 ),
                #                 dmc.Group(
                #                     direction='column',
                #                     position='center',
                #                     spacing='xs',
                #                     style={'margin-top': 10},
                #                     children=[
                #                         dmc.Text('Paperless Billing Accounts', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                #                         dmc.Text(id='paperless', size='xl', style={'font-family': 'IntegralCF-ExtraBold'}),
                #                         dmc.Text('Reams Saved', id='reams_saved', size='xs', color='green', style={'font-family': 'IntegralCF-RegularOblique'})
                #                     ]
                #                 )
                #             ],
                #         ),
            #         ]
            #     ),
            #     dmc.Divider(label='Demographics', labelPosition='center', size='xl'),
            #     dmc.Group(
            #         direction='row',
            #         grow=True,
            #         children=[
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '350px'},
            #                 children=[
            #                     dmc.Title('Gender', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='gender'),
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '350px'},
            #                 children=[
            #                     dmc.Title('Household', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='household')
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '350px'},
            #                 children=[
            #                     dmc.Title('Senior Citizen Status', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='age')
            #                 ]
            #             ),
            #         ]
            #     ),
            #     dmc.Group(
            #         direction='row',
            #         grow=True,
            #         children=[
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '500px'},
            #                 children=[
            #                     dmc.Title('Customer Density', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='locations_map')
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '500px'},
            #                 children=[
            #                     dmc.Title('Customers W/O Phone Service', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='locations_map1')
            #                 ]
            #             ),
            #             dmc.Paper(
            #                 radius="md",  # or p=10 for border-radius of 10px
            #                 withBorder=True,
            #                 shadow='xs',
            #                 p='sm',
            #                 style={'height': '500px'},
            #                 children=[
            #                     dmc.Title('Customers W/O Internet Service', order=4, style={'font-family': 'IntegralCF-Regular', 'text-align': 'center', 'color': 'grey', 'letter-spacing': '1px'}),
            #                     ddk.Graph(id='locations_map2')
            #                 ]
            #             ),
            #         ]
            #     ),
            #
            #     dmc.Space(h=50)

        # html.A(dmc.ThemeIcon( DashIconify(icon = '/assets/images/vgsi_logo.png'))),
        # Date Picker: Base Inventory Date --
        dcc.DatePickerSingle(id='baseInventory_date', date=TODAY,
                             style={'position':'absolute','left': 1200, 'top': TOP_0, 'width':300,  'font_size':10, 'height':10},),

        dcc.DatePickerRange(
            id="date_range",
            min_date_allowed=datetime.date(2022,1,1), max_date_allowed=TODAY+datetime.timedelta(days=1), start_date=TODAY-datetime.timedelta(days=30), end_date=TODAY+datetime.timedelta(days=1),
            style={'position':'absolute','left': 10, 'top': TOP_0, 'width':300, 'height':20,  'textSize':15},
        ),

        dmc.Button("Rfresh", id="button",leftIcon=DashIconify(icon="carbon:settings-check",color='pink', width=20),
                   style={'position':'absolute','left': 10, 'top': TOP_0-50, 'width':250, 'height': 30, 'color':'red', 'background-color':'lightblue'}),



        # Board Level CheckList --
        html.Label("Board Level Filter",
                   style={'position':'absolute', 'textAlign':'center', 'color':'black', 'textSize':20,  'left': LEFT_1, 'top': TOP_0, 'width':250, 'backgroundColor': 'cyan'}),
        dcc.Checklist(id='level_checkList',  options=['LV_1', 'LV_2', 'LV_3', 'Cut'], value=['LV_1', 'LV_2', 'LV_3', 'Cut'], inline=True,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': LEFT_1, 'top': TOP_0+30, 'width':300}
                      ),


        # Graph: Board Inventory -----
        dcc.Graph(id="pie_1", style={'position':'absolute','left': 10, 'top': TOP_0+60, 'width':300, 'height':300}),
        dcc.Graph(id="pie_2", style={'position':'absolute','left': 280, 'top': TOP_0+60, 'width':500, 'height':550}),

        dcc.Graph(id="bar_1", style={'position':'absolute','left': 820, 'top': TOP_0+60, 'width':1000, 'height': 500}),
        dcc.Graph(id="bar_2", style={'position':'absolute','left': LEFT_2, 'top': TOP_0+620, 'width':900, 'height': 500}),
        dcc.Graph(id="bar_3", style={'position':'absolute','left': LEFT_0, 'top': TOP_0+620, 'width':900, 'height': 500}),

        # dcc.Graph(id="indi_1", style={'position':'absolute','left': 1500, 'top': TOP_0, 'width':400, 'height': 150}),

        dcc.RadioItems(id='dropDown_qty',  options=['Qty_sqm', 'Qty_pcs','Qty_pt',], value='Qty_sqm', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': 870, 'top': TOP_0, 'width':100, 'backgroundColor':'lightgray'}
                      ),

        # Inventory Trend -------
        dcc.Checklist(id='dailyInventory',  options=['Inventory Trend'], value=[], inline=True,
                      style={'position':'absolute', 'textAlign':'left', 'color':'red', 'textSize':10,  'left': LEFT_0, 'top': TOP_0+600, 'width':1900, 'height':20, 'backgroundColor': 'lightgray'}
                      ),
        dcc.RadioItems(id='radio1',  options=['Inventory', 'Input', 'Output'], value='Input', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': LEFT_1+200, 'top': TOP_0+620, 'width':100, 'height':60, 'backgroundColor': 'lightgray'}
                      ),
        dcc.RadioItems(id='radio2',  options=['Inventory', 'Input', 'Output'], value='Output', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': LEFT_3+200, 'top': TOP_0+620, 'width':100, 'height':60, 'backgroundColor': 'lightgray'}
                      ),
        dcc.Checklist(id='select_board',  options=['Select All'], value=['Select All'], inline=True,
                      style={'position':'absolute','left': LEFT_1, 'top': TOP_0+600, 'width':150, 'height': 20, 'font_size':15, 'color': 'red', 'backgroundColor':'gold'}
                      ),



        # Bar Chart Drop Down ---
        html.Label("Base Unit", style={'position':'absolute', 'textAlign':'center', 'color':'black', 'textSize':20,  'left': 720, 'top': TOP_0, 'width':150, 'backgroundColor': 'cyan'}),


        # Periodical BoardName Select
        html.Label("Inventory Base Date", style={'position':'absolute', 'textAlign':'center', 'color':'black', 'textSize':20,  'left': 1050, 'top': TOP_0, 'width':150, 'backgroundColor': 'cyan'}),


        # Updateed date ----
        html.Label("DB Update Date(In/Out):", style={'position': 'absolute', 'textAlign': 'right', 'color': 'black', 'textSize': 20, 'left': 1000, 'top': TOP_0+60, 'width': 200, 'height':20,'backgroundColor': 'cyan'}),
        dcc.Textarea(id='update_date1', style={'position': 'absolute', 'textAlign': 'center', 'color': 'black', 'textSize': 20, 'left': 1200, 'top': TOP_0+60, 'width': 100, 'height':20,'backgroundColor': 'white'}),
        dcc.Textarea(id='update_date2', style={'position': 'absolute', 'textAlign': 'center', 'color': 'black', 'textSize': 20, 'left': 1300, 'top': TOP_0+60, 'width': 100, 'height':20,'backgroundColor': 'white'}),

        # layout: Board Shipping -----
        html.Label("Shipping Analyze", style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':30,  'left': 10, 'top': TOP_1+100, 'width':1900, 'height':30, 'backgroundColor': 'cyan'}),
        dcc.Graph(id="bar_11", style={'position':'absolute','left': 10, 'top': TOP_1+130, 'width':900, 'height':500}),  # Customers Position
        dcc.RadioItems(id='radio_custom_vendor',  options=['Customer', 'Vendor'], value='Customer', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': 600, 'top': TOP_1+170, 'width':600}),
        dcc.RadioItems(id='radio_period',  options=['Daily', 'Monthly', 'Weekly', 'Quarterly'], value='Daily', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left':310,'top': TOP_0, 'width':100, 'backgroundColor':'lightgray'}),
        dcc.Graph(id="bar_12", style={'position':'absolute','left': 920, 'top': TOP_1+130, 'width':900, 'height':500}),  # Customers Position
        dcc.Input(id="input_days", type="number", placeholder="Debounce False", value=60,
                  style={'position':'absolute', 'textAlign':'right', 'color':'red', 'textSize':20,  'left':1500,'top': TOP_1+170, 'width':100}),

        # pivot table --
        # html.Div(
        #     dash_pivottable.PivotTable(
        #         id='pvt_11',
        #         cols=['YM'],
        #         rows=['BoardName'],
        #         vals=['Qty_sqm'],
        #         aggregatorName='Sum',
        #         # rendererName='Table',
        #     ), style={'position': 'absolute', 'left': 10, 'top': pos_top_base_material-500, 'width': 800, 'height':400, 'text-align':'center'}
        # ),


        # layout: Material Inventory --------
        html.Label("Material Inventory Analyze", style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':30,  'left': 10, 'top': TOP_2, 'width':1900, 'height':30, 'backgroundColor': 'cyan'}),
        dcc.Graph(id="bar_21", style={'position':'absolute','left': 10, 'top': TOP_2+30, 'width':900, 'height':500}),  # Customers Position
        dcc.Graph(id="idc_21", style={'position':'absolute','left': 300, 'top': TOP_2+30, 'width':100, 'height': 100}),
        dcc.Graph(id="idc_22", style={'position':'absolute','left': 400, 'top': TOP_2+30, 'width':100, 'height': 100}),
        dcc.Graph(id="idc_23", style={'position':'absolute','left': 500, 'top': TOP_2+30, 'width':100, 'height': 100}),

        # html.A("Return to Home", href='http://127.0.0.1:8050/logistic_analyze_01/', target="bar_1",
        #        style={'position':'absolute','left': 1000, 'top': pos_top_base_material+30, 'width':200, 'height': 100})
    ]
)
@logistic_app.callback(Output('content', 'children'),
                [Input('url', 'pathname')])
def display_content(pathname):
    page_name = logistic_app.strip_relative_path(pathname)
    if not page_name:  # None or ''
        return logistic_app.customerbase.layout
    elif page_name == 'churn':
        return logistic_app.churn.layout
    elif page_name == 'summary':
        return logistic_app.summary.layout


@logistic_app.callback(
    # Board Inventory ---
    Output('pie_1', 'figure'),
    Output('pie_2', 'figure'),

    Output('bar_1', 'figure'),
    Output('bar_2', 'figure'),
    Output('bar_3', 'figure'),

    Output('indi_1', 'figure'),

    # Shipping Analyze ---
    Output('bar_11', 'figure'),
    Output('bar_12', 'figure'),
    # Output('pvt_11', 'data'),

    Output('bar_21', 'figure'),
    Output('update_date1', 'value'),
    Output('update_date2', 'value'),
    Output('idc_21', 'figure'),
    Output('idc_22', 'figure'),
    Output('idc_23', 'figure'),

    # Board Inventory ---
    Input('date_range', 'start_date'),
    Input('date_range', 'end_date'),
    Input('button', 'n_clicks'),
    Input('level_checkList', 'value'),
    Input('dropDown_qty', 'value'),
    Input('baseInventory_date', 'date'),
    Input('dailyInventory', 'value'),
    Input('radio1', 'value'),
    Input('radio2', 'value'),

    # Shipping Analyze ---
    Input('radio_period', 'value'),
    Input('radio_custom_vendor', 'value'),
    Input('input_days', 'value'),
    Input('select_board', 'value'),

)
def updateData(start_date, end_date, button, level_checkList, dropDown_qty, baseInventory_date, dailyInventory, radio1, radio2,
               radio_period, radio_custom_vendor, input_days, select_board):
    TODAY = date.today()
    # print(date_range.start_date)
    start_date = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:10]))
    end_date = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]))
    baseInventory_date = datetime.date(int(baseInventory_date[:4]), int(baseInventory_date[5:7]), int(baseInventory_date[8:10]))

    val_BoardLevel = level_checkList
    unit_Analyze = dropDown_qty

    # Board Analyze ----------------
    df_BI = pd.read_sql("select * from 900_BaseInventory_Board;", con=engine)  # Board Inventory DB
    df_Input  = pd.read_sql("select * from 900_Logistic_Input_Board;", con=engine)  # Board Inventory DB
    df_Output = pd.read_sql("select * from 900_Logistic_Output_Board;", con=engine)  # Board Inventory DB

    df_Input_BI = df_Input.merge(df_BI, how='left', left_on='CodeTOB', right_on='BoardCode')
    df_Input_BI['Invt_in_pcs'] = df_Input_BI['BoardStockBase'] + df_Input_BI['Qty_pcs']
    df_Input_BI['Invt_in_sqm'] = df_Input_BI['Invt_in_pcs'] * df_Input_BI['PcsArea']
    df_Input_BI['Invt_in_pt'] = df_Input_BI['Invt_in_pcs'] / df_Input_BI['spp_x']

    df_Output_BI = df_Output.merge(df_BI, how='left', left_on='CodeTOB', right_on='BoardCode')
    df_Output_BI['Invt_out_pcs'] = df_Output_BI['BoardStockBase'] + df_Output_BI['Qty_pcs']
    df_Output_BI['Invt_out_sqm'] = df_Output_BI['Invt_out_pcs'] * df_Output_BI['PcsArea']
    df_Output_BI['Invt_out_pt'] = df_Output_BI['Invt_out_pcs'] / df_Output_BI['spp_x']

    df_Input_BI['Date2'] = pd.to_datetime(df_Input_BI['Date'])
    df_Input_BI['YM'] = df_Input_BI['Date2'].dt.strftime("%Y%m")
    df_Input_BI['YW'] = df_Input_BI['Date2'].dt.strftime("%Y%w")
    df_Input_BI['YQ'] = df_Input_BI['Date2'].dt.quarter

    df_Output_BI['Date2'] = pd.to_datetime(df_Output_BI['Date'])
    df_Output_BI['YM'] = df_Output_BI['Date2'].dt.strftime("%Y%m")
    df_Output_BI['YW'] = df_Output_BI['Date2'].dt.strftime("%Y%w")
    df_Output_BI['YQ'] = df_Output_BI['Date2'].dt.quarter

    # Material Analyze ----------------
    df_Mt_Master = pd.read_sql("select * from 900_Logistic_Masterfile_Material;", con=engine)  # Material Master DB
    df_Mt_In = pd.read_sql("select * from 900_Logistic_Input_Material;", con=engine)  # Material Inventory DB
    df_Mt_Out = pd.read_sql("select * from 900_Logistic_Output_Material;", con=engine)  # Material

    df_Mt_In_Master = df_Mt_In.merge(df_Mt_Master, how='left', left_on='LinkInCode', right_on='LinkCode')
    df_Mt_Out_Master = df_Mt_Out.merge(df_Mt_Master, how='left', left_on='LinkOutCode', right_on='LinkCode')

    # SH = xl.Book('D:\\Python_Print_CHK.xlsx').sheets['temp']
    # SH2 = xl.Book('D:\\Python_Print_CHK.xlsx').sheets['Sheet2']
    # # SH2 = xl.Book('D:\PyProject2023\Logistic\XLS\900_Board_Material.xlsx').sheets['temp2']
    # SH.range('a1:az100000').clear_contents()
    # SH.range('a1').value = df_Mt_In_Master


    # Define the Period ---

    if radio_period=='Daily':Period = 'Date'
    elif radio_period=='Monthly':Period = 'YM'
    elif radio_period=='Weekly':Period = 'YW'
    elif radio_period=='Quarterly':Period = 'YQ'
    else: Period = 'Date'

    [pie_chart1, pie_chart2, bar_chart1, idc_TotalInventory, bar_chart2, bar_chart3] =\
    BoardInventory(df_BI, df_Input_BI, df_Output_BI,  val_BoardLevel, unit_Analyze, baseInventory_date, start_date, end_date, dailyInventory, radio1, df_Input_BI,
                   df_Output_BI, radio2, radio_period, radio_custom_vendor, Period, select_board)

    [bar_chart_11, bar_chart_12, data_pv1] = \
    BoardOutput(df_BI, df_Input_BI, df_Output_BI,  val_BoardLevel, unit_Analyze, baseInventory_date, start_date, end_date, dailyInventory, radio1, df_Input_BI,
                df_Output_BI, radio2, radio_custom_vendor, Period, input_days)

    [bar_chart_21, IDC_21, IDC_22, IDC_23] = \
        Material_Inventory(df_Mt_Master, df_Mt_In_Master, df_Mt_Out_Master, baseInventory_date, start_date, end_date,)

    update_input = df_Input['Date'].max()
    update_output = df_Output['Date'].max()

    return [pie_chart1, pie_chart2,
            bar_chart1, bar_chart2, bar_chart3,
            idc_TotalInventory,
            bar_chart_11, bar_chart_12, #data_pv1,
            bar_chart_21,
            update_input, update_output,
            IDC_21, IDC_22, IDC_23]

def Material_Inventory(df_Mt_Master, df_Mt_In_Master, df_Mt_Out_Master, baseInventory_date, start_date, end_date,):
    # Board Inventory ------
    BASE_DATE = baseInventory_date

    def fx_invt_qty_in(row):
        if row.Date > row.BaseDate: return row.Qty_kg
        elif row.Date < row.BaseDate: return row.Qty_kg * (-1)
        else: return 0

    def fx_invt_qty_out(row):
        if row.Date > row.BaseDate: return row.Qty_kg * (-1)
        elif row.Date < row.BaseDate: return row.Qty_kg
        else: return 0

    df_Mt_In_Master['Qty_kg_adj'] = df_Mt_In_Master.apply(fx_invt_qty_in, axis=1)
    df_Mt_Out_Master['Qty_kg_adj'] = df_Mt_Out_Master.apply(fx_invt_qty_out, axis=1)

    def fx_input(row):
        return df_Mt_In_Master[(df_Mt_In_Master["Date"] > row.BaseDate) & (df_Mt_In_Master["Date"] <= BASE_DATE) & (df_Mt_In_Master['Material_Code'] == row.Item_Code)]['Qty_kg_adj'].sum()
    def fx_output(row):
        return df_Mt_Out_Master[(df_Mt_Out_Master["Date"] > row.BaseDate) & (df_Mt_Out_Master["Date"] <= BASE_DATE) & (df_Mt_Out_Master['Material_Code'] == row.Item_Code)]['Qty_kg_adj'].sum()
    def fx_inventory(row): return row.Base_kg + row.In_sum - row.Out_sum

    df_Mt_Master['In_sum'] = df_Mt_Master.apply(fx_input, axis=1)
    df_Mt_Master['Out_sum'] = df_Mt_Master.apply(fx_output, axis=1)
    df_Mt_Master['Qty_kg'] = df_Mt_Master.apply(fx_inventory, axis=1)

    # df_Mt_Master['Date_Invt'] = BASE_DATE

    color_Market = {'Korea': 'dodgerblue', 'VietNam': 'orangered', }
    color_BoardType = {'SD_Korea': 'gold', 'SD_Viet': 'ivory', 'AM_Korea': 'yellowgreen', 'MR_Korea': 'dodgerblue', 'MR_Viet': 'mediumseagreen', 'FR_Korea': 'red', 'FR_Viet': 'pink', 'Cut_Viet': 'silver', }
    # Bar 1: Market analyze --

    df_bar_21 = df_Mt_Master.query("Category2 in ['CF', 'BB', 'CF_Korea','BB_Korea', 'CF_Korea2']").groupby(by=['Category','Supplier'], as_index=False).agg({'Qty_kg': 'sum'}).sort_values(by='Qty_kg', ascending=False)
    df_sct_21 = df_Mt_Master.query("Category2 in ['CF', 'BB', 'CF_Korea','BB_Korea', 'CF_Korea2']").groupby(by=['Category'], as_index=False).agg({'Qty_kg': 'sum'}).sort_values(by='Qty_kg', ascending=False)
    bar_chart_21 = px.bar(df_bar_21, x='Category', y='Qty_kg', color='Supplier', title='Paper Inventory(kg) ')
    bar_chart_21.add_scatter(x=df_sct_21['Category'], y=df_sct_21['Qty_kg'], text=df_sct_21['Qty_kg'], name='Category Total', textposition='top center', texttemplate="%{text:,.0f}",
                             mode='markers+text')

    # Indicator 21:  CF 950, 955 --
    # Qty_CF_Korea2 = df_Mt_Master.query("Category2 == 'CF_Korea2'")['Qty_kg'].sum()
    val_IDC_21_1 = df_Mt_Master.query("Category2 == 'CF_Korea2'").agg({'Qty_kg': 'sum'}) # CF Korea2
    IDC_21 = go.Figure(go.Indicator( mode="number", value=float(val_IDC_21_1), number={'font_color': 'black', 'font_size': 15, "valueformat": ",.0f"},
                                     title={'text': 'CF(Korea2)','font_size': 15,}, domain={'x': [1, 0], 'y': [0, 1]}, )
                       )
    val_IDC_21_2 = df_Mt_Master.query("Category2 == 'CF_Korea'").agg({'Qty_kg': 'sum'}) # CF Korea
    IDC_22 = go.Figure(go.Indicator( mode="number", value=float(val_IDC_21_2), number={'font_color': 'black', 'font_size': 15, "valueformat": ",.0f"},
                                     title={'text': 'CF(Korea)','font_size': 15,}, domain={'x': [1, 0], 'y': [0, 1]}, )
                       )
    val_IDC_21_3 = df_Mt_Master.query("Category2 == 'BB_Korea'").agg({'Qty_kg': 'sum'}) # BB Korea
    IDC_23 = go.Figure(go.Indicator( mode="number", value=float(val_IDC_21_3), number={'font_color': 'black', 'font_size': 15, "valueformat": ",.0f"},
                                     title={'text': 'BB(Korea)','font_size': 15,}, domain={'x': [1, 0], 'y': [0, 1]}, )
                       )

    return [bar_chart_21, IDC_21, IDC_22, IDC_23]

def BoardOutput(df_BI, df_Input, df_Output,  val_BoardLevel, unit_Analyze, baseInventory_date, start_date, end_date, dailyInventory, radio1, df_Input_BI,
                df_Output_BI, radio2,  radio_custom_vendor, Period, input_days):
    df_Output_BI_copy = df_Output_BI.copy()
    df_Output_BI = df_Output_BI.query("Date>=@start_date and Date<=@end_date")

    # Bar 11: Customers/Venodrs Quantity Sales --------
    df_Output_BI_bar11 = df_Output_BI.query("Level in @val_BoardLevel").groupby(by=[radio_custom_vendor, 'MarketGroup', ], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by='Qty_sqm', ascending=False)
    bar_chart_11 = px.bar(df_Output_BI_bar11, x=radio_custom_vendor, y=unit_Analyze, color='MarketGroup', title=radio_custom_vendor + ' Sales Quantity: ' + unit_Analyze, text_auto=True, )
    # bar_chart_11.update_traces(visible="legendonly")
    bar_chart_11.update_traces(texttemplate='%{y:,.0f}')

    days = int(input_days)

    dayFrom = baseInventory_date - datetime.timedelta(days=days)
    title_text = 'Daily average shipment over the past {} days: '.format(days) + unit_Analyze

    df_Output_BI_copy = df_Output_BI_copy.query("Date>=@dayFrom and Date<=@baseInventory_date")
    df_Output_BI_bar12 = df_Output_BI_copy.query("Level in @val_BoardLevel").groupby(by=['BoardName_y', 'MarketGroup', ], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by='Qty_sqm', ascending=False)
    df_Output_BI_bar12[unit_Analyze] = df_Output_BI_bar12[unit_Analyze] / days
    bar_chart_12 = px.bar(df_Output_BI_bar12, x='BoardName_y', y=unit_Analyze, color='MarketGroup', title=title_text, text_auto=True, )
    bar_chart_12.update_traces(texttemplate='%{y:,.0f}')
    # bar_chart_11.update_traces(visible="legendonly")

    # Pivot 1: Shipping ------
    df_pv_1 = df_Output_BI
    data_pv1 = df_pv_1.to_dict('records')

       # df_BI_daily_bar2_scatter = df_BI_daily.query("Level in @val_BoardLevel").groupby(by=['Date_invt'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
    # bar_chart2.add_scatter(x=df_BI_daily_bar2_scatter.Date_invt, y=df_BI_daily_bar2_scatter[unit_Analyze], text=unit_Analyze, name='Total Inventory',
    #                        marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2)))

    return [bar_chart_11, bar_chart_12, data_pv1]

def BoardInventory(df_BI, df_Input, df_Output,  val_BoardLevel, unit_Analyze, baseInventory_date, start_date, end_date, dailyInventory, radio1, df_Input_BI,
                   df_Output_BI, radio2, radio_period, radio_custom_vendor, Period, select_board):
    # Board Inventory ------
    BASE_DATE = baseInventory_date

    def fx_input(row): return df_Input[(df_Input["Date"] > row.BaseDate) & (df_Input["Date"] <= BASE_DATE) & (df_Input['CodeTOB']==row.BoardCode)].Qty_pcs.sum()
    def fx_output(row): return df_Output[(df_Output["Date"] > row.BaseDate) & (df_Output["Date"] <= BASE_DATE) & (df_Output['CodeTOB']==row.BoardCode)].Qty_pcs.sum()
    def fx_inventory(row): return row.BoardStockBase + row.In_sum - row.Out_sum

    df_BI['In_sum']    = df_BI.apply(fx_input, axis=1)
    df_BI['Out_sum']   = df_BI.apply(fx_output, axis=1)
    df_BI['Inventory'] = df_BI.apply(fx_inventory, axis=1)
    df_BI['Date_invt'] = BASE_DATE
    df_BI['Qty_pt'] = df_BI['Inventory'] / df_BI['spp']
    df_BI['Qty_sqm'] = df_BI['Inventory'] * df_BI['Width'] / 1000 * df_BI['Length'] / 1000
    df_BI['Qty_pcs'] = df_BI['Inventory']

    df_BI_daily = df_BI.copy()
    DayList = np.arange(start_date, end_date, dtype='datetime64[D]')
    df_BI_daily.drop(df_BI_daily.index, inplace=True)


    color_Market = {'Korea': 'dodgerblue', 'VietNam': 'orangered',}
    color_BoardType = {'SD_Korea': 'gold', 'SD_Viet': 'ivory', 'AM_Korea': 'yellowgreen','MR_Korea': 'dodgerblue','MR_Viet': 'mediumseagreen','FR_Korea': 'red','FR_Viet': 'pink', 'Cut_Viet': 'silver',}

    # Pie 1: Market analyze --
    df_BI_pie1 = df_BI.query("Level in @val_BoardLevel")
    pie_chart1 = px.pie(df_BI_pie1, names='MarketGroup', values=unit_Analyze, color='MarketGroup', title='Market Ratio: ' + unit_Analyze, hole=0.1, color_discrete_map=color_Market)
    pie_chart1.update_traces(textposition='auto', textinfo='label+value+percent', texttemplate="%{value:,.0f} / %{percent:0.1%}", )

    # Pie 2: Board Level analyze ---
    df_BI_pie2 = df_BI.query("Level in @val_BoardLevel").groupby(by=['BoardType'], as_index=False).agg({'Qty_pt': 'count', 'Qty_sqm': 'sum', 'Qty_pcs':'sum'})
    pie_chart2 = px.pie(df_BI_pie2, names='BoardType', values='Qty_sqm', color='BoardType', title='TOB Inventory Ratio: ' + unit_Analyze, hole=0.1, color_discrete_map=color_BoardType )
    pie_chart2.update_traces(textinfo='value+percent', textposition='auto', texttemplate="%{value:,.0f} / %{percent:0.2%}",)

    # Bar1: BoardName Inventory ---
    df_BI_bar1 = df_BI.query("Level in @val_BoardLevel").groupby(by=['MarketGroup', 'BoardCode', 'BoardName'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs':'sum'}).sort_values(by='Qty_sqm', ascending=False)
    bar_chart1 = px.bar(df_BI_bar1, x='BoardName', y=unit_Analyze, color='MarketGroup', title='Board Inventory: ' + unit_Analyze, text_auto=True, text=unit_Analyze,
                        color_discrete_map=color_Market,)
    bar_chart1.update_traces(texttemplate='%{y:,.0f}')

    # Indicator: Total Inventory --
    num_target = 500000
    if unit_Analyze == 'Qty_pcs': num_target = num_target / 1.62
    elif unit_Analyze == 'Qty_pt': num_target = num_target / 1.62 / 120
    else: num_target = num_target

    val_invTotal = df_BI.query("Level in @val_BoardLevel")[unit_Analyze].sum()
    idc_TotalInventory = go.Figure(go.Indicator(
        mode = "number+delta", value = val_invTotal, number={'font_color':'black', 'font_size':35, "valueformat": ",.0f"},
        title = {'text': 'Total Inventory:' + unit_Analyze, 'font_size':10, 'font_color': 'red'},
        delta={'reference':num_target, "valueformat": ",.0f" }, domain = {'x': [1, 0], 'y': [0.5, 0.5]})
    )

    # Daily Inventory --------
    if dailyInventory == ['Inventory Trend']:

        for i, dd in enumerate(DayList):
            def fx_input(row):
                return df_Input[(df_Input["Date"] > row.BaseDate) & (df_Input["Date"] <= dd) & (df_Input['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()

            def fx_output(row):
                return df_Output[(df_Output["Date"] > row.BaseDate) & (df_Output["Date"] <= dd) & (df_Output['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()

            def fx_inventory(row):
                return row.BoardStockBase + row.In_sum - row.Out_sum

            df_BI['In_sum'] = df_BI.apply(fx_input, axis=1)
            df_BI['Out_sum'] = df_BI.apply(fx_output, axis=1)
            df_BI['Inventory'] = df_BI.apply(fx_inventory, axis=1)
            df_BI['Date_invt'] = dd

            df_BI['Qty_pt'] = df_BI['Inventory'] / df_BI['spp']
            df_BI['Qty_sqm'] = df_BI['Inventory'] * df_BI['Width'] / 1000 * df_BI['Length'] / 1000
            df_BI['Qty_pcs'] = df_BI['Inventory']

            for i, v in enumerate(df_BI.values):
                df_BI_daily.loc[len(df_BI_daily)] = v

        if radio1 == 'Inventory':
            # Bar2 and Scatter 1: Daily Inventory Trend (Market) ---
            df_BI_daily_bar2 = df_BI_daily.query("Level in @val_BoardLevel").groupby(by=['Date_invt', 'MarketGroup', ], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by='Qty_sqm', ascending=False)
            bar_chart2 = px.bar(df_BI_daily_bar2, x='Date_invt', y=unit_Analyze, color='MarketGroup', title='Daily Board Inventory: ' + unit_Analyze, text_auto=True, )

            df_BI_daily_bar2_scatter = df_BI_daily.query("Level in @val_BoardLevel").groupby(by=['Date_invt'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
            if select_board == ['Select All']:
                bar_chart2.add_scatter(x=df_BI_daily_bar2_scatter['Date_invt'], y=df_BI_daily_bar2_scatter[unit_Analyze], text=df_BI_daily_bar2_scatter[unit_Analyze], name='Total Inventory', mode='markers+lines+text',
                                       textposition='top center', texttemplate='%{text:,.0f}',
                                       marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2)), )
                bar_chart2.update_xaxes(rangeslider_visible=True)
            else:
                bar_chart2.update_traces(visible="legendonly")

            bar_chart2.update_traces(texttemplate='%{y:,.0f}')

            # Bar3 and Scatter 2: Daily Inventory Trend (BoardName)---
            df_BI_daily_bar3 = df_BI_daily.query("Level in @val_BoardLevel").groupby(by=['Date_invt', 'BoardName', ], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by='Qty_sqm', ascending=False)
            bar_chart3 = px.bar(df_BI_daily_bar3, x='Date_invt', y=unit_Analyze, color='BoardName', title='Daily Board Inventory: ' + unit_Analyze, text_auto=True, )


            df_BI_daily_bar3_scatter = df_BI_daily.query("Level in @val_BoardLevel").groupby(by=['Date_invt'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
            bar_chart3.add_scatter(x=df_BI_daily_bar3_scatter.Date_invt, y=df_BI_daily_bar3_scatter[unit_Analyze], text=unit_Analyze, name='Total Inventory',
                                   marker=dict( color='blue', size=11, line=dict( color='MediumPurple', width=2)))
            if select_board == ['Select All']:
                bar_chart3.add_scatter(x=df_BI_daily_bar3_scatter['Date_invt'], y=df_BI_daily_bar3_scatter[unit_Analyze], text=df_BI_daily_bar3_scatter[unit_Analyze], name='Total Inventory', mode='markers+lines+text',
                                       textposition='top center', texttemplate='%{text:,.0f}',
                                       marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2)), )
                bar_chart3.update_xaxes(rangeslider_visible=True)
            else:
                bar_chart3.update_traces(visible="legendonly")

            bar_chart3.update_traces(texttemplate='%{y:,.0f}')

    else:
        bar_chart2 = bar_chart1
        bar_chart3 = bar_chart1

    if radio1 == 'Input':
        # Bar and Scatter 2: Daily Input Trend (BoardName)---

        df_Input_BI_filt = df_Input_BI.query("Date>=@start_date and Date<=@end_date")
        # df_Input_BI_filt = df_Input_BI[(df_Input_BI["Date"]>=start_date) & (df_Input_BI["Date"]<=end_date)]
        df_Input_bar3 = df_Input_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period, 'BoardName_y'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
        bar_chart3 = px.bar(df_Input_bar3, x=Period, y=unit_Analyze, color='BoardName_y', title=Period + ' Board Input: ' + unit_Analyze, text_auto=True,  )

        df_Input_scatter3 = df_Input_BI_filt.query("Level in @val_BoardLevel").sort_values(by=Period, ascending=True).groupby(by=[Period], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})

        if select_board ==['Select All']:
            bar_chart3.add_scatter(x=df_Input_scatter3[Period], y=df_Input_scatter3[unit_Analyze], text=df_Input_scatter3[unit_Analyze], name='Total Input', mode='markers+lines+text',
                                   textposition='top center', texttemplate='%{text:,.0f}',
                                   marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2)), )
            bar_chart3.update_xaxes(rangeslider_visible=True)
        else: bar_chart3.update_traces(visible="legendonly")

        bar_chart3.update_traces(texttemplate='%{y:,.0f}')

    if radio1 == 'Output':
        # Bar and Scatter 2: Daily Input Trend (BoardName)---
        df_Output_BI_filt = df_Output_BI.query("Date>=@start_date and Date<=@end_date")
        df_Output_bar3 = df_Output_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period, 'BoardName_y', ], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by=Period, ascending=True)
        bar_chart3 = px.bar(df_Output_bar3, x=Period, y=unit_Analyze, color='BoardName_y', title=Period + ' Board Input: ' + unit_Analyze, text_auto=True, )

        df_Output_scatter3 = df_Output_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by=Period, ascending=True)

        if select_board == ['Select All']:
            bar_chart3.add_scatter(x=df_Output_scatter3[Period], y=df_Output_scatter3[unit_Analyze], text=df_Output_scatter3[unit_Analyze], name='Total Output', mode='markers+lines+text',
                                   textposition='top center', texttemplate='%{text:,.0f}',
                                   marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2)), )

        else:
            bar_chart3.update_traces(visible="legendonly")

        bar_chart3.update_traces(texttemplate='%{y:,.0f}')

    if radio2 == 'Input':
        # Bar and Scatter 2: Daily Input Trend (BoardName)---
        df_Input_BI_filt = df_Input_BI.query("Date>=@start_date and Date<=@end_date")
        # df_Input_BI_filt = df_Input_BI[(df_Input_BI["Date"]>=start_date) & (df_Input_BI["Date"]<=end_date)]
        df_Input_bar3 = df_Input_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period, 'BoardName_y'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by=Period, ascending=True)
        bar_chart2 = px.bar(df_Input_bar3, x=Period, y=unit_Analyze, color='BoardName_y', title=Period + ' Board Input: ' + unit_Analyze, text_auto=True, texttemplate='%{y:,.0f}',)

        df_Input_scatter3 = df_Input_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by=Period, ascending=True)

        if select_board == ['Select All']:
            bar_chart2.add_scatter(x=df_Input_scatter3[Period], y=df_Input_scatter3[unit_Analyze], text=df_Input_scatter3[unit_Analyze], name='Total Input', mode='markers+lines+text',
                                   textposition='top center', texttemplate='%{text:,.0f}',
                                   marker=dict(color='green', size=11, line=dict(color='MediumPurple', width=2)), )

        else:
            bar_chart2.update_traces(visible="legendonly")

        bar_chart2.update_traces(texttemplate='%{y:,.0f}')

    if radio2 == 'Output':
        # Bar and Scatter 2: Daily Input Trend (BoardName)---
        df_Output_BI_filt = df_Output_BI.query("Date>=@start_date and Date<=@end_date")
        df_Output_bar3 = df_Output_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period, 'BoardName_y', ], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by=Period, ascending=True)
        bar_chart2 = px.bar(df_Output_bar3, x=Period, y=unit_Analyze, color='BoardName_y', title=Period + ' Board Output: ' + unit_Analyze, text_auto=True, )

        df_Output_scatter3 = df_Output_BI_filt.query("Level in @val_BoardLevel").groupby(by=[Period], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values(by=Period, ascending=True)

        if select_board == ['Select All']:
            bar_chart2.add_scatter(x=df_Output_scatter3[Period], y=df_Output_scatter3[unit_Analyze], text=df_Output_scatter3[unit_Analyze], name='Total Output', mode='markers+lines+text',
                                   textposition='top center', texttemplate='%{text:,.0f}',
                                   marker=dict(color='green', size=11, line=dict(color='MediumPurple', width=2)), )
            bar_chart2.update_xaxes(rangeslider_visible=True)
        else:
            bar_chart2.update_traces(visible="legendonly")

        bar_chart2.update_traces(texttemplate='%{y:,.0f}')

    return [pie_chart1, pie_chart2, bar_chart1, idc_TotalInventory, bar_chart2, bar_chart3]


if __name__ == '__main__':
    # logistic_app.run_server(debug=False, host='10.50.3.152', port=61303)
    logistic_app.run_server(debug=False,)


