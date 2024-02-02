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
import datetime
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import dash_ag_grid as dag

from dash_iconify import DashIconify
from datetime import date
from dash import Dash, Input, Output, ctx, dcc, html, dash_table
from sqlalchemy import create_engine
from pymsgbox import alert, confirm, password, prompt

HOST = '10.50.3.163'
DB = 'gfactoryDB'
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

        # Board DB Download ----------------
        df_BI = pd.read_sql("select * from 900_BaseInventory_Board;", con=engine)  # Board Inventory DB
        df_Input = pd.read_sql("select * from 900_Logistic_Input_Board;", con=engine)  # Board Inventory DB
        df_Output = pd.read_sql("select * from 900_Logistic_Output_Board;", con=engine)  # Board Inventory DB


        conn.close()

        return [df_BI, df_Input, df_Output]

    except mariadb.Error as e:
        alert(e)

from DashBoard.QC_local.app import qc_app2

layout = dmc.MantineProvider(
    id='dark_moder',
    theme={"colorScheme": "dark"},
    inherit=True,
    withNormalizeCSS=True,
    withGlobalStyles=True,
    children=[
        dmc.Title(children='Board Inventory Status', order=1, color='green', style={'font-family': 'IntegralCF-ExtraBold', 'text-align': 'left', 'font-size': 20}),
        dmc.Divider(label='Overview', labelPosition='center', size='xl'),

        # Indicater Overview -----
        dmc.Group(
            display='column',
            grow=False,
            children=[
                # dmc.Space(),
                dcc.Graph(id="lg_indi_1", style={'width': 250, 'height': 100}),

                # Korea vs Vietnam -----
                dmc.Paper(
                    radius='sm', withBorder=True, shadow='xs', p='sm', style={'width': 350, 'height': 150},
                    children=[
                        dmc.Text('Korea vs Vietnam', size=15, color='white', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size=2, color='white'),
                        dmc.Text(id='lg_market_korea', size=20, color='blue', ),
                        dmc.Text(id='lg_market_vietnam', size=20, color='red', ),
                        dmc.Text(id='lg_update_date', size=15, color='orange',),
                    ]
                ),

                # Yearly Cumulated -----
                dmc.Paper(
                    radius='sm', withBorder=True, shadow='xs', p='sm', style={'width': 450, 'height': 150},
                    children=[
                        dmc.Text('Yearly Cumulated (Korea+Viet) KR%  ', size=15, color='white', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size=2, color='white'),
                        dmc.Text(id='lg_cumulate_in_year', size=20, color='blue', ),
                        dmc.Text(id='lg_cumulate_out_year', size=20, color='red',),
                        dmc.Text(id='lg_gap_year', size=20, color='orange', ),
                    ]
                ),

                # Monthly Cumulated -----
                dmc.Paper(
                    radius='sm', withBorder=True, shadow='xs', p='sm', style={'width': 450, 'height': 150},
                    children=[
                        dmc.Text('Monthly Cumulated (Korea+Viet) KR% ', size=15, color='white', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size=2),
                        dmc.Text(id='lg_cumulate_in_month', size=20, color='blue',),
                        dmc.Text(id='lg_cumulate_out_month', size=20, color='red', ),
                        dmc.Text(id='lg_gap_month', size=20, color='orange', ),
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
                    id="lg_select_graph", value="In Stock Status of Each Products",
                    data=["In Stock Status of Each Products", 'Trend Analyze Input/Output of Boards', 'Output Status', 'Input Status'],
                    style={"width": 300, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Select BoardName',
                    placeholder="Select all you like!",
                    id="lg_select_boardname", value=[],
                    data=[],
                    style={"width": 300, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Group Select(Legend = last item)',
                    placeholder="Select Multi Groups",
                    id="lg_select_groupby", value=[],
                    data=[],
                    style={"width": 300, "marginBottom": 0},
                ),

                dmc.Select(
                    label='X_axis Select',
                    placeholder="Select X-axis item",
                    id="lg_x_axis", value='',
                    data=[],
                    style={"width": 200, "marginBottom": 0},
                ),
                dmc.Checkbox(id="lg_filter_apply", label="Apply Filter", mb=10, value=False),
                dmc.Button(
                    "Data Copy",
                    id='lg_data_copy',
                    variant="outline",
                    leftIcon=DashIconify(icon="streamline:graph"),
                    style={"width": 150, "marginBottom": 0},
                ),

            ]
        ),

        dmc.Group(
            display='column',
            grow=False,
            children=[
                dmc.Paper(
                    radius='sm', withBorder=True, shadow='xs', p='sm', style={'width': 1550, 'height': 600},
                    children=[
                        # dmc.Avatar(src="../assets/images/vgsi_logo.png", size="sm"),
                        dmc.Text(id='lg_graph_title', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dcc.Graph(id='lg_bar_chart_inventory_tob'),
                        dmc.Divider(labelPosition='left', size='xs', label='Current Graph Comments', color='blue'),
                        dmc.Text(id='lg_graph_comments_1', size='xs', color='black', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='lg_graph_comments_2', size='xs', color='black', ),
                        dmc.Text(id='lg_graph_comments_3', size='xs', color='blue', ),
                        dmc.Text(id='lg_graph_comments_4', size='xs', color='red', ),
                    ]
                ),

            ]
        ),

    ]
)

@qc_app2.callback(
    # Board Inventory ---
    [
         Output('lg_indi_1', 'figure'),
         Output('lg_market_korea', 'children'),
         Output('lg_market_vietnam', 'children'),
         Output('lg_update_date', 'children'),
         #
         Output('lg_cumulate_in_year', 'children'),
         Output('lg_cumulate_out_year', 'children'),
         Output('lg_gap_year', 'children'),
         Output('lg_cumulate_in_month', 'children'),
         Output('lg_cumulate_out_month', 'children'),
         Output('lg_gap_month', 'children'),
         #
         # Output('lg_bar_chart_inventory_tob', 'figure'),
         # Output('lg_graph_title', 'children'),
         # Output('lg_select_boardname', 'data'),
         # Output('lg_select_groupby', 'data'),
         # Output('lg_x_axis', 'data'),
         #
         # Output('lg_graph_comments_1', 'children'),
         # Output('lg_graph_comments_2', 'children'),
         # Output('lg_graph_comments_3', 'children'),
         # Output('lg_graph_comments_4', 'children'),
    ],

    # Board Inventory ---
    [
         Input('refresh', 'n_clicks'),
         Input('date_range', 'value'),
         Input('baseInventory_date', 'value'),
         Input('radio_period', 'value'),
         Input('level_checkList', 'value'),
         Input('unit_Analyze', 'value'),

         # Input('lg_select_graph', 'value'),
         # Input('lg_select_boardname', 'value'),
         # Input('lg_select_groupby', 'value'),
         # Input('lg_x_axis', 'value'),
         # Input('lg_oneday_range', 'checked'),
         # Input('lg_filter_apply', 'checked'),
         #
         Input('url', 'pathname'),
    ]

)
def BoardStatus(refresh, date_range, baseInventory_date, radio_period, level_checkList, unit_Analyze,
                # lg_select_graph, lg_select_boardname, lg_select_groupby, lg_x_axis, lg_oneday_range, checked,
                n):
    try:
        # Const ---------
        TODAY = date.today()
        start_date = datetime.date(int(date_range[0][:4]), int(date_range[0][5:7]), int(date_range[0][8:10]))
        end_date = datetime.date(int(date_range[1][:4]), int(date_range[1][5:7]), int(date_range[1][8:10]))
        baseInventory_date = datetime.date(int(baseInventory_date[:4]), int(baseInventory_date[5:7]), int(baseInventory_date[8:10]))

        # filter_apply = True if checked else False

        # DB Call -----
        df_BI, df_Input, df_Output, df_Input_BI, df_Output_BI = db_call(start_date, end_date, baseInventory_date)


        # Indicator ----
        lg_indi_1 = indi_1(unit_Analyze, TODAY, df_BI, level_checkList)

        # Market ratio ---
        market_korea_txt, market_vietnam_txt, update_date = f_inventory_market(df=df_BI, level_checkList=level_checkList, unit_Analyze=unit_Analyze)

        #Yearly/Monthly Cumulate In an Out ----
        start_date_year = date(baseInventory_date.year, 1, 1)
        start_date_month = date(baseInventory_date.year, baseInventory_date.month, 1)
        # df_Output.to_csv('chk2.csv')
        Y_in, Y_out, Y_gap = f_cum_in_out(df_in=df_Input_BI, df_out=df_Output_BI, unit_Analyze=unit_Analyze, level_checkList=level_checkList, period_txt='Year',
                                          period=baseInventory_date.year, start_date=start_date_year, end_date=baseInventory_date)
        M_in, M_out, M_gap = f_cum_in_out(df_in=df_Input_BI, df_out=df_Output_BI, unit_Analyze=unit_Analyze, level_checkList=level_checkList, period_txt='Month',
                                          period=baseInventory_date.month, start_date=start_date_month, end_date=baseInventory_date)

        return [lg_indi_1,
                market_korea_txt, market_vietnam_txt, update_date,
                Y_in, Y_out, Y_gap,
                M_in, M_out, M_gap,]
    except Exception as e: pass



def bar_chart_update(df_bar=go.Figure(), unit_Analyze='Qty_sqm', x='', ):
    try:
        fig = px.bar(df_bar, x=x, y=unit_Analyze, color=gr_by[-1], text_auto=True, text='Ratio',
                                         orientation='v', hover_data={'Ratio': ':0.0%', unit_Analyze: ':,.0f'})
        fig.update_traces(texttemplate='%{y:,.0f} (%{text:0.0%})', )

        return fig
    except Exception as e:
        return go.Figure()

def f_cum_in_out(df_in=pd.DataFrame(), df_out=pd.DataFrame(), level_checkList=[], unit_Analyze='Qty_sqm', period_txt='Year', period=2024, start_date=date.today(), end_date=date.today()):
    try:
        qry_txt = "Date>=@start_date and Date<@end_date and Level in @level_checkList and " + period_txt + "==" + str(period)
        df_cum_in = df_in.query(qry_txt).groupby(by=['MarketGroup'], as_index=False)[unit_Analyze].sum()
        df_cum_out = df_out.query(qry_txt).groupby(by=['MarketGroup'], as_index=False)[unit_Analyze].sum()

        kr_in = df_cum_in.values[0][1]
        vn_in = df_cum_in.values[1][1]
        in_sum = kr_in + vn_in

        kr_out = df_cum_out.values[0][1]
        vn_out = df_cum_out.values[1][1]
        out_sum = kr_out + vn_out

        print(df_cum_out)

        gap = in_sum - out_sum
        in_txt = "IN: {:,.0f} ( {:,.0f} + {:,.0f} ) >> {: 0.0%} ".format(in_sum, kr_in, vn_in, kr_in/in_sum)
        out_txt = "OUT: {:,.0f} ( {:,.0f} + {:,.0f} ) >> {: 0.0%}  ".format(out_sum, kr_out, vn_out, kr_out/out_sum)
        gap_txt = "IN - OUT: {:,.0f} ".format(gap)

        return [in_txt, out_txt, gap_txt]

    except Exception as e:
        # alert('chk function: f_cum_in_out')
        return [None, None, None]

def f_inventory_market(df=pd.DataFrame(), level_checkList=[], unit_Analyze='Qty_sqm', update = date.today()):
    try:
        qry_Level = "Level in @level_checkList"

        df_market = df.query(qry_Level).groupby(by=['MarketGroup'], as_index=False)[unit_Analyze].sum()

        inventory_korea = df_market.values[0][1]
        inventory_vietnam = df_market.values[1][1]
        inventory_total = inventory_korea + inventory_vietnam

        if inventory_total > 0:
            market_korea_r = inventory_korea / inventory_total
            market_vietnam_r = inventory_vietnam / inventory_total
        else:
            market_korea_r = 0
            market_vietnam_r = 0

        market_korea_txt = "Korea    : {:,.0f} ({: 0.0%})".format(inventory_korea, market_korea_r)
        market_vietnam_txt = "Vietnam: {:,.0f} ({: 0.0%})".format(inventory_vietnam, market_vietnam_r)
        update_date = "Updated: " + str(update)
        return [market_korea_txt, market_vietnam_txt, update_date]
    except Exception as e: return [None, None, None]


def txt_indi(n_out, ):
    out_result = ['' for i in n_out]

    return out_result


def indi_1(unit_Analyze, TODAY, df_BI, level_checkList):
    try:
        # Indicator: Total Inventory --
        num_target = 710000
        if unit_Analyze == 'Qty_pcs':
            num_target = num_target / 1.62
        elif unit_Analyze == 'Qty_pt':
            num_target = num_target / 1.62 / 120
        else:
            num_target = num_target

        # update_input = df_Input['Date'].max()
        # update_output = df_Output['Date'].max()
        update_date = TODAY  # max(update_output,update_input)
        # Indicators -------------------------------
        val_invTotal = df_BI.query("Level in @level_checkList")[unit_Analyze].sum()

        idc_TotalInventory = go.Figure(go.Indicator(
            mode="number+delta", value=val_invTotal, number={'font_color': 'orange', 'font_size': 35, "valueformat": ",.0f"},
            title={'text': 'Total Inventory:' + unit_Analyze, 'font_size': 10, 'font_color': 'green'},
            delta={'reference': num_target, "valueformat": ",.0f"}, domain={'x': [1, 0], 'y': [0.5, 0.5]})
        )

        idc_TotalInventory.layout.plot_bgcolor = '#ddd'
        idc_TotalInventory.layout.paper_bgcolor = '#101010'
        idc_TotalInventory.update_xaxes(title_font_color='white', color='white')
        idc_TotalInventory.update_yaxes(title_font_color='white', color='white')
        # idc_TotalInventory.layout.legend.bgcolor = 'white'

        return idc_TotalInventory

    except Exception as e:
        alert('chk fundtion: indi_1', e)
        return go.Figure()

def db_call(start_date, end_date, baseInventory_date):
    df_BI, df_Input, df_Output = db_conn()
    # df_Output.to_csv('outPUT.csv')
    df_Input['Qty_sqm'] = df_Input.apply(lambda x: x.Qty_pcs * x.PcsArea, axis=1)
    df_Output['Qty_sqm'] = df_Output.apply(lambda x: x.Qty_pcs * x.PcsArea, axis=1)


    df_Input_BI = df_Input.merge(df_BI, how='left', left_on='CodeTOB', right_on='BoardCode')
    df_Output_BI = df_Output.merge(df_BI, how='left', left_on='CodeTOB', right_on='BoardCode')

    df_Input_BI['Date2'] = pd.to_datetime(df_Input_BI['Date'])
    df_Input_BI['Month'] = df_Input_BI['Date2'].apply(lambda x: x.month)
    df_Input_BI['WeekOfYear'] = df_Input_BI['Date2'].apply(lambda x: x.isocalendar().week)
    df_Input_BI['Quarter'] = df_Input_BI['Date2'].apply(lambda x: x.quarter)
    df_Input_BI['Year'] = df_Input_BI['Date2'].apply(lambda x: x.year)

    df_Output_BI['Date2'] = pd.to_datetime(df_Output_BI['Date'])
    df_Output_BI['Month'] = df_Output_BI['Date2'].apply(lambda x: x.month)
    df_Output_BI['WeekOfYear'] = df_Output_BI['Date2'].apply(lambda x: x.isocalendar().week)
    df_Output_BI['Quarter'] = df_Output_BI['Date2'].apply(lambda x: x.quarter)
    df_Output_BI['Year'] = df_Output_BI['Date2'].apply(lambda x: x.year)
    # df_Output_BI.to_csv('out_bi_tmp.csv')

    # Board Inventory ----------
    BASE_DATE = baseInventory_date

    def fx_input(row):
        if BASE_DATE>=row.BaseDate:
            in_sum_total = df_Input[(df_Input["Date"] > row.BaseDate) & (df_Input["Date"] <= BASE_DATE) & (df_Input['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()
        else:
            in_sum_total =(-1) * df_Input[(df_Input["Date"] <= row.BaseDate) & (df_Input["Date"] > BASE_DATE) & (df_Input['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()
        return in_sum_total

    def fx_output(row):
        if BASE_DATE >= row.BaseDate:
            out_sum_total = df_Output[(df_Output["Date"] > row.BaseDate) & (df_Output["Date"] <= BASE_DATE) & (df_Output['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()
        else:
            out_sum_total =(-1) * df_Output[(df_Output["Date"] <= row.BaseDate) & (df_Output["Date"] > BASE_DATE) & (df_Output['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()
        return out_sum_total

    def fx_inventory(row):
        return row.BoardStockBase + row.In_sum - row.Out_sum

    df_BI['In_sum'] = df_BI.apply(fx_input, axis=1)
    df_BI['Out_sum'] = df_BI.apply(fx_output, axis=1)
    df_BI['Inventory'] = df_BI.apply(fx_inventory, axis=1)
    df_BI['Date_invt'] = BASE_DATE
    df_BI['Qty_pt'] = df_BI['Inventory'] / df_BI['spp']
    df_BI['Qty_sqm'] = df_BI['Inventory'] * df_BI['Width'] / 1000 * df_BI['Length'] / 1000
    df_BI['Qty_pcs'] = df_BI['Inventory']

    return [df_BI, df_Input, df_Output, df_Input_BI, df_Output_BI]