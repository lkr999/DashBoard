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
import datetime

import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dash_iconify import DashIconify
from datetime import date
from dash import Dash, Input, Output, ctx, dcc, html, dash_table
from sqlalchemy import create_engine
from pymsgbox import alert, confirm, password, prompt
import numba
import vaex as vx

HOST     = '10.50.3.163'
DB       = 'gfactoryDB'
USER = 'leekr'
PASSWORD = 'g1234'

def db_conn():
    try:
        # self.conn = pymysql.connect(host='192.168.1.95', user=USER, password=PASSWORD, db='zeitgypsumdb', charset='utf8')
        pymysql.install_as_MySQLdb()
        engine = create_engine("mysql://{user}:{password}@{host}/{db}".format(user=USER, password=PASSWORD, host=HOST, db=DB))
        # conn = mysql.connector.connect(**config)
        conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8')
        cur = conn.cursor()

        df = pd.read_sql("select *, concat(TOB,' ', Thick, '*' , Width,'*',Length) BoardName from QC_Takeoff;", con=engine)

        df['Date2'] = df['Date']
        df['Date'] = pd.to_datetime(df['Date'])
        df['Qty_sqm'] = df['Quantity'] * df['Width'] / 1000 * df['Length'] / 1000
        df['Qty_pcs'] = df['Quantity']
        df['Qty_pt'] = df['Qty_pcs'] / abs(df['Quantity'])
        df['WeekOfYear'] = df['Date'].apply(lambda x: x.isocalendar().week)
        df['Month'] = df['Date'].apply(lambda x: x.month)
        df['Quarter'] = df['Date'].apply(lambda x: x.quarter)
        def fx(row):
            if row.Time is not None:
                try:
                    val_tmp = (float(row.Time) + 24) * 3600 * 24 - 7 * 3600
                    val = datetime.datetime.fromtimestamp(val_tmp).strftime('%H:%M')
                except:
                    val = row.Time
            else:
                val = 0
            return val
        df['Time2'] = df.apply(fx, axis=1)

        df_wh_trans = pd.read_sql("select * from 810_WH_Transfer;", con=engine)

        df_wh_trans = df_wh_trans.sort_values(by='id', ascending=False).drop_duplicates('packCode')

        df_wh = df.merge(df_wh_trans,how='left', left_on='PackingCode', right_on='packCode')
        # df_wh['Date'] = pd.to_datetime(df_wh['dateRead'])

        conn.close()

        return df, df_wh

    except mariadb.Error as e: alert(e)

from DashBoard.QC.app import qc_app

