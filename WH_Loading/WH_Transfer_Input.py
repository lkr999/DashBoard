import dash
import flask
import numpy as np
import xlwings as xl
import dash_mantine_components as dmc
import dash_bootstrap_components as dbc
import dash_ag_grid as dag
import matplotlib.pyplot as plt

import plotly.express as px
import pandas as pd
import pymysql
import mariadb
import dash_pivottable
import mysql.connector
import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash_iconify import DashIconify
from datetime import date
from dash import Dash, Input, Output, ctx, dcc, html, dash_table
from sqlalchemy import create_engine
from pymsgbox import alert, confirm, password, prompt
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from sklearn import linear_model
from sklearn.linear_model import LinearRegression
import cv2
import pyzbar.pyzbar as pyzbar
from pyzbar.pyzbar import decode
from playsound import playsound

from html import unescape
from dash_extensions import DeferScript
from dash_extensions.enrich import DashProxy, html
import qrcode

HOST     = '10.50.3.163'
DB       = 'gfactoryDB'
USER = 'leekr'
PASSWORD = 'g1234'

def df_download():
    try:
        # self.conn = pymysql.connect(host='192.168.1.95', user=USER, password=PASSWORD, db='zeitgypsumdb', charset='utf8')
        pymysql.install_as_MySQLdb()
        engine = create_engine("mysql://{user}:{password}@{host}/{db}".format(user=USER, password=PASSWORD, host=HOST, db=DB))
        # conn = mysql.connector.connect(**config)
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8')

        cur = conn.cursor()

        # df down ----
        df = pd.read_sql("select * from 800_WH_Loading;", con=engine)
    except mariadb.Error as e: alert(e)

    return df

from DashBoard.WH_Loading.app import wh_app
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

def read_qr_code():
    cap = cv2.VideoCapture(0)
    read_code = ''
    try:
        while True:
            success, frame = cap.read()
            if success:
                for code in pyzbar.decode(frame):
                    read_code = code.data.decode('utf-8')
                    if len(read_code)>10:
                        print('인식 성공', read_code)

                cv2.imshow('cam', frame)
                key = cv2.waitKey(1)
                # if key == 27:
                if len(read_code)>10: break
        cap.release()
        cv2.destroyAllWindows()
        return read_code
    except Exception as e:
        alert(e)

Period_radio_data = ['Daily', 'Weekly', 'Monthly', 'Quarterly']
Unit_radio_data = ['Qty_sqm','Qty_pcs','Qty_pt']
mxgraph = r'{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;app.diagrams.net\&quot; modified=\&quot;2021-06-07T06:06:13.695Z\&quot; agent=\&quot;5.0 (Windows)\&quot; etag=\&quot;4lPJKNab0_B4ArwMh0-7\&quot; version=\&quot;14.7.6\&quot;&gt;&lt;diagram id=\&quot;YgMnHLNxFGq_Sfquzsd6\&quot; name=\&quot;Page-1\&quot;&gt;jZJNT4QwEIZ/DUcToOriVVw1JruJcjDxYho60iaFIaUs4K+3yJSPbDbZSzN95qPTdyZgadm/GF7LAwrQQRyKPmBPQRzvktidIxgmwB4IFEaJCUULyNQvEAyJtkpAswm0iNqqegtzrCrI7YZxY7Dbhv2g3r5a8wLOQJZzfU4/lbByoslduPBXUIX0L0cheUrugwk0kgvsVojtA5YaRDtZZZ+CHrXzukx5zxe8c2MGKntNgknk8bs8fsj3+KtuDhxP+HZDVU5ct/RhatYOXgGDbSVgLBIG7LGTykJW83z0dm7kjklbaneLnEnlwFjoL/YZzb93WwNYgjWDC6EEdkuC0cZEO7p3i/6RF1WutL8nxmnkxVx6UcUZJIy/LgP49622mO3/AA==&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}'

wh_app.layout = dmc.MantineProvider(
    id = 'dark-moder2',
    withGlobalStyles=False,
    children = [
        dmc.Title(children='Whare House Transfer', order=1, style={'font-family': 'IntegralCF-ExtraBold', 'text-align': 'center', 'color': 'slategray', 'background-color': 'skyblue'}),
        html.Div(
            children=[
                # html.Div(className='mxgraph', style={"maxWidth": "100%"}, **{'data-mxgraph': unescape(mxgraph)}),
                DeferScript(src='https://viewer.diagrams.net/js/viewer-static.min.js'),
                DeferScript(src='http://unpkg.com/html5-qrcode'),
                DeferScript(src='index.js'),
                dmc.Group(
                    grow=False,
                    children=[
                        dmc.Button(
                            "Read QrCode",
                            id='read_qrcode',
                            variant="outline",
                            leftIcon=DashIconify(icon="streamline:graph"),
                            style={"width": 200, "marginBottom": 0},
                        ),
                        dmc.Text(id='read_txt', size=15, color='black', align='right', ),
                    ]
                ),
            ]
        )
    ]
)

#analytics = dash_user_analytics.DashUserAnalytics(app, automatic_routing=False)

@wh_app.callback(
    [Output('read_txt', 'children')],
    [Input('read_qrcode', 'n_clicks')]
)
def read_update(n_clicks):
    print('hello')
    read_txt = read_qr_code()
    cv2.destroyAllWindows()
    return read_txt


# @wh_app.clientside_callback(
#     """
#     function placeholder(n_clicks, data) {
#         window.data_to_copy = data.data;
#         var copyText = document.getElementById("text_input");
#         copyText.select();
#         copyText.setSelectionRange(0, 99999);
#         document.execCommand("copy");
#     }
#
#     // Overwrite what is being copied to the clipboard.
#     document.addEventListener('copy', function(e){
#       // e.clipboardData is initially empty, but we can set it to the
#       // data that we want copied onto the clipboard.
#       e.clipboardData.setData('text/plain', window.data_to_copy);
#
#       // This is necessary to prevent the current document selection from
#       // being written to the clipboard.
#       e.preventDefault();
#     });
#     """,
#     [Output("copy_output", "children"),
#      Output("excel_output", "data")],
#     [Input("copy_button", "n_clicks")],
# )
# def call():pass

if __name__ == '__main__':
    # wh_app.run_server(debug=True)
    wh_app.run_server(debug=False, host='10.50.3.152', port=59280)
