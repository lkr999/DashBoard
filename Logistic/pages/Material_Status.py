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

try:
    # self.conn = pymysql.connect(host='192.168.1.95', user=USER, password=PASSWORD, db='zeitgypsumdb', charset='utf8')
    pymysql.install_as_MySQLdb()
    engine = create_engine("mysql://{user}:{password}@{host}/{db}".format(user=USER, password=PASSWORD, host=HOST, db=DB))
    # conn = mysql.connector.connect(**config)
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8')

    cur = conn.cursor()
    df_BI = pd.read_sql("select * from 900_BaseInventory_Board;", con=engine)  # Board Inventory DB
    df_BI = df_BI.sort_values('BoardName')
    select_BoardName = [ d for d in df_BI['BoardName'].unique()]
except mariadb.Error as e: alert(e)

from DashBoard.Logistic.app import logistic_app

layout = dmc.MantineProvider(
    id = 'dark_moder',

    withGlobalStyles=True,
    children=[
        dmc.Title(children = 'Material Status', order = 1, style = {'font-family':'IntegralCF-ExtraBold', 'text-align':'left', 'color' :'slategray', 'font-size':20}),
        dmc.Divider(label = 'Overview',  labelPosition='center', size='xl'),

        # Indicater Overview -----
        dmc.Group(
            display ='column',
            grow=False,
            children=[
                # dmc.Space(),
                dcc.Graph(id="indi_1",style={'width':200, 'height': 100}),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':200,'height': 100},
                    children = [
                        dmc.Text('Korea vs Vietnam', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='market_korea', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='market_vietnam', size='xs', color='blue', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='update_date', size=10, color='black', style={'font-family': 'IntegralCF-RegularOblique'}),
                        # dmc.Text('Churn Rate', id='churn_rate', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                    ]
                ),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':330,'height': 100},
                    children = [
                        dmc.Text('Yearly Cumulated (Korea+Viet) KR%  ', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='cumulate_in_year', size='xs', color='black', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='cumulate_out_year', size='xs', color='blue', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='gap_year', size=9, color='red', style={'font-family': 'IntegralCF-RegularOblique'}),
                        # dmc.Text('Churn Rate', id='churn_rate', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                    ]
                ),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':330,'height': 100},
                    children = [
                        dmc.Text('Monthly Cumulated (Korea+Viet) KR% ', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='cumulate_in_month', size='xs', color='black', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='cumulate_out_month', size='xs', color='blue', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='gap_month', size=9, color='red', style={'font-family': 'IntegralCF-RegularOblique'}),
                        # dmc.Text('Churn Rate', id='churn_rate', size='xs', color='red', style={'font-family': 'IntegralCF-RegularOblique'})
                    ]
                ),
            ]
        ),

        # Graphs -----
        dmc.Divider(label='Inventory Graphs', style={"marginBottom": 20, "marginTop": 5}),
        dmc.Group(
            display='column',
            grow=False,
            children=[
                dmc.Select(
                    label='Select Graph',
                    placeholder="Select one",
                    id="select_graph", value="In Sotck Status of Each Products",
                    data=["Paper Inventory Status",'Trend Analyze Input/Output of Boards', 'Output Status', 'Input Status'],
                    style={"width": 400, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Select BoardName',
                    placeholder="Select all you like!",
                    id="select_boardname", value=[],
                    data=select_BoardName,
                    style={"width": 500, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Group Select(Legend = last item)',
                    placeholder="Select Multi Groups",
                    id="select_groupby", value=[],
                    data=[],
                    style={"width": 300, "marginBottom": 0},
                ),

                dmc.Select(
                    label='X_axis Select',
                    placeholder="Select X-axis item",
                    id="x_axis", value='',
                    data=[],
                    style={"width": 300, "marginBottom": 0},
                ),

            ]
        ),

        dmc.Group(
            display='column',
            grow=False,
            children=[
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 450},
                    children = [
                        # dmc.Avatar(src="../assets/images/vgsi_logo.png", size="sm"),
                        dmc.Text(id='graph_title', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dcc.Graph(id='bar_chart_inventory_tob')
                    ]
                ),

            ]
        ),

    ]
)

@logistic_app.callback(

    Input('date_range', 'value'),
    Input('baseInventory_date', 'value'),
    Input('select_graph', 'value'),

    Input('url', 'pathname'),
)