layout = dmc.MantineProvider(
    id = 'dark_moder',
    theme={"colorScheme": "dark"},
    inherit=True,
    withNormalizeCSS=True,
    withGlobalStyles=True,
    children=[
        dmc.Title(children = 'Takeoff Inspection Status', order = 1, color='green',  style = {'font-family':'IntegralCF-ExtraBold', 'text-align':'left', 'font-size':20}),
        dmc.Divider(label = 'Overview',  labelPosition='center', size='xl'),

        # Indicater Overview -----
        dmc.Group(
            display ='column',
            grow=False,
            children=[
                # dmc.Space(),
                # dcc.Graph(id="qindi_1",style={'width':200, 'height': 100}),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':300,'height': 200},

                    children = [

                        dmc.Text(id='basedate_result', size='xl', color='red', align='center', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='total_product', size=20, color='blue', align='right', ),
                        dmc.Divider(labelPosition='left', size='xs'),
                        dmc.Text(id='good_product_daily', size=15, color='red', align='right', ),
                        dmc.Text(id='sort_product_daily', size=15, color='green', align='right', ),
                        dmc.Text(id='ng_product_daily', size=15, color='white', align='right', ),
                        dmc.Text(id='x_product_daily', size=15, color='purple', align='right', ),
                    ]
                ),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':300,'height': 200, },

                    children = [
                        dmc.Text(id='monthly_result', size='xl', color='dimmed', align='center', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='product_monthly', size=20, color='blue', align='right', ),
                        dmc.Divider(labelPosition='left', size='xs'),
                        dmc.Text(id='good_product_monthly', size=15, color='red', align='right', ),
                        dmc.Text(id='sort_product_monthly', size=15, color='green', align='right', ),
                        dmc.Text(id='ng_product_monthly', size=15, color='white', align='right', ),
                        dmc.Text(id='x_product_monthly', size=15, color='purple', align='right', ),
                    ]
                ),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':300,'height': 200, },

                    children = [
                        dmc.Text(id='weekly_result', size='xl', color='dimmed', align='center', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='product_weekly', size=20, color='blue', align='right', ),
                        dmc.Divider(labelPosition='left', size='xs'),
                        dmc.Text(id='good_product_weekly', size=15, color='red', align='right', ),
                        dmc.Text(id='sort_product_weekly', size=15, color='green', align='right', ),
                        dmc.Text(id='ng_product_weekly', size=15, color='white', align='right', ),
                        dmc.Text(id='x_product_weekly', size=15, color='purple', align='right', ),
                    ]
                ),

                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':300,'height': 200, },

                    children = [
                        dmc.Text(id='last_product_name', size='xl', color='dimmed', align='center', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Text(id='product_last', size=20, color='blue', align='right', ),
                        dmc.Divider(labelPosition='left', size='xs'),
                        dmc.Text(id='good_product_last', size=15, color='red', align='right', ),
                        dmc.Text(id='sort_product_last', size=15, color='green', align='right', ),
                        dmc.Text(id='ng_product_last', size=15, color='white', align='right', ),
                        dmc.Text(id='x_product_last', size=15, color='purple', align='right', ),
                        dmc.Text(id='update_time', size=15, color='orange', align='center', ),
                    ]
                ),


                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':250,'height': 200},
                    children = [
                        dmc.Text('Good Ratio', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Progress(id='good_daily_ratio',value=0, label="0%", size=18, color='red'),
                        dmc.Text(id='good_daily_qty', size='xs', color='red',),

                        dmc.Space(h=0),
                        dmc.Text('Sort Ratio', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Progress(id='sort_daily_ratio',value=0, label="0%", size=18, color='green'),
                        dmc.Text(id='sort_daily_qty', size='xs', color='green',),

                        dmc.Space(h=0),
                        dmc.Text('NG Ratio', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dmc.Progress(id='ng_daily_ratio',value=0, label="0%", size=18, color='blue'),
                        dmc.Text(id='ng_daily_qty', size='xs', color='purple',),
                    ]
                ),
            ]
        ),

        # Graphs -----
        dmc.Divider(label='Garphs based on Date Range',size='xl', style={"marginBottom": 20, "marginTop": 5}),
        dmc.Group(
            display='column',
            grow=False,
            children=[
                dmc.Select(
                    label='Select Graph',
                    placeholder="Select one",
                    id="select_graph", value="Evaluation Status(Time Base)",
                    data=['Evaluation Status(Time Base)','Evaluation Status(Board Base)', 'Good Board Ratio(Daily)','Good Board Ratio(BoardName)',],
                    style={"width": 350, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Select BoardName',
                    placeholder="Select all you like!",
                    id="select_boardname", value=[],
                    data=[],
                    style={"width": 350, "marginBottom": 0},
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
                    style={"width": 200, "marginBottom": 0},
                ),
                dmc.Checkbox(id="filter_apply", label="Apply Filter", mb=10, value=False),
                # dmc.Button(
                #     "Data Copy",
                #     id='qdata_copy',
                #     variant="outline",
                #     leftIcon=DashIconify(icon="streamline:graph"),
                #     style={"width": 200, "marginBottom": 0},
                # ),

            ]
        ),
        # Graph comments ----
        dmc.Group(
            display='column',
            grow=False,
            children=[
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 600},
                    children = [
                        # dmc.Avatar(src="../assets/images/vgsi_logo.png", size="sm"),
                        dmc.Text(id='graph_title', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dcc.Graph(id='bar_1'),
                        dmc.Divider(labelPosition='left', size='xs', label='Current Graph Comments', color='blue'),
                        dmc.Text(id='graph_comments_1', size='xs', color='black',style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='graph_comments_2', size='xs', color='black',),
                        dmc.Text(id='graph_comments_3', size='xs', color='blue',),
                        dmc.Text(id='graph_comments_4', size='xs', color='red',),
                        dmc.Text(id='graph_comments_5', size='xs', color='black',),
                    ]
                ),

            ]
        ),

        # Tables ----
        dmc.Divider(label='Tables',size='xl', style={"marginBottom": 20, "marginTop": 15}),
        dmc.Group(
            display='column',
            grow=False,
            children=[
                #AgGrid --
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 450},
                    children = [
                        dag.AgGrid(
                            id="aggrid_1",
                            defaultColDef={"resizable": True, "sortable": True, "filter": True},
                            dashGridOptions={"rowHeight": 30},
                            style={'height': 400, 'background-color':'gray', 'font-color':'white'},
                            columnSize='sizeToFit',
                            columnSizeOptions={"skipHeader": True},
                        )
                    ]
                ),
                #Pivot ---
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 600},
                    children = [
                        dash_pivottable.PivotTable(
                            id='table_pv1',
                            cols=['Evaluate'],
                            rows=['Date2', 'BoardName'],
                            vals=['Qty_pt'],
                            aggregatorName='Sum',
                        ),
                    ]
                ),

                # Ware House Status plot ----
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 600},
                    children = [
                        dcc.Graph(id='takeoff_chart_2',),
                    ]
                ),

            ]
        ),
    ]
)

