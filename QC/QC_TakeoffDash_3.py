import dash
import flask

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

from datetime import date

import xlwings
from dash import Dash, Input, Output, dcc, html, dash_table
from sqlalchemy import create_engine
from pymsgbox import alert, confirm, password, prompt

HOST     = '10.50.3.163'
DB       = 'gfactoryDB'
USER = 'leekr'
PASSWORD = 'g1234'

NOW = datetime.datetime.now()
TODAY = date.today()


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
logistic_app = dash.Dash(__name__, url_base_pathname='/qc_takeoff/')
logistic_app.title = "QC Takeoff"
logistic_app.layout = html.Div(
    [
        html.H1("QC Takeoff Inspection Result", style={'textAlign':'center', 'color':'blue', 'textSize':20}),

        dcc.DatePickerRange(
            id="date_range",
            min_date_allowed=datetime.datetime(2022,1,1), max_date_allowed=TODAY+datetime.timedelta(days=365), start_date=TODAY, end_date=TODAY,
            style={'position':'absolute','left': 10, 'top': 90, 'width':300,  'textSize':15},
        ),
        html.Button("Rfresh", id="button", style={'position':'absolute','left': 10, 'top': 50, 'width':250, 'height': 30, 'color':'red'}),

        # Graph -----
        dcc.Graph(id="pie_1", style={'position':'absolute','left': 10, 'top': 150, 'width':350, 'height':400}),
        dcc.Graph(id="pie_2", style={'position':'absolute','left': 360, 'top': 150, 'width':450, 'height': 400}),
        dcc.Graph(id="bar_1", style={'position':'absolute','left': 820, 'top': 220, 'width':1000, 'height': 400}),
        dcc.Graph(id="bar_2", style={'position':'absolute','left': 820, 'top': 620, 'width':1000, 'height': 400}),
        dcc.Graph(id="indi_1", style={'position':'absolute','left': 1300, 'top': 60, 'width':200, 'height': 200}),
        dcc.Graph(id="indi_2", style={'position':'absolute','left': 1500, 'top': 60, 'width':200, 'height': 200}),
        dcc.Graph(id="indi_3", style={'position':'absolute','left': 1700, 'top': 60, 'width':200, 'height': 200}),
        dcc.Graph(id="indi_4", style={'position':'absolute','left': 1050, 'top': 60, 'width':200, 'height': 200}),

        dcc.RadioItems(id='radio_unit',  options=['Qty_sqm', 'Qty_pcs', 'Qty_pt'], value='Qty_sqm', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': 320, 'top': 90, 'width':200, 'backgroundColor':'lightgray'}),
        dcc.RadioItems(id='radio_Ev_BN',  options=['Evaluate', 'BoardName', ], value='Evaluate', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': 1600, 'top': 260, 'width':200, 'backgroundColor':'lightgray'}),
        dcc.RadioItems(id='radio_DT_BN',  options=['Date2', 'BoardName', ], value='Date2', inline=False,
                      style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': 1600, 'top': 650, 'width':200, 'backgroundColor':'lightgray'}),

        dcc.Interval(id='interval1', interval=600 * 1000, n_intervals=0),

        html.H2("Evaluate Result", style={'position':'absolute', 'textAlign':'left', 'color':'black', 'textSize':10,  'left': 10, 'top': 550, 'width':800}),
        html.Div(
            dag.AgGrid(
                id="DataTable1",
                defaultColDef={"resizable": True, "sortable": True, "filter": True},
                dashGridOptions = {"rowHeight": 30},
                style={'height': 400},
                columnSize='sizeColumnsToFit',
                columnSizeOptions={"skipHeader": True},
            ), style={'position':'absolute','left': 820, 'top': 1050, 'width':1000, 'height': 400}
        ),

        html.Div(
            dash_pivottable.PivotTable(
                id='table_pv1',
                cols=['Evaluate'],
                rows=['Date2', 'BoardName'],
                vals=['Qty_pt'],
                aggregatorName='Sum',
                # rendererName='Table',
            ), style={'position': 'absolute', 'left': 10, 'top': 650, 'width': 800, 'height':400, 'text-align':'center'}
        ),

    ]
)

@logistic_app.callback(
    Output('pie_1', 'figure'),
    Output('pie_2', 'figure'),
    Output('bar_1', 'figure'),
    Output('bar_2', 'figure'),
    Output('indi_1', 'figure'),
    Output('indi_2', 'figure'),
    Output('indi_3', 'figure'),

    Output('DataTable1', 'columnDefs'),
    Output('DataTable1', 'rowData'),
    Output('table_pv1', 'data'),
    Output('indi_4', 'figure'),
    # Output('DataTable2', 'children'),
    # Output('pvTable1', 'data'),

    Input('date_range', 'start_date'),
    Input('date_range', 'end_date'),
    Input('button', 'n_clicks'),
    Input('interval1', 'n_intervals'),
    Input('radio_unit', 'value'),
    Input('radio_Ev_BN', 'value'),
    Input('radio_DT_BN', 'value'),
)
def updateChart(start_date, end_date, n_clicks, n_intervals, radio_unit, radio_Ev_BN, radio_DT_BN):
    TODAY = date.today()

    start_date = datetime.date(int(start_date[:4]), int(start_date[5:7]), int(start_date[8:10]))
    end_date = datetime.date(int(end_date[:4]), int(end_date[5:7]), int(end_date[8:10]))

    df = pd.read_sql("select *, concat(TOB,' ', Thick, '*' , Width,'*',Length) BoardName from QC_Takeoff;", con=engine)
    df['Date2'] = df['Date']
    df['Date'] = pd.to_datetime(df['Date'])
    df['Qty_sqm'] = df['Quantity'] * df['Width'] / 1000 * df['Length'] / 1000
    df['Qty_pcs'] = df['Quantity']
    df['Qty_pt'] = df['Qty_pcs'] / abs(df['Quantity'])
    df['WeekOfYear'] = df['Date'].apply(lambda x: x.isocalendar().week)
    df['Month'] = df['Date'].apply(lambda x: x.month)
    df['Quarter'] = df['Date'].apply(lambda x: x.quarter)
    df = df.query("Date>=@start_date and Date<=@end_date")

    df_qty = df.groupby(by=['Date', 'Date2', 'BoardName', 'Evaluate'], as_index=False)[['Quantity', 'Qty_sqm']].sum(numeric_only=True)

    df_P = df
    df_P = df_P[['Date2', 'BoardName', 'Evaluate', 'Quantity', 'Qty_sqm', 'TOB', 'Thick', 'Discription']]
    df2 = df

    # Pie 1 : Evaluate ----
    Evaluate_color = {'G':'lightblue', 'G2':'cyan','G3':'blue', 'S':'yellow', 'X':'gray', 'NG':'purple'}

    df_pie_1 = df
    pie_chart1 = px.pie(df_pie_1, names='Evaluate', values=radio_unit, color='Evaluate', title='Evaluate Ratio:' + radio_unit, hole=0.5, color_discrete_map=Evaluate_color)
    pie_chart1.update_traces(textposition='outside', textinfo='value+percent', texttemplate="%{value:,.0f} / %{percent}",)

    # Pie 2: TOB Ratio ----
    df_pie_2 = df
    pie_chart2 = px.pie(df_pie_2, names='BoardName', values=radio_unit, color='BoardName', title='TOB Ratio: ' + radio_unit , hole=0.5)
    pie_chart2.update_traces(textposition='outside', textinfo='value+percent')

    # Bar 1: Daily Evaluate Result ---
    df_bar_1 = df.groupby(by=['Date2', radio_Ev_BN], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs':'sum'}).sort_values('Date2')
    bar_chart1 = px.bar(df_bar_1, x='Date2', y= radio_unit, color=radio_Ev_BN, title='Daily '+ radio_Ev_BN + ' Result: '+ radio_unit, text_auto=True,
                        color_discrete_map=Evaluate_color, )
    bar_chart1.update_traces(texttemplate='%{y:,.0f}',)
    df_bar_sct_1 = df.groupby(by=['Date2'], as_index=False).agg({'Qty_pt': 'sum', 'Qty_sqm': 'sum', 'Qty_pcs':'sum'}).sort_values('Date2')
    bar_chart1.add_scatter(x=df_bar_sct_1['Date2'], y=df_bar_sct_1[radio_unit], text=radio_unit, textposition="top right",  name=radio_unit,
                           marker=dict(color='blue', size=11, line=dict(color='MediumPurple', width=2))
                           )

    # Scatter 2: Daily or  Good Board Ratio ---
    def f_good_ratio(group):
        group['Good'] = group[(group['Evaluate']=='G') | (group['Evaluate']=='G2')  | (group['Evaluate']=='G3')]['Qty_sqm'].sum()
        # group['Good'] = group.qeery("Evaluate in ['G', 'G2', 'G3']")['Qty_sqm'].sum()
        group['grSum'] = group['Qty_sqm'].sum()
        group['GoodRatio'] = group['Good'] / group['grSum'] * 100
        group['GoodRatio'] = group['GoodRatio'].round(2)
        return group

    df_bar_sct_2 = df2.groupby(by=[radio_DT_BN], as_index=False).apply(f_good_ratio)
    bar_chart2 = px.scatter(df_bar_sct_2, x=radio_DT_BN, y= 'GoodRatio', title= radio_DT_BN + ' Good Board Ratio(%)', text='GoodRatio',)
    bar_chart2.update_traces(textposition='top center', mode='markers+lines+text', texttemplate='%{text:.2f}', )
    # bar_chart2 = bar_chart1

    # Indicators -----
    val_indi_1 = df2[radio_unit].sum()
    val_indi_2 = df2.query("Evaluate in ('G', 'G2', 'G3')")[radio_unit].sum()
    val_indi_3 = df2.query("Evaluate =='S'")[radio_unit].sum()
    val_indi_4 = df2.query("Evaluate =='NG'")[radio_unit].sum()

    if val_indi_1>0:
        yield_good = val_indi_2 / val_indi_1 * 100
        ratio_sort = val_indi_3 / val_indi_1 * 100
        ratio_NG = val_indi_4 / val_indi_1 * 100
    else:
        yield_good = 0
        ratio_sort = 0
        ratio_NG = 0

    indicator_1 = go.Figure(go.Indicator(mode = "number+delta", value = yield_good,  number={'font_color':'black', 'font_size':40,  "valueformat": ".1f"},
                                         title = {'text': 'Good Ratio(%)'}, delta={'reference':95, "valueformat": ".1f"}, domain = {'x': [1, 0], 'y': [0, 1]},),
                            )
    indicator_2 = go.Figure(go.Indicator(mode = "number+delta", value = ratio_sort, number={'font_color':'black', 'font_size':40, "valueformat": ".1f"},
                                         title = {'text': 'Sort Ratio(%)'}, delta = {'reference': 5, 'increasing': {'color': 'red'},'decreasing': {'color': 'green'}, "valueformat": ".1f"}, domain = {'x': [1, 0], 'y': [0, 1],})
                            )
    indicator_3 = go.Figure(go.Indicator(mode = "number+delta", value = ratio_NG, number={'font_color':'black', 'font_size':40, "valueformat": ".1f"},
                                         title = {'text': 'NG Ratio(%)'}, delta = {'reference': 1, 'increasing': {'color': 'red'},'decreasing': {'color': 'green'}, "valueformat": ".1f"}, domain = {'x': [1, 0], 'y': [0, 1],})
                            )
    indicator_4 = go.Figure(go.Indicator(mode = "number+delta", value = val_indi_1, number={'font_color':'black', 'font_size':30, "valueformat": ",.0f"},
                                         title = {'text': 'Total Products'}, domain = {'x': [1, 0], 'y': [0, 1],})
                            )

    # Tables ---
    df_dTable1 = df2.groupby(by=['Date2', 'BoardName', 'Evaluate'], as_index=False).agg({'Quantity': 'count', 'Qty_sqm': 'sum',})
    df_dTable1 = df_dTable1[['Date2', 'BoardName', 'Evaluate', 'Quantity', ]]

    def fx(row):
        if row.Time is not None:
            try:
                val_tmp = (float(row.Time)+24)*3600*24 - 7*3600
                val = datetime.datetime.fromtimestamp(val_tmp).strftime('%H:%M')
            except: val = row.Time
        else: val = 0
        return val

    df2['Time2'] = df2.apply(fx, axis=1)
    # print(df2['Time'].astype('str'))
    # print(df2['Time2'])

    df_table_1 = df2[['Date2', 'BoardName','LotNo','Time2', 'Evaluate', 'Discription', 'Quantity']].sort_values(['Date2', 'BoardName'])
    # dt1_columns = [{'name': 'Date', 'id': 'Date2'}, {'name': 'BoardName', 'id': 'BoardName'}, {'Evaluate': 'Date', 'id': 'Evaluate'}, {'name': 'Pallet No.', 'id': 'Quantity'}, {'name': 'Qty_sq', 'id': 'Qty_sqm'} ]
    width_col = [120, 150, 80,80, 100, 500, 100]
    dt1_columns = [{'headerName': i, 'field': i, 'width':width_col[k]} for k, i in enumerate(df_table_1.columns)]
    dt1_data = df_table_1.to_dict('records')


    df_pv_1 = df2[['Date2', 'BoardName', 'LotNo', 'Time', 'Evaluate', 'Discription', 'Quantity', 'Qty_sqm', 'Qty_pcs', 'Qty_pt']]
    data_pv1 = df_pv_1.to_dict('records')


    return [pie_chart1, pie_chart2, bar_chart1, bar_chart2, indicator_1, indicator_2,indicator_3, dt1_columns, dt1_data,
            data_pv1, indicator_4]


if __name__ == '__main__':
    logistic_app.run_server(debug=False, host='10.50.3.152', port=61024)
    # logistic_app.run_server(debug=False)


