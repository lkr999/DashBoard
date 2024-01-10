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

import dash_qr_manager as dqm

HOST     = '10.50.3.163'
DB       = 'gfactoryDB'
USER = 'leekr'
PASSWORD = 'g1234'

NOW = datetime.datetime.now()

TODAY = datetime.date.today()

try:
    # self.conn = pymysql.connect(host='192.168.1.95', user=USER, password=PASSWORD, db='zeitgypsumdb', charset='utf8')
    pymysql.install_as_MySQLdb()
    engine = create_engine("mysql://{user}:{password}@{host}/{db}".format(user=USER, password=PASSWORD, host=HOST, db=DB))
    # conn = mysql.connector.connect(**config)
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8')

    cur = conn.cursor()
except mariadb.Error as e: alert(e)

qrcode_app = dash.Dash(__name__, suppress_callback_exceptions = True,  url_base_pathname='/qrcode/',)

qrcode_app.layout = dmc.MantineProvider(
    id = 'dark_moder',

    withGlobalStyles=True,
    children=[
        dmc.Group(
            display="column",
            grow=False,
            children=[
                dmc.Button(
                    "QR Code Read",
                    id='qr_read',
                    variant="outline",
                    leftIcon=DashIconify(icon="material-symbols:refresh"),
                    style={"width": 250, "marginBottom": 10, "marginTop": 10},
                ),

                dqm.DashQrReader(
                    id='qr_code_reader',
                    style={'width': '50%'}
                ),

                dmc.Paper(
                    radius='sm', withBorder=True, shadow='xs', p='sm', style={'width': 330, 'height': 100},
                    children=[
                        dmc.Text('QR Code Read Result ', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='qrcode_read', size='xs', color='black', style={'font-family': 'IntegralCF-RegularOblique'}),
                    ]
                ),
            ],
        ),
    ]
)

@qrcode_app.callback(
    Output('qrcode_read','children'),
    Input('qr_code_reader', 'result'),
    Input('qr_read', 'n_clicks'),
)
def qrcode_update(qr_code_reader, qr_read):
    print("hello")
    return qr_code_reader

if __name__ == '__main__':
    qrcode_app.run_server(debug=True)
    # qrcode_app.run_server(debug=False, host='10.50.3.152', port=60659)