@qc_app.callback(
    # Board Inventory ---
    [Output('select_groupby', 'data'),
    Output('select_boardname', 'data'),
    Output('x_axis', 'data'),

    Output('basedate_result', 'children'),
    Output('total_product', 'children'),
    Output('good_product_daily', 'children'),
    Output('sort_product_daily', 'children'),
    Output('ng_product_daily', 'children'),
    Output('x_product_daily', 'children'),

    Output('good_daily_ratio', 'value'),
    Output('good_daily_ratio', 'label'),
    Output('good_daily_qty', 'children'),

    Output('sort_daily_ratio', 'value'),
    Output('sort_daily_ratio', 'label'),
    Output('sort_daily_qty', 'children'),

    Output('ng_daily_ratio', 'value'),
    Output('ng_daily_ratio', 'label'),
    Output('ng_daily_qty', 'children'),
    # 7

    Output('monthly_result', 'children'),
    Output('product_monthly', 'children'),
    Output('good_product_monthly', 'children'),
    Output('sort_product_monthly', 'children'),
    Output('ng_product_monthly', 'children'),
    Output('x_product_monthly', 'children'),
    # 6

    Output('weekly_result', 'children'),
    Output('product_weekly', 'children'),
    Output('good_product_weekly', 'children'),
    Output('sort_product_weekly', 'children'),
    Output('ng_product_weekly', 'children'),
    Output('x_product_weekly', 'children'),
    # 6

    Output('last_product_name', 'children'),
    Output('product_last', 'children'),
    Output('good_product_last', 'children'),
    Output('sort_product_last', 'children'),
    Output('ng_product_last', 'children'),
    Output('x_product_last', 'children'),
    Output('update_time', 'children'),

    Output('bar_1', 'figure'),
    Output('x_axis', 'value'),
    Output('select_groupby', 'value'),
    Output('graph_title', 'children'),
    Output('table_pv1', 'data'),
    Output('aggrid_1', 'columnDefs'),
    Output('aggrid_1', 'rowData'),
    Output('table_pv1', 'vals'),

    Output('graph_comments_1', 'children'),
    Output('graph_comments_2', 'children'),
    Output('graph_comments_3', 'children'),
    Output('graph_comments_4', 'children'),
    Output('graph_comments_5', 'children'),

    Output('takeoff_chart_2', 'figure'),],

    # Board Inventory ---
    [Input('date_range', 'value'),
    Input('baseInventory_date', 'value'),
    Input('radio_period', 'value'),
    Input('chip_evaluate', 'value'),
    Input('unit_Analyze', 'value'),
    Input('oneday_range', 'checked'),

    Input('select_boardname', 'value'),
    Input('select_groupby', 'value'),
    Input('x_axis', 'value'),
    Input('select_graph', 'value'),

    Input('refresh', 'n_clicks'),
    Input('filter_apply', 'checked'),]

)
def update_contents(date_range, baseInventory_date, radio_period, chip_evaluate, unit_Analyze, oneday_range,
                    select_boardname, select_groupby, x_axis, select_graph,
                    n_clicks, filter_apply):

    # DB Read -----
    df = db_conn()[0]
    df_no_qry = df.copy()
    df_scan = db_conn()[1]

    df.to_csv('D:\\G_FactoryDB_Asset\\PKL\\qc_takeoff.csv')
    df_scan.to_csv('D:\\G_FactoryDB_Asset\\PKL\\810_wh_transfer.csv')


    # Initial define ------
    select_groupby_val = []
    x_axis_val = ''
    graph_title = ''

    graph_comments_1 = ''
    graph_comments_2 = ''
    graph_comments_3 = ''
    graph_comments_4 = ''
    graph_comments_5 = ''
    last_boardname = ''

    Period = 'Date2'
    if radio_period == 'Daily':
        Period = 'Date2'
    elif radio_period == 'Weekly':
        Period = 'WeekOfYear'
    elif radio_period == 'Monthly':
        Period = 'Month'
    elif radio_period == 'Quarterly':
        Period = 'Quarter'
    elif radio_period == 'Yearly':
        Period = 'Year'
    else:
        Period = 'Date2'

    try:
        TODAY = date.today()
        start_date = datetime.date(int(date_range[0][:4]), int(date_range[0][5:7]), int(date_range[0][8:10]))
        end_date = datetime.date(int(date_range[1][:4]), int(date_range[1][5:7]), int(date_range[1][8:10]))
        baseInventory_date = datetime.date(int(baseInventory_date[:4]), int(baseInventory_date[5:7]), int(baseInventory_date[8:10]))

        takeoff_chart_1 = go.Figure()
        takeoff_chart_2 = go.Figure()
        if oneday_range:
            start_date = baseInventory_date
            end_date = baseInventory_date

            # Monthly Result ----
        start_year = date(baseInventory_date.year, 1, 1)
        start_month = date(baseInventory_date.year, baseInventory_date.month, 1)


        if len(select_boardname)>=1:
            qry_board_date = "(BoardName in @select_boardname) and (Evaluate in @chip_evaluate) and Date>=@start_date and Date<=@end_date"
            qry_monthly_txt = "(BoardName in @select_boardname) and (Evaluate in @chip_evaluate) and Date>=@start_month and Date<=@baseInventory_date"
            qry_board_level = "(BoardName in @select_boardname) and Evaluate in @chip_evaluate"
            qry_weekly_txt = "(BoardName in @select_boardname) and (Evaluate in @chip_evaluate) and Date>=@start_year and Date<=@end_date and WeekOfYear==@week_day"

        else:
            qry_board_date = "Evaluate in @chip_evaluate and Date>=@start_date and Date<=@end_date"
            qry_monthly_txt = "(Evaluate in @chip_evaluate) and Date>=@start_month and Date<=@baseInventory_date"
            qry_board_level = "Evaluate in @chip_evaluate"
            qry_weekly_txt = "(Evaluate in @chip_evaluate) and Date>=@start_year and Date<=@end_date and WeekOfYear==@week_day"


        Evaluate_color = {'G': 'red', 'G2': 'cyan', 'G3': 'blue', 'S': 'yellow', 'X': 'gray', 'NG': 'purple'}

        board_List = df.query("Evaluate in @chip_evaluate and Date>=@start_date and Date<=@end_date").sort_values('BoardName')['BoardName'].unique()

        select_groupby_list = ['Date2','WeekOfYear', 'Month', 'Quarter', 'Evaluate','BoardName']
        x_axis_list = ['Date2','WeekOfYear', 'Month', 'Quarter', 'Evaluate','BoardName']

        # Daily Calculate -----
        daily_product = df_no_qry.query("Date==@baseInventory_date")[unit_Analyze].sum()
        daily_product_good = df_no_qry.query("Date==@baseInventory_date and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
        daily_product_sort = df_no_qry.query("Date==@baseInventory_date and Evaluate in ['S',]" )[unit_Analyze].sum()
        daily_product_ng = df_no_qry.query("Date==@baseInventory_date and Evaluate in ['NG',]")[unit_Analyze].sum()
        daily_product_x = df_no_qry.query("Date==@baseInventory_date and Evaluate in ['X',]")[unit_Analyze].sum()

        daily_ratio_good = 0
        daily_ratio_sort = 0
        daily_ratio_ng = 0
        daily_ratio_x = 0

        if daily_product>0:
            daily_ratio_good = daily_product_good / daily_product
            daily_ratio_sort = daily_product_sort / daily_product
            daily_ratio_ng   = daily_product_ng / daily_product
            daily_ratio_x   = daily_product_x / daily_product

        basedate_result = str(baseInventory_date) + ' Results'
        daily_result_1 = "Products:  {:,.0f}".format(daily_product)
        daily_result_2 = "Good:  {:,.0f} ({:0.0%})".format(daily_product_good, daily_ratio_good)
        daily_result_3 = "Sort:  {:,.0f} ({:0.0%})".format(daily_product_sort, daily_ratio_sort)
        daily_result_4 = "NG:  {:,.0f} ({:0.0%})".format(daily_product_ng, daily_ratio_ng)
        daily_result_5 = "CUT:  {:,.0f} ({:0.0%})".format(daily_product_x, daily_ratio_x)

        # Monthly Result ---
        monthly_product = df_no_qry.query(qry_monthly_txt)[unit_Analyze].sum()
        monthly_product_good = df_no_qry.query(qry_monthly_txt + " and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
        monthly_product_sort = df_no_qry.query(qry_monthly_txt + " and Evaluate in ['S',]")[unit_Analyze].sum()
        monthly_product_ng = df_no_qry.query(qry_monthly_txt + " and Evaluate in ['NG',]")[unit_Analyze].sum()
        monthly_product_x = df_no_qry.query(qry_monthly_txt + " and Evaluate in ['X',]")[unit_Analyze].sum()

        monthly_ratio_good = 0
        monthly_ratio_sort = 0
        monthly_ratio_ng = 0
        monthly_ratio_x = 0

        if monthly_product > 0:
            monthly_ratio_good = monthly_product_good / monthly_product
            monthly_ratio_sort = monthly_product_sort / monthly_product
            monthly_ratio_ng = monthly_product_ng / monthly_product
            monthly_ratio_x = monthly_product_x / monthly_product

        monthly_result = str(baseInventory_date.strftime('%B')) + ' _Cumulated'
        monthly_result_1 = "Products:  {:,.0f}".format(monthly_product)
        monthly_result_2 = "Good:  {:,.0f} ({:0.0%})".format(monthly_product_good, monthly_ratio_good)
        monthly_result_3 = "Sort:  {:,.0f} ({:0.0%})".format(monthly_product_sort, monthly_ratio_sort)
        monthly_result_4 = "NG:  {:,.0f} ({:0.0%})".format(monthly_product_ng, monthly_ratio_ng)
        monthly_result_5 = "CUT:  {:,.0f} ({:0.0%})".format(monthly_product_x, monthly_ratio_x)


        # weekly Result ----
        year_base = baseInventory_date.year
        month_base = baseInventory_date.month

        start_year = date(year_base, 1, 1)
        start_month = date(year_base, month_base, 1)
        week_day = baseInventory_date.isocalendar().week

        weekly_product = df_no_qry.query(qry_weekly_txt)[unit_Analyze].sum()
        weekly_product_good = df_no_qry.query(qry_weekly_txt + " and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
        weekly_product_sort = df_no_qry.query(qry_weekly_txt + " and Evaluate in ['S',]")[unit_Analyze].sum()
        weekly_product_ng = df_no_qry.query(qry_weekly_txt + " and Evaluate in ['NG',]")[unit_Analyze].sum()
        weekly_product_x = df_no_qry.query(qry_weekly_txt + " and Evaluate in ['X',]")[unit_Analyze].sum()

        weekly_ratio_good = 0
        weekly_ratio_sort = 0
        weekly_ratio_ng = 0
        weekly_ratio_x = 0

        if weekly_product > 0:
            weekly_ratio_good = weekly_product_good / weekly_product
            weekly_ratio_sort = weekly_product_sort / weekly_product
            weekly_ratio_ng = weekly_product_ng / weekly_product
            weekly_ratio_x = weekly_product_x / weekly_product

        weekly_result = 'Week_' + str(baseInventory_date.isocalendar().week) + ' _Cumulated'
        weekly_result_1 = "Products:  {:,.0f}".format(weekly_product)
        weekly_result_2 = "Good:  {:,.0f} ({:0.0%})".format(weekly_product_good, weekly_ratio_good)
        weekly_result_3 = "Sort:  {:,.0f} ({:0.0%})".format(weekly_product_sort, weekly_ratio_sort)
        weekly_result_4 = "NG:  {:,.0f} ({:0.0%})".format(weekly_product_ng, weekly_ratio_ng)
        weekly_result_5 = "CUT:  {:,.0f} ({:0.0%})".format(weekly_product_x, weekly_ratio_x)

        # Last product Result ----
        qry_last_txt = 'Date>=@start_month and Date<=@baseInventory_date'
        last_boardname = str(df_no_qry.query(qry_last_txt).sort_values(by=['Date','Time2'])['BoardName'].values[-1])
        qry_last_txt = "BoardName==@last_boardname and Date==@baseInventory_date"

        last_product = df_no_qry.query(qry_last_txt)[unit_Analyze].sum()
        last_product_good = df_no_qry.query(qry_last_txt + " and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
        last_product_sort = df_no_qry.query(qry_last_txt + " and Evaluate in ['S',]")[unit_Analyze].sum()
        last_product_ng = df_no_qry.query(qry_last_txt + " and Evaluate in ['NG',]")[unit_Analyze].sum()
        last_product_x = df_no_qry.query(qry_last_txt + " and Evaluate in ['X',]")[unit_Analyze].sum()

        last_ratio_good = 0
        last_ratio_sort = 0
        last_ratio_ng = 0
        last_ratio_x = 0

        if last_product > 0:
            last_ratio_good = last_product_good / last_product
            last_ratio_sort = last_product_sort / last_product
            last_ratio_ng = last_product_ng / last_product
            last_ratio_x = last_product_x / last_product

        last_result = last_boardname
        last_result_1 = str(baseInventory_date) + " Products:  {:,.0f}".format(last_product)
        last_result_2 = "Good:  {:,.0f} ({:0.0%})".format(last_product_good, last_ratio_good)
        last_result_3 = "Sort:  {:,.0f} ({:0.0%})".format(last_product_sort, last_ratio_sort)
        last_result_4 = "NG:  {:,.0f} ({:0.0%})".format(last_product_ng, last_ratio_ng)
        last_result_5 = "CUT:  {:,.0f} ({:0.0%})".format(last_product_x, last_ratio_x)
        last_result_6 = "Updated at: " + datetime.datetime.now().strftime("%H:%M")

        idc_daily_good_ratio = last_ratio_good * 100
        idc_daily_good_ratio_2 = "{:0.1%}".format(last_ratio_good)
        idc_daily_good_qty = "Qty: {:,.0f}".format(last_product_good)

        idc_daily_sort_ratio = last_ratio_sort * 100
        idc_daily_sort_ratio_2 = "{:0.1%}".format(last_ratio_sort)
        idc_daily_sort_qty = "Qty: {:,.0f}".format(last_product_sort)

        idc_daily_ng_ratio = last_ratio_ng * 100
        idc_daily_ng_ratio_2 = "{:0.1%}".format(last_ratio_ng)
        idc_daily_ng_qty = "Qty: {:,.0f}".format(last_product_ng)


        # Graphs -----
        # data = ["Good Board Ratio(Daily)", 'Sorting Board Status(This Month)', 'Output Status', 'Input Status'],
        qry_daterange_good = "Date>=@start_date and Date<=@end_date and Evaluate in ['G','G2','G3']"
        qry_daterange = "Date>=@start_date and Date<=@end_date"

        def f_good_ratio(group):
            group['Good'] = group[(group['Evaluate'] == 'G') | (group['Evaluate'] == 'G2') | (group['Evaluate'] == 'G3')][unit_Analyze].sum()
            group['Sort'] = group[(group['Evaluate'] == 'S')][unit_Analyze].sum()
            # group['Good'] = group.qeery("Evaluate in ['G', 'G2', 'G3']")['Qty_sqm'].sum()
            group['grSum'] = group[unit_Analyze].sum()
            group['GoodRatio'] = group['Good'] / group['grSum'] * 100
            group['SortRatio'] = group['Sort'] / group['grSum'] * 100
            group['GoodRatio'] = group['GoodRatio'].round(2)

            return group

        if oneday_range:
            qry_daterange_1 = "Date>=@start_month and Date<=@end_date"
            qry_daterange_2 = "Date>=@start_month and Date<=@end_date" + " and " + qry_board_level
        else:
            qry_daterange_1 = "Date>=@start_date and Date<=@end_date"
            qry_daterange_2 = "Date>=@start_date and Date<=@end_date" + " and " + qry_board_level


        if select_graph=='Good Board Ratio(Daily)':
            graph_title = 'Good Board Ratio(Period)'

            selected_group_items = [Period, 'Evaluate', 'BoardName']
            selected_xaxis_items = [Period, 'Evaluate', 'BoardName']

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = [Period]
                x_val = Period

            # Bar 1: Daily Evaluate Result ---
            df_sct_1 = df_no_qry.query(qry_daterange_2).groupby(by=gr_by, as_index=False).apply(f_good_ratio)
            sct_chart1 = px.scatter(df_sct_1, x=x_val, y='GoodRatio', text='grSum', )
            sct_chart1.update_traces(textposition='top center', mode='markers+lines+text', texttemplate='%{y:,.1f} (%{text:,.0f})', )

            takeoff_chart_1 = sct_chart1

            # Graph Comments 1--------------------------------------
            df_grp = df.query(qry_board_date)
            g_product = df_grp.query(qry_daterange_2)[unit_Analyze].sum()
            g_good = df_grp.query(qry_daterange_1 + " and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
            g_sort = df_grp.query(qry_daterange_1 + " and Evaluate in ['S',]")[unit_Analyze].sum()
            g_ng = df_grp.query(qry_daterange_1 + " and Evaluate in ['NG',]")[unit_Analyze].sum()
            g_x = df_grp.query(qry_daterange_1 + " and Evaluate in ['X',]")[unit_Analyze].sum()

            g_ratio_good = 0
            g_ratio_sort = 0
            g_ratio_ng = 0
            g_ratio_x = 0

            if g_product > 0:
                g_ratio_good = g_good / g_product
                g_ratio_sort = g_sort / g_product
                g_ratio_ng = g_ng / g_product
                g_ratio_x = g_x / g_product

            graph_comments_1 = "Products:  {:,.0f}".format(g_product)
            graph_comments_2 = "Good:  {:,.0f} ({:0.0%})".format(g_good, g_ratio_good)
            graph_comments_3 = "Sort:  {:,.0f} ({:0.0%})".format(g_sort, g_ratio_sort)
            graph_comments_4 = "NG:  {:,.0f} ({:0.0%})".format(g_ng, g_ratio_ng)
            graph_comments_5 = "CUT:  {:,.0f} ({:0.0%})".format(g_x, g_ratio_x)


        if select_graph=='Good Board Ratio(BoardName)':
            graph_title = 'Good Board Ratio(BoardName)'

            selected_group_items = [Period, 'Evaluate', 'BoardName']
            selected_xaxis_items = [Period, 'Evaluate', 'BoardName']

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = ['BoardName']
                x_val = 'BoardName'


            # Bar 1: Daily Evaluate Result ---
            df_sct_1 = df_no_qry.query(qry_daterange_2).groupby(by=gr_by, as_index=False).apply(f_good_ratio)
            sct_chart1 = px.scatter(df_sct_1, x=x_val, y='GoodRatio', text='grSum', )
            sct_chart1.update_traces(textposition='top center', mode='markers+lines+text', texttemplate='%{y:,.1f} (%{text:,.0f})', )

            takeoff_chart_1 = sct_chart1

            # Graph Comments 2--------------------------------------
            df_grp = df.query(qry_board_date)
            g_product = df_grp.query(qry_daterange_2)[unit_Analyze].sum()
            g_good = df_grp.query(qry_daterange_1 + " and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
            g_sort = df_grp.query(qry_daterange_1 + " and Evaluate in ['S',]")[unit_Analyze].sum()
            g_ng = df_grp.query(qry_daterange_1 + " and Evaluate in ['NG',]")[unit_Analyze].sum()
            g_x = df_grp.query(qry_daterange_1 + " and Evaluate in ['X',]")[unit_Analyze].sum()

            g_ratio_good = 0
            g_ratio_sort = 0
            g_ratio_ng = 0
            g_ratio_x = 0

            if g_product > 0:
                g_ratio_good = g_good / g_product
                g_ratio_sort = g_sort / g_product
                g_ratio_ng = g_ng / g_product
                g_ratio_x = g_x / g_product

            graph_comments_1 = "Products:  {:,.0f}".format(g_product)
            graph_comments_2 = "Good:  {:,.0f} ({:0.0%})".format(g_good, g_ratio_good)
            graph_comments_3 = "Sort:  {:,.0f} ({:0.0%})".format(g_sort, g_ratio_sort)
            graph_comments_4 = "NG:  {:,.0f} ({:0.0%})".format(g_ng, g_ratio_ng)
            graph_comments_5 = "CUT:  {:,.0f} ({:0.0%})".format(g_x, g_ratio_x)


        if select_graph=='Evaluation Status(Board Base)':
            graph_title = 'Evaluation Status(Board Base) '

            selected_group_items = [Period, 'Evaluate', 'BoardName']
            selected_xaxis_items = [Period, 'Evaluate', 'BoardName']

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = ['BoardName', 'Evaluate', ]
                x_val = 'BoardName'

            df_bar_1 = df_no_qry.query(qry_board_date).groupby(by=gr_by, as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum',})

            if df_bar_1.empty:pass
            else:
                bar_chart_1 = px.bar(df_bar_1, x=x_val, y=unit_Analyze, color=gr_by[-1], text='Qty_pt', text_auto=True, barmode='group')
                bar_chart_1.update_traces(texttemplate='%{y:,.0f} (%{text:,.0f})', )

                takeoff_chart_1 = bar_chart_1

                # Graph Comments 3--------------------------------------
                df_grp = df.query(qry_board_date)
                g_product = df_grp.query(qry_daterange_2)[unit_Analyze].sum()
                g_good = df_grp.query(qry_daterange_1 + " and Evaluate in ['G','G2','G3']")[unit_Analyze].sum()
                g_sort = df_grp.query(qry_daterange_1 + " and Evaluate in ['S',]")[unit_Analyze].sum()
                g_ng = df_grp.query(qry_daterange_1 + " and Evaluate in ['NG',]")[unit_Analyze].sum()
                g_x = df_grp.query(qry_daterange_1 + " and Evaluate in ['X',]")[unit_Analyze].sum()

                g_ratio_good = 0
                g_ratio_sort = 0
                g_ratio_ng = 0
                g_ratio_x = 0

                if g_product > 0:
                    g_ratio_good = g_good / g_product
                    g_ratio_sort = g_sort / g_product
                    g_ratio_ng = g_ng / g_product
                    g_ratio_x = g_x / g_product

                graph_comments_1 = "Products:  {:,.0f}".format(g_product)
                graph_comments_2 = "Good:  {:,.0f} ({:0.0%})".format(g_good, g_ratio_good)
                graph_comments_3 = "Sort:  {:,.0f} ({:0.0%})".format(g_sort, g_ratio_sort)
                graph_comments_4 = "NG:  {:,.0f} ({:0.0%})".format(g_ng, g_ratio_ng)
                graph_comments_5 = "CUT:  {:,.0f} ({:0.0%})".format(g_x, g_ratio_x)

        Evaluate_color = {'G': 'red', 'G2': 'cyan', 'G3': 'blue', 'S': 'green', 'X': 'gray', 'NG': 'purple'}

        if select_graph=='Evaluation Status(Time Base)':
            graph_title = 'Evaluation Status(Time Base)'

            def f_ev_point(row):
                if row.Evaluate=='G':    val = 7
                elif row.Evaluate=='G2': val = 6
                elif row.Evaluate=='G3': val = 5
                elif row.Evaluate=='S':  val = 4
                elif row.Evaluate=='X':  val = 3
                elif row.Evaluate=='NG': val = 2
                else: val = 0
                return val
            df_no_qry['EV_point'] = df_no_qry.apply(f_ev_point, axis=1)

            df_bar_2 = df_no_qry.query(qry_last_txt)[['Date2', 'BoardName', 'LotNo', 'Time2', 'Evaluate', 'Discription', 'Quantity', 'Qty_sqm', 'Qty_pcs', 'Qty_pt','EV_point']].sort_values(by=['LotNo'], ascending=True)

            if df_bar_2.empty: pass
            else:
                bar_chart_2 = px.scatter(df_bar_2, x='LotNo', y='EV_point', color='Evaluate', hover_data={'Time2', 'Discription'}, color_discrete_map=Evaluate_color)
                bar_chart_2.update_traces(texttemplate='%{y:,.0f} ',)

                takeoff_chart_1 = bar_chart_2

        # Pivot Table -----
        if oneday_range: qry_pv = 'Date==@baseInventory_date'
        else: qry_pv = 'Date>=@start_date and Date<=@end_date'

        df_pv_1 = df_no_qry.query(qry_pv)[['Date2', 'BoardName', 'LotNo', 'Time2', 'Evaluate', 'Discription', 'Quantity', 'Qty_sqm', 'Qty_pcs', 'Qty_pt']]
        data_pv1 = df_pv_1.to_dict('records')
        pv1_vals = [unit_Analyze]

        # AgGrid Table ----
        qry_basedate_evaluate= 'Date==@baseInventory_date and Evaluate in @chip_evaluate'
        df_aggrid_1 = df_no_qry.query(qry_basedate_evaluate)[['Date2', 'BoardName', 'LotNo', 'Time2', 'Evaluate', 'Discription', 'Quantity']].sort_values(['Date2', 'BoardName'])

        # dt1_columns = [{'name': 'Date', 'id': 'Date2'}, {'name': 'BoardName', 'id': 'BoardName'}, {'Evaluate': 'Date', 'id': 'Evaluate'}, {'name': 'Pallet No.', 'id': 'Quantity'}, {'name': 'Qty_sq', 'id': 'Qty_sqm'} ]
        width_col = [120, 180, 100, 100, 100, 700, 150]
        aggrid_col = [{'headerName': i, 'field': i, 'width': width_col[k]} for k, i in enumerate(df_aggrid_1.columns)]
        aggrid_data = df_aggrid_1.to_dict('records')


        # Scan Status ---

        if df_scan.empty: pass
        else:
            df_scan_chart = df_scan.query(qry_pv).groupby(by=['numWH', 'BoardName'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).sort_values('numWH', ascending=False)
            bar_chart_wh = px.bar(df_scan_chart, x='numWH', y=unit_Analyze, color='BoardName', barmode='group')
            bar_chart_wh.update_traces(texttemplate='%{y:,.0f} ', )

            takeoff_chart_2 = bar_chart_wh

        # Graph Color Change ---
        takeoff_chart_1.layout.plot_bgcolor = '#ddd'
        takeoff_chart_1.layout.paper_bgcolor = '#101010'
        takeoff_chart_1.update_xaxes(title_font_color='white', color='white')
        takeoff_chart_1.update_yaxes(title_font_color='white', color='white')
        takeoff_chart_1.layout.legend.bgcolor = 'white'

        takeoff_chart_2.layout.plot_bgcolor = '#333'
        takeoff_chart_2.layout.paper_bgcolor = '#101010'
        takeoff_chart_2.update_xaxes(title_font_color='white', color='white')
        takeoff_chart_2.update_yaxes(title_font_color='white', color='white')
        takeoff_chart_2.layout.legend.bgcolor = 'white'


        return [select_groupby_list, board_List, x_axis_list,
                basedate_result, daily_result_1, daily_result_2, daily_result_3, daily_result_4, daily_result_5, # 6
                idc_daily_good_ratio, idc_daily_good_ratio_2, idc_daily_good_qty,
                idc_daily_sort_ratio, idc_daily_sort_ratio_2, idc_daily_sort_qty,
                idc_daily_ng_ratio, idc_daily_ng_ratio_2, idc_daily_ng_qty,
                monthly_result, monthly_result_1, monthly_result_2, monthly_result_3, monthly_result_4, monthly_result_5,  # 6
                weekly_result,weekly_result_1,weekly_result_2,weekly_result_3,weekly_result_4,weekly_result_5,  # 6
                last_result, last_result_1, last_result_2, last_result_3, last_result_4, last_result_5, last_result_6, # 6
                takeoff_chart_1, x_axis_val, select_groupby_val, graph_title,
                data_pv1,aggrid_col, aggrid_data, pv1_vals,
                graph_comments_1, graph_comments_2, graph_comments_3, graph_comments_4, graph_comments_5,
                takeoff_chart_2]

    except Exception as e:
        # alert(e)
        return