def MaterialStatus(date_range, baseInventory_date, select_graph, n):
    # Board Inventory ------
    BASE_DATE = baseInventory_date
    TODAY = date.today()
    # print(date_range.start_date)
    start_date = datetime.date(int(date_range[0][:4]), int(date_range[0][5:7]), int(date_range[0][8:10]))
    end_date = datetime.date(int(date_range[1][:4]), int(date_range[1][5:7]), int(date_range[1][8:10]))
    baseInventory_date = datetime.date(int(baseInventory_date[:4]), int(baseInventory_date[5:7]), int(baseInventory_date[8:10]))

    # Material DB read ----------------
    df_Mt_Master = pd.read_sql("select * from 900_Logistic_Masterfile_Material;", con=engine)  # Material Master DB
    df_Mt_In = pd.read_sql("select * from 900_Logistic_Input_Material;", con=engine)  # Material Inventory DB
    df_Mt_Out = pd.read_sql("select * from 900_Logistic_Output_Material;", con=engine)  # Material

    df_Mt_In_Master = df_Mt_In.merge(df_Mt_Master, how='left', left_on='LinkInCode', right_on='LinkCode')
    df_Mt_Out_Master = df_Mt_Out.merge(df_Mt_Master, how='left', left_on='LinkOutCode', right_on='LinkCode')


    def fx_invt_qty_in(row):
        if row.Date > row.BaseDate:
            return row.Qty_kg
        elif row.Date < row.BaseDate:
            return row.Qty_kg * (-1)
        else:
            return 0

    def fx_invt_qty_out(row):
        if row.Date > row.BaseDate:
            return row.Qty_kg * (-1)
        elif row.Date < row.BaseDate:
            return row.Qty_kg
        else:
            return 0

    df_Mt_In_Master['Qty_kg_adj'] = df_Mt_In_Master.apply(fx_invt_qty_in, axis=1)
    df_Mt_Out_Master['Qty_kg_adj'] = df_Mt_Out_Master.apply(fx_invt_qty_out, axis=1)

    def fx_input(row):
        return df_Mt_In_Master[(df_Mt_In_Master["Date"] > row.BaseDate) & (df_Mt_In_Master["Date"] <= BASE_DATE) & (df_Mt_In_Master['Material_Code'] == row.Item_Code)]['Qty_kg_adj'].sum()

    def fx_output(row):
        return df_Mt_Out_Master[(df_Mt_Out_Master["Date"] > row.BaseDate) & (df_Mt_Out_Master["Date"] <= BASE_DATE) & (df_Mt_Out_Master['Material_Code'] == row.Item_Code)]['Qty_kg_adj'].sum()

    def fx_inventory(row):
        return row.Base_kg + row.In_sum - row.Out_sum

    df_Mt_Master['In_sum'] = df_Mt_Master.apply(fx_input, axis=1)
    df_Mt_Master['Out_sum'] = df_Mt_Master.apply(fx_output, axis=1)
    df_Mt_Master['Qty_kg'] = df_Mt_Master.apply(fx_inventory, axis=1)

    # df_Mt_Master['Date_Invt'] = BASE_DATE

    color_Market = {'Korea': 'dodgerblue', 'VietNam': 'orangered', }
    color_BoardType = {'SD_Korea': 'gold', 'SD_Viet': 'ivory', 'AM_Korea': 'yellowgreen', 'MR_Korea': 'dodgerblue', 'MR_Viet': 'mediumseagreen', 'FR_Korea': 'red', 'FR_Viet': 'pink', 'Cut_Viet': 'silver', }
    # Bar 1: Market analyze --

    # Graphs ----
    df_bar_21 = df_Mt_Master.query("Category2 in ['CF', 'BB', 'CF_Korea','BB_Korea', 'CF_Korea2']").groupby(by=['Category', 'Supplier'], as_index=False).agg({'Qty_kg': 'sum'}).sort_values(by='Qty_kg', ascending=False)
    df_sct_21 = df_Mt_Master.query("Category2 in ['CF', 'BB', 'CF_Korea','BB_Korea', 'CF_Korea2']").groupby(by=['Category'], as_index=False).agg({'Qty_kg': 'sum'}).sort_values(by='Qty_kg', ascending=False)
    bar_chart_21 = px.bar(df_bar_21, x='Category', y='Qty_kg', color='Supplier', title='Paper Inventory(kg) ')
    bar_chart_21.add_scatter(x=df_sct_21['Category'], y=df_sct_21['Qty_kg'], text=df_sct_21['Qty_kg'], name='Category Total', textposition='top center',
                             mode='markers+text')

    # Indicator 21:  CF 950, 955 --
    # Qty_CF_Korea2 = df_Mt_Master.query("Category2 == 'CF_Korea2'")['Qty_kg'].sum()
    val_IDC_21_1 = df_Mt_Master.query("Category2 == 'CF_Korea2'").agg({'Qty_kg': 'sum'})  # CF Korea2
    IDC_21 = go.Figure(go.Indicator(mode="number", value=float(val_IDC_21_1), number={'font_color': 'black', 'font_size': 15, "valueformat": ",.0f"},
                                    title={'text': 'CF(Korea2)', 'font_size': 15, }, domain={'x': [1, 0], 'y': [0, 1]}, )
                       )
    val_IDC_21_2 = df_Mt_Master.query("Category2 == 'CF_Korea'").agg({'Qty_kg': 'sum'})  # CF Korea
    IDC_22 = go.Figure(go.Indicator(mode="number", value=float(val_IDC_21_2), number={'font_color': 'black', 'font_size': 15, "valueformat": ",.0f"},
                                    title={'text': 'CF(Korea)', 'font_size': 15, }, domain={'x': [1, 0], 'y': [0, 1]}, )
                       )
    val_IDC_21_3 = df_Mt_Master.query("Category2 == 'BB_Korea'").agg({'Qty_kg': 'sum'})  # BB Korea
    IDC_23 = go.Figure(go.Indicator(mode="number", value=float(val_IDC_21_3), number={'font_color': 'black', 'font_size': 15, "valueformat": ",.0f"},
                                    title={'text': 'BB(Korea)', 'font_size': 15, }, domain={'x': [1, 0], 'y': [0, 1]}, )
                       )

    return [bar_chart_21, IDC_21, IDC_22, IDC_23]