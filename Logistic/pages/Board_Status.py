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

try:
    # self.conn = pymysql.connect(host='192.168.1.95', user=USER, password=PASSWORD, db='zeitgypsumdb', charset='utf8')
    pymysql.install_as_MySQLdb()
    engine = create_engine("mysql://{user}:{password}@{host}/{db}".format(user=USER, password=PASSWORD, host=HOST, db=DB))
    # conn = mysql.connector.connect(**config)
    conn = pymysql.connect(host=HOST, user=USER, password=PASSWORD, db=DB, charset='utf8')
    cur = conn.cursor()
except mariadb.Error as e: alert(e)


from DashBoard.Logistic.app import logistic_app

layout = dmc.MantineProvider(
    id = 'dark_moder',

    withGlobalStyles=True,
    children=[
        dmc.Title(children = 'Board Status', order = 1, style = {'font-family':'IntegralCF-ExtraBold', 'text-align':'left', 'color' :'slategray', 'font-size':20}),
        dmc.Divider(label = 'Overview',  labelPosition='center', size='xl'),

        # Indicater Overview -----
        dmc.Group(
            display ='column',
            grow=False,
            children=[
                # dmc.Space(),
                dcc.Graph(id="indi_1",style={'width':200, 'height': 100}),

                # Korea vs Vietnam -----
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

                # Yearly Cumulated -----
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
                    id="select_graph", value="In Stock Status of Each Products",
                    data=["In Stock Status of Each Products",'Trend Analyze Input/Output of Boards', 'Output Status', 'Input Status'],
                    style={"width": 300, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Select BoardName',
                    placeholder="Select all you like!",
                    id="select_boardname", value=[],
                    data=[],
                    style={"width": 300, "marginBottom": 0},
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
                dmc.Button(
                    "Data Copy",
                    id='data_copy',
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
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 600},
                    children = [
                        # dmc.Avatar(src="../assets/images/vgsi_logo.png", size="sm"),
                        dmc.Text(id='graph_title', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dcc.Graph(id='bar_chart_inventory_tob'),
                        dmc.Divider(labelPosition='left', size='xs', label='Current Graph Comments', color='blue'),
                        dmc.Text(id='graph_comments_1', size='xs', color='black',style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Text(id='graph_comments_2', size='xs', color='black',),
                        dmc.Text(id='graph_comments_3', size='xs', color='blue',),
                        dmc.Text(id='graph_comments_4', size='xs', color='red',),
                    ]
                ),

            ]
        ),

    ]
)

@logistic_app.callback(
    # Board Inventory ---
    Output('indi_1', 'figure'),
    Output('market_korea', 'children'),
    Output('market_vietnam', 'children'),
    Output('update_date', 'children'),

    Output('cumulate_in_year', 'children'),
    Output('cumulate_out_year', 'children'),
    Output('gap_year', 'children'),
    Output('cumulate_in_month', 'children'),
    Output('cumulate_out_month', 'children'),
    Output('gap_month', 'children'),

    Output('bar_chart_inventory_tob', 'figure'),
    Output('graph_title', 'children'),
    Output('select_boardname', 'data'),
    Output('select_groupby', 'data'),
    Output('x_axis', 'data'),

    Output('graph_comments_1', 'children'),
    Output('graph_comments_2', 'children'),
    Output('graph_comments_3', 'children'),
    Output('graph_comments_4', 'children'),

    # Board Inventory ---
    Input('refresh', 'n_clicks'),
    Input('date_range', 'value'),
    Input('baseInventory_date', 'value'),
    Input('radio_period', 'value'),
    Input('level_checkList', 'value'),
    Input('unit_Analyze', 'value'),

    Input('select_graph', 'value'),
    Input('select_boardname', 'value'),
    Input('select_groupby', 'value'),
    Input('x_axis', 'value'),
    Input('data_copy', 'n_clicks'),
    Input('oneday_range', 'checked'),
    Input('filter_apply', 'checked'),

    Input('url', 'pathname'),
)
def BoardStatus(refresh, date_range, baseInventory_date, radio_period, level_checkList, unit_Analyze,
                select_graph, select_boardname, select_groupby, x_axis, data_copy, oneday_range, checked,
                n):
    try:
        TODAY = date.today()
        # print(date_range.start_date)
        start_date = datetime.date(int(date_range[0][:4]), int(date_range[0][5:7]), int(date_range[0][8:10]))
        end_date = datetime.date(int(date_range[1][:4]), int(date_range[1][5:7]), int(date_range[1][8:10]))
        baseInventory_date = datetime.date(int(baseInventory_date[:4]), int(baseInventory_date[5:7]), int(baseInventory_date[8:10]))

        filter_apply = True if checked else False

        if oneday_range:
            start_date = baseInventory_date
            end_date = baseInventory_date
        val_BoardLevel = level_checkList

        # Board DB Download ----------------
        df_BI = pd.read_sql("select * from 900_BaseInventory_Board;", con=engine)  # Board Inventory DB
        df_Input  = pd.read_sql("select * from 900_Logistic_Input_Board;", con=engine)  # Board Inventory DB
        df_Output = pd.read_sql("select * from 900_Logistic_Output_Board;", con=engine)  # Board Inventory DB
        # df_Input['Date'] = pd.to_datetime(df_Input['Date'])
        # df_Output['Date'] = pd.to_datetime(df_Output['Date'])

        df_Input_BI = df_Input.merge(df_BI, how='left', left_on='CodeTOB', right_on='BoardCode')
        df_Input_BI['Invt_in_pcs'] = df_Input_BI['BoardStockBase'] + df_Input_BI['Qty_pcs']
        df_Input_BI['Invt_in_sqm'] = df_Input_BI['Invt_in_pcs'] * df_Input_BI['PcsArea']
        df_Input_BI['Invt_in_pt'] = df_Input_BI['Invt_in_pcs'] / df_Input_BI['spp_x']

        df_Output_BI = df_Output.merge(df_BI, how='left', left_on='CodeTOB', right_on='BoardCode')
        df_Output_BI['Invt_out_pcs'] = df_Output_BI['BoardStockBase'] + df_Output_BI['Qty_pcs']
        df_Output_BI['Invt_out_sqm'] = df_Output_BI['Invt_out_pcs'] * df_Output_BI['PcsArea']
        df_Output_BI['Invt_out_pt'] = df_Output_BI['Invt_out_pcs'] / df_Output_BI['spp_x']

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

        # Clipboard df ----
        df_clipbaord = ''


        Period = 'Date'
        if radio_period == 'Daily':
            Period = 'Date'
        elif radio_period == 'Weekly':
            Period = 'WeekOfYear'
        elif radio_period == 'Monthly':
            Period = 'Month'
        elif radio_period == 'Quarterly':
            Period = 'Quarter'
        elif radio_period == 'Yearly':
            Period = 'Year'
        else:
            Period = 'Date'

        # Board Inventory ----------
        BASE_DATE = baseInventory_date

        def fx_input(row):
            return df_Input[(df_Input["Date"] > row.BaseDate) & (df_Input["Date"] <= BASE_DATE) & (df_Input['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()

        def fx_output(row):
            return df_Output[(df_Output["Date"] > row.BaseDate) & (df_Output["Date"] <= BASE_DATE) & (df_Output['CodeTOB'] == row.BoardCode)].Qty_pcs.sum()

        def fx_inventory(row):
            return row.BoardStockBase + row.In_sum - row.Out_sum

        df_BI['In_sum'] = df_BI.apply(fx_input, axis=1)
        df_BI['Out_sum'] = df_BI.apply(fx_output, axis=1)
        df_BI['Inventory'] = df_BI.apply(fx_inventory, axis=1)
        df_BI['Date_invt'] = BASE_DATE
        df_BI['Qty_pt'] = df_BI['Inventory'] / df_BI['spp']
        df_BI['Qty_sqm'] = df_BI['Inventory'] * df_BI['Width'] / 1000 * df_BI['Length'] / 1000
        df_BI['Qty_pcs'] = df_BI['Inventory']

        df_BI_daily = df_BI.copy()
        DayList = np.arange(start_date, end_date, dtype='datetime64[D]')
        df_BI_daily.drop(df_BI_daily.index, inplace=True)

        # Indicator: Total Inventory --
        num_target = 500000
        if unit_Analyze == 'Qty_pcs':
            num_target = num_target / 1.62
        elif unit_Analyze == 'Qty_pt':
            num_target = num_target / 1.62 / 120
        else:
            num_target = num_target

        update_input = df_Input['Date'].max()
        update_output = df_Output['Date'].max()
        update_date = max(update_output,update_input)

        # Indicators -------------------------------
        val_invTotal = df_BI.query("Level in @val_BoardLevel")[unit_Analyze].sum()
        idc_TotalInventory = go.Figure(go.Indicator(
            mode="number+delta", value=val_invTotal, number={'font_color': 'black', 'font_size': 35, "valueformat": ",.0f"},
            title={'text': 'Total Inventory:' + unit_Analyze, 'font_size': 10, 'font_color': 'red'},
            delta={'reference': num_target, "valueformat": ",.0f"}, domain={'x': [1, 0], 'y': [0.5, 0.5]})
        )

        market_korea = df_BI.query("Level in @val_BoardLevel and MarketGroup=='Korea'")[unit_Analyze].sum()
        market_vietnam = df_BI.query("Level in @val_BoardLevel and MarketGroup=='Vietnam'")[unit_Analyze].sum()

        if val_invTotal>0:
            market_korea_r = market_korea / val_invTotal
            market_vietnam_r = market_vietnam / val_invTotal
        else:
            market_korea_r = 0
            market_vietnam_r = 0

        market_korea_txt   = "Korea  : {:,.0f} ({: 0.0%})".format(market_korea, market_korea_r)
        market_vietnam_txt = "Vietnam: {:,.0f} ({: 0.0%} )".format(market_vietnam, market_vietnam_r)
        update_date = "Latest Updated: " + str(update_date)

        # Cumulate ----
        year_base = BASE_DATE.year
        month_base = BASE_DATE.month

        start_year = date(BASE_DATE.year,1,1)
        start_month = date(BASE_DATE.year, BASE_DATE.month,1)

        qry_txt_year = "Date>=@start_year and Date<=@BASE_DATE and Level in @val_BoardLevel"
        qry_txt_month = "Date>=@start_month and Date<=@BASE_DATE and Level in @val_BoardLevel"
        qry_txt_year_korea = "Date>=@start_year and Date<=@BASE_DATE and Level in @val_BoardLevel and MarketGroup=='Korea'"
        qry_txt_year_viet = "Date>=@start_year and Date<=@BASE_DATE and Level in @val_BoardLevel and MarketGroup=='Vietnam'"
        qry_txt_month_korea = "Date>=@start_month and Date<=@BASE_DATE and Level in @val_BoardLevel and MarketGroup=='Korea'"
        qry_txt_month_viet = "Date>=@start_month and Date<=@BASE_DATE and Level in @val_BoardLevel and MarketGroup=='Vietnam'"

        cumulate_in_year_korea_ratio = 0
        cumulate_out_year_korea_ratio = 0
        cumulate_in_month_korea_ratio = 0
        cumulate_out_month_korea_ratio = 0

        cumulate_in_year = df_Input_BI.query(qry_txt_year)[unit_Analyze].sum()
        cumulate_in_year_korea = df_Input_BI.query(qry_txt_year_korea)[unit_Analyze].sum()
        cumulate_in_year_viet = df_Input_BI.query(qry_txt_year_viet)[unit_Analyze].sum()
        if cumulate_in_year>0: cumulate_in_year_korea_ratio = cumulate_in_year_korea / cumulate_in_year

        cumulate_out_year = df_Output_BI.query(qry_txt_year)[unit_Analyze].sum()
        cumulate_out_year_korea = df_Output_BI.query(qry_txt_year_korea)[unit_Analyze].sum()
        cumulate_out_year_viet = df_Output_BI.query(qry_txt_year_viet)[unit_Analyze].sum()
        if cumulate_out_year > 0: cumulate_out_year_korea_ratio = cumulate_out_year_korea / cumulate_out_year

        gap_year = cumulate_in_year - cumulate_out_year

        cumulate_in_month = df_Input_BI.query(qry_txt_month)[unit_Analyze].sum()
        cumulate_in_month_korea = df_Input_BI.query(qry_txt_month_korea)[unit_Analyze].sum()
        cumulate_in_month_viet = df_Input_BI.query(qry_txt_month_viet)[unit_Analyze].sum()
        if cumulate_in_month > 0: cumulate_in_month_korea_ratio = cumulate_in_month_korea / cumulate_in_month

        cumulate_out_month = df_Output_BI.query(qry_txt_month)[unit_Analyze].sum()
        cumulate_out_month_korea = df_Output_BI.query(qry_txt_month_korea)[unit_Analyze].sum()
        cumulate_out_month_viet = df_Output_BI.query(qry_txt_month_viet)[unit_Analyze].sum()
        if cumulate_out_month > 0: cumulate_out_month_korea_ratio = cumulate_out_month_korea / cumulate_out_month

        gap_month = cumulate_in_month - cumulate_out_month

        cumulate_in_year_txt = "IN: {:,.0f} ( {:,.0f} + {:,.0f} ) >> {: 0.0%} ".format(cumulate_in_year, cumulate_in_year_korea, cumulate_in_year_viet, cumulate_in_year_korea_ratio)
        cumulate_out_year_txt = "OUT: {:,.0f} ( {:,.0f} + {:,.0f} ) >> {: 0.0%}  ".format(cumulate_out_year,cumulate_out_year_korea,cumulate_out_year_viet,cumulate_out_year_korea_ratio)
        gap_year_txt = "IN - OUT: {:,.0f} ".format(gap_year)
        cumulate_in_month_txt = "IN: {:,.0f} ( {:,.0f} + {:,.0f} ) >> {: 0.0%}  ".format(cumulate_in_month,cumulate_in_month_korea,cumulate_in_month_viet,cumulate_in_month_korea_ratio)
        cumulate_out_month_txt = "OUT: {:,.0f} ( {:,.0f} + {:,.0f} ) >> {: 0.0%}  ".format(cumulate_out_month,cumulate_out_month_korea,cumulate_out_month_viet,cumulate_out_month_korea_ratio)
        gap_month_txt = "IN - OUT: {:,.0f} ".format(gap_month)

        # Inventory Graphs -----

        graph_title = select_graph
        selected_group_items = []
        selected_xaxis_items = []
        graph_comments_1 = ''
        graph_comments_2 = ''
        graph_comments_3 = ''
        graph_comments_4 = ''
        # print(end_date)
        chart_1 = go.Figure()
        selected_boardname_items = df_BI.sort_values(by=['BoardName'],ascending=True)['BoardName'].unique()

        if len(select_boardname)>=1:
            qry_board_date = "(BoardName_y in @select_boardname) and (Level in @val_BoardLevel) and Date>=@start_date and Date<=@end_date"
            qry_board_level = "(BoardName in @select_boardname) and Level in @val_BoardLevel"
        else:
            qry_board_date = "Level in @val_BoardLevel and Date>=@start_date and Date<=@end_date"
            qry_board_level = "Level in @val_BoardLevel"

        df_bar1_inventory_tob = df_BI_daily_bar3 = df_BI_daily.query(qry_board_level).groupby(by=['BoardName','MarketGroup'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
        if select_graph=='In Stock Status of Each Products':
            selected_group_items = ['MarketGroup', 'Level', 'BoardName']
            selected_xaxis_items = ['MarketGroup', 'Level', 'BoardName']

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = ['BoardName', 'MarketGroup', ]
                x_val = 'BoardName'

            print(gr_by, x_val, filter_apply)

            total_Invent = df_BI.query(qry_board_level).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
            df_BI['Ratio'] = df_BI.query(qry_board_level)[unit_Analyze] / total_Invent[unit_Analyze]
            df_BI_bar1 = df_BI.query(qry_board_level).groupby(by=gr_by, as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum','Ratio':'sum'}).sort_values(by='Qty_sqm', ascending=False)
            bar_chart_inventory_tob = px.bar(df_BI_bar1, x=x_val, y=unit_Analyze, color=gr_by[-1], text_auto=True, text='Ratio',
                                orientation='v', hover_data={'Ratio':':0.0%',unit_Analyze:':,.0f'})
            bar_chart_inventory_tob.update_traces(texttemplate='%{y:,.0f} (%{text:0.0%})',)
            chart_1 = bar_chart_inventory_tob

            df_clipbaord = df_BI_bar1
            refresh = None


        if select_graph=='Trend Analyze Input/Output of Boards':

            selected_group_items = []
            selected_xaxis_items = []

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = []
                x_val = ''


            df_daily_in= df_Input_BI.query(qry_board_date).groupby(by=[Period], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).fillna(0)
            df_daily_out= df_Output_BI.query(qry_board_date).groupby(by=[Period], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'}).fillna(0)

            x_list = df_daily_out[Period]

            sct_in_out = go.Figure()
            sct_in_out.add_scatter(x=x_list, y=df_daily_in[unit_Analyze],
                                   mode='markers+lines+text', textposition='top center', texttemplate='%{y:,.0f}', name='Input',
                                   marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2)),)
            sct_in_out.add_scatter(x=x_list, y=df_daily_out[unit_Analyze],
                                   mode='markers+lines+text', textposition='top center', texttemplate='%{y:,.0f}', name='Output',
                                   marker=dict(color='red', size=11, line=dict(color='MediumPurple', width=2)), )
            sct_in_out.add_scatter(x=x_list, y=(df_daily_in[unit_Analyze] - df_daily_out[unit_Analyze]),
                                   mode='markers+lines+text', textposition='top center', texttemplate='%{y:,.0f}', name='diff_Inventory',
                                   marker=dict(color='green', size=11, line=dict(color='MediumPurple', width=2)), )
            # sct_in_out.update_traces(hover_data='%{y:,.0f}')
            sct_in_out.update_traces(hovertemplate=None, )
            sct_in_out.update_layout(hovermode="x unified")
            chart_1 = sct_in_out

            df_clipbaord = df_daily_out

            # Graph comments ---
            qry_txt_korea = qry_board_date + " and MarketGroup=='Korea'"
            qry_txt_viet = qry_board_date + " and MarketGroup=='Vietnam'"

            qty_total_in = df_Input_BI.query(qry_board_date).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})[unit_Analyze]
            qty_total_in_korea = df_Input_BI.query(qry_txt_korea).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})[unit_Analyze]
            qty_total_in_viet = df_Input_BI.query(qry_txt_viet).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})[unit_Analyze]
            qty_kr_ratio = 0
            if qty_total_in>0: qty_kr_ratio = qty_total_in_korea / qty_total_in

            qty_total_out = df_Output_BI.query(qry_board_date).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})[unit_Analyze]
            qty_total_out_korea = df_Output_BI.query(qry_txt_korea).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})[unit_Analyze]
            qty_total_out_viet = df_Output_BI.query(qry_txt_viet).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})[unit_Analyze]
            qty_out_kr_ratio = 0
            if qty_total_out>0: qty_out_kr_ratio = qty_total_out_korea / qty_total_out

            qty_diff = qty_total_in - qty_total_out
            qty_diff_korea = qty_total_in_korea - qty_total_out_korea
            qty_diff_viet = qty_total_in_viet - qty_total_out_viet


            graph_comments_1 = '[Quantity in date range(Korea + Vietnam)KR%]'
            graph_comments_2 ='   Input: {:,.0f} ({:,.0f} + {:,.0f}) {:.0%}'.format(qty_total_in, qty_total_in_korea, qty_total_in_viet, qty_kr_ratio)
            graph_comments_3 ='  Output: {:,.0f} ({:,.0f} + {:,.0f}) {:.0%}'.format(qty_total_out, qty_total_out_korea, qty_total_out_viet, qty_out_kr_ratio)
            graph_comments_4 ='  In-Out: {:,.0f} ({:,.0f} + {:,.0f})'.format(qty_diff, qty_diff_korea, qty_diff_viet,)

            refresh = None

        # Output Status ----------------
        if select_graph == 'Output Status':
            selected_group_items = [Period, 'MarketGroup', 'Level', 'Category1', 'Category2', 'BoardName_y']
            selected_xaxis_items = [Period, 'MarketGroup', 'Level', 'Category1', 'Category2', 'BoardName_y']

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = [Period, 'BoardName_y', ]
                x_val = Period


            total_out = df_Output_BI.query(qry_board_date).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
            df_Output_BI['Ratio'] = df_Output_BI.query(qry_board_date)[unit_Analyze] / total_out[unit_Analyze]

            df_daily_out = df_Output_BI.query(qry_board_date).groupby(by=gr_by, as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum', 'Ratio':'sum'}).sort_values(x_val, ascending=True)
            bar_chart_11 = px.bar(df_daily_out, x=x_val, y=unit_Analyze, color=gr_by[-1],text='Ratio', text_auto=True, barmode='group',
                                  hover_data={'Ratio':':0.0%',unit_Analyze:':,.0f'})
            # bar_chart_11.update_traces(visible="legendonly")
            bar_chart_11.update_traces(texttemplate='%{y:,.0f} (%{text:0.0%})', )
            chart_1 = bar_chart_11

            df_clipbaord = df_daily_out
            refresh=None

        # Input Staus ----------------
        if select_graph == 'Input Status':
            selected_group_items = [Period, 'MarketGroup', 'Level', 'Category1', 'Category2', 'BoardName_y']
            selected_xaxis_items = [Period, 'MarketGroup', 'Level', 'Category1', 'Category2', 'BoardName_y']

            if len(select_groupby) >= 1 and len(x_axis) >= 1 and filter_apply:
                gr_by = select_groupby
                x_val = x_axis
            else:
                gr_by = [Period, 'BoardName_y', ]
                x_val = Period

            selected_group_items = [Period, 'MarketGroup', 'Level',  'Category1', 'Category2', 'BoardName_y']
            selected_xaxis_items = [Period, 'MarketGroup', 'Level',  'Category1', 'Category2', 'BoardName_y']

            total_in = df_Input_BI.query(qry_board_date).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum'})
            df_Input_BI['Ratio'] = df_Input_BI.query(qry_board_date)[unit_Analyze] / total_in[unit_Analyze]

            df_daily_in = df_Input_BI.query(qry_board_date).groupby(by=gr_by, as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs': 'sum', 'Ratio': 'sum'}).sort_values(x_val, ascending=True)
            bar_chart_11 = px.bar(df_daily_in, x=x_val, y=unit_Analyze, color=gr_by[-1], text='Ratio', text_auto=True, barmode='group',
                                  hover_data={'Ratio': ':0.0%', unit_Analyze: ':,.0f'})
            # bar_chart_11.update_traces(visible="legendonly")
            bar_chart_11.update_traces(texttemplate='%{y:,.0f} (%{text:0.0%})', )
            chart_1 = bar_chart_11

            df_clipbaord = df_daily_in
            refresh = None

        # Data copy to clipboard ----
        if data_copy is not None:
            print(df_clipbaord)
            df_clipbaord.to_clipboard()
            data_copy = None

        # Miss match Check -----
        mismatch_out = df_Output_BI[df_Output_BI['BoardCode'].isna()]['BoardName_x']
        mismatch_in = df_Input_BI[df_Input_BI['BoardCode'].isna()]['BoardName_x']
        #
        print(mismatch_out.unique())
        print(mismatch_in.unique())

        return [idc_TotalInventory, market_korea_txt, market_vietnam_txt, update_date,
                cumulate_in_year_txt, cumulate_out_year_txt, gap_year_txt, cumulate_in_month_txt, cumulate_out_month_txt, gap_month_txt,
                chart_1, graph_title, selected_boardname_items, selected_group_items, selected_xaxis_items,
                graph_comments_1, graph_comments_2, graph_comments_3, graph_comments_4]

    except Exception as e:
        # alert(e)
        return



