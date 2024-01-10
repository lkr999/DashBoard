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
        df = pd.read_sql("select * from 800_Board_Quality;", con=engine)
        df['Date'] = pd.to_datetime(df['Date_Product'])
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

        df_spec = pd.read_sql("select * from 800_Board_Quality_Spec;", con=engine)

    except mariadb.Error as e: alert(e)

    return df, df_spec

from DashBoard.QC_local.app import qc_app2
layout = dmc.MantineProvider(
    id = 'dark_moder_quality', #theme={"colorScheme": "white"},

    withGlobalStyles=True,
    children=[
        dmc.Title(children = 'Board Quality', order = 1, style = {'font-family':'IntegralCF-ExtraBold', 'text-align':'left', 'color' :'slategray', 'font-size':20}),

        dmc.Divider(label='',size='xl', style={"marginBottom": 5, "marginTop": 5}),
        dmc.Group(
            display='column',
            grow=False,
            children=[
                # Graph Selecter ---
                dmc.Select(
                    label='Select Board Quality Item',
                    placeholder="Select one",
                    id="select_graph", value="Daily Property(Box Chart)",
                    data=['Daily Property(Box Chart)', 'Class Base Analyze(Box Chart)', 'Multi Regression','Process Capability',],
                    style={"width": 250, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='TOB Select',
                    placeholder="Select all you like!",
                    id="select_tob", value=['SD 9.5'],
                    data=[],
                    style={"width": 250, "marginBottom": 0},
                ),

                dmc.Select(
                    label='Property Select',
                    placeholder="Select the TOB",
                    id="select_property", value="F_Strength_MD_Avg",
                    data=[],
                    style={"width": 250, "marginBottom": 0},
                ),
                dmc.MultiSelect(
                    label='Class Select',
                    placeholder="Select Class!",
                    id="select_class", value=[],
                    data=[],
                    style={"width": 250, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Multi Regression Factors_X',
                    placeholder="Select the Factors!",
                    id="regression_items_x", value=[],
                    data=[],
                    style={"width": 200, "marginBottom": 0},
                ),

                dmc.MultiSelect(
                    label='Multi Regression Item_Y',
                    placeholder="Select the Result Value!",
                    id="regression_items_y", value=[],
                    data=[],
                    style={"width": 200, "marginBottom": 0},
                ),

            ]
        ),
        dmc.Divider(label='Graphs',size='xs', style={"marginBottom": 20, "marginTop": 5}),

        # Graph Area_1 ----
        dmc.Group(
            grow=False,
            children=[
                dmc.Paper(
                    radius='sm',  withBorder=True, shadow='xs', p='sm', style={'width':1550,'height': 1000},
                    children = [
                        # dmc.Avatar(src="../assets/images/vgsi_logo.png", size="sm"),
                        dmc.Text(id='graph_title_bq', size='xs', color='dimmed', style={'font-family': 'IntegralCF-RegularOblique'}),
                        dmc.Divider(labelPosition='center', size='xl'),
                        dcc.Graph(id='graph_1', style={'width':1550, 'height':600 } ),
                        dmc.Divider(label='Graph Detail',labelPosition='left', size='xs', color='blue'),

                        # dmc.Container(id='graph_detail', size="xs", px="xs",
                        #               style={"height": 300, 'width':1500,
                        #                      "marginTop": 5,"marginBottom": 5, 'align': 'left'},
                        #               ),
                        dcc.Textarea(
                                id='graph_detail',
                                value='Textarea content initialized\nwith multiple lines of text',
                                style={'width':'100%', 'height': 400}
                        ),
                    ]
                ),

            ]
        ),
    ]
)

@qc_app2.callback(

    Output('graph_title_bq','children'),
    Output('graph_1','figure'),
    Output('select_tob','data'),
    Output('select_property','data'),
    Output('select_class','data'),
    Output('graph_detail','value'),
    Output('regression_items_x','data'),
    Output('regression_items_y','data'),

    Input('date_range', 'value'),
    Input('baseInventory_date', 'value'),
    Input('radio_period', 'value'),
    Input('level_checkList', 'value'),
    Input('unit_Analyze', 'value'),
    Input('oneday_range', 'checked'),

    Input('select_graph', 'value'),
    Input('refresh','n_clicks'),
    Input('select_property','value'),
    Input('select_tob','value'),
    Input('select_class','value'),
    Input('regression_items_x','value'),
    Input('regression_items_y','value'),

    Input('url', 'pathname'),
)
def BoardQualityUpdate(date_range,baseInventory_date,radio_period,level_checkList,unit_Analyze,oneday_range,
                       select_graph, refresh, select_property, select_tob,select_class,regression_items_x, regression_items_y,
                       n):

    def calculate_cpk_ppk_one_spec(data, spec_limit, upper_side=True):
        # Process mean and standard deviation
        process_mean = np.mean(data)
        process_std = np.std(data, ddof=1)  # Using Bessel's correction for sample standard deviation

        # Cp, Cpk calculation
        # Cp = (spec_limit) / (3 * process_std) if upper_side else (spec_limit) / (3 * process_std)
        Cpk = (spec_limit - process_mean) / (3 * process_std) if upper_side else (process_mean - spec_limit) / (3 * process_std)
        # Cpl = (process_mean - spec_limit) / (3 * process_std) if not upper_side else 0
        # Cpk = min(Cpu, Cpl) if upper_side else max(Cpu, Cpl)

        # Pp, Ppk calculation
        # Pp = (spec_limit) / (3 * process_std) if upper_side else (spec_limit) / (3 * process_std)
        # Ppu = (spec_limit - process_mean) / (3 * process_std) if upper_side else 0
        # Ppl = (process_mean - spec_limit) / (3 * process_std) if not upper_side else 0
        # Ppk = min(Ppu, Ppl) if upper_side else max(Ppu, Ppl)

        return Cpk

    def cal_cpk(data, low_spec, up_spec):
        # Process mean and standard deviation
        process_mean = np.mean(data)
        process_std = np.std(data, ddof=1)  # Using Bessel's correction for sample standard deviation
        Cpk, Ppk = [0,0]

        if low_spec>0 and up_spec>0:
            # Cp, Cpk calculation
            Cp = (up_spec - low_spec) / (6 * process_std)
            Cpu = (up_spec - process_mean) / (3 * process_std)
            Cpl = (process_mean - low_spec) / (3 * process_std)
            Cpk = min(Cpu, Cpl)

            # Pp, Ppk calculation
            Pp = (up_spec - low_spec) / (6 * process_std)
            Ppu = (up_spec - process_mean) / (3 * process_std)
            Ppl = (process_mean - low_spec) / (3 * process_std)
            Ppk = min(Ppu, Ppl)

        if low_spec>0 and not (up_spec>0):
            limit_spec = low_spec
            upper_limit = False
            Cpk = calculate_cpk_ppk_one_spec(data=data, spec_limit=limit_spec, upper_side=upper_limit)

        if up_spec>0 and not (low_spec>0):
            limit_spec = up_spec
            upper_limit = True
            Cpk = calculate_cpk_ppk_one_spec(data=data, spec_limit=limit_spec, upper_side=upper_limit)
        return Cpk

    def cpk_to_ppm(cpk):
        # Calculate the corresponding Z value for Cpk
        z_cpk = abs(cpk)

        # Calculate the PPM using the cumulative distribution function (CDF)
        ppm = stats.norm.cdf(-z_cpk) * 1e6

        return ppm

    try:
        start_date = datetime.date(int(date_range[0][:4]), int(date_range[0][5:7]), int(date_range[0][8:10]))
        end_date = datetime.date(int(date_range[1][:4]), int(date_range[1][5:7]), int(date_range[1][8:10]))
        qry_daterange = "Date_Product>=@start_date and Date_Product<=@end_date"

        # Period Define ---
        if radio_period == 'Daily': Period = 'Date_Product'
        elif radio_period == 'Weekly': Period = 'WeekOfYear'
        elif radio_period == 'Monthly': Period = 'Month'
        elif radio_period == 'Quarterly': Period = 'Quarter'
        else: Period = 'Date_Product'

        df = df_download()[0]
        df_spec = df_download()[1]
        chart_1 = go.Figure()
        list_TOB = df.sort_values(by='TOB', ascending=True)['TOB'].unique()
        list_Property =[str(x) for x in df.columns[5:-5]]
        list_Class = df['Class_1'].dropna().unique()

        graph_detail  = ''

        spec_min = df_spec.query("TOB in @select_tob and Property==@select_property")['Min'].values
        spec_max = df_spec.query("TOB in @select_tob and Property==@select_property")['Max'].values

        if select_graph=='Daily Property(Box Chart)':
            qry_chart = qry_daterange + " and TOB in @select_tob"

            df_chart1 = df.query(qry_chart)
            if len(spec_min) < 1: y_spec_min = []
            else: y_spec_min = [spec_min[0] for i in df_chart1[Period]]
            if len(spec_max) < 1: y_spec_max = []
            else: y_spec_max = [spec_max[0] for i in df_chart1[Period]]

            data_1 = df_chart1[select_property].dropna()
            span_cpk = (np.mean(data_1))

            y_Cpk = [cal_cpk(data=df_chart1[df_chart1[Period]==i][select_property].dropna().values, low_spec=spec_min[0], up_spec=spec_max[0])*100 for i in df_chart1[Period].values]

            chart_1 = px.box(df_chart1, x=Period, y=select_property, color='TOB')
            chart_1.add_scatter(x=df_chart1[Period], y=y_spec_min, name='Lower Spec',
                                mode='lines', line=dict(color='red', width=3, dash='dash'),)
            chart_1.add_scatter(x=df_chart1[Period], y=y_spec_max, name='Uppper Spec',
                                mode='lines', line=dict(color='magenta', width=3, dash='dot'),)

            # type-1 anova summary
            ols_txt = select_property + ' ~ C(' + Period + ', Sum)*C(TOB, Sum)'
            model = ols(ols_txt, data=df_chart1).fit()
            table_type_1 = sm.stats.anova_lm(model, typ=1)

            graph_detail = "# OLS Analyze Result --------------------------------------------------- \n \n " + str(table_type_1)

        if select_graph=='Class Base Analyze(Box Chart)':
            qry_chart = "Class_1 in @select_class"

            df_chart1 = df.query(qry_chart)
            chart_x_val = 'Class_1'

            if len(spec_min) < 1: y_spec_min = []
            else: y_spec_min = [spec_min[0] for i in df_chart1[Period]]
            if len(spec_max) < 1: y_spec_max = []
            else: y_spec_max = [spec_max[0] for i in df_chart1[Period]]

            chart_1 = px.box(df_chart1, x=chart_x_val, y=select_property, color='Class_1')
            chart_1.add_scatter(x=df_chart1[chart_x_val], y=y_spec_min, name='Lower Spec',
                                mode='lines', line=dict(color='red', width=3, dash='dash'), )
            chart_1.add_scatter(x=df_chart1[chart_x_val], y=y_spec_max, name='Uppper Spec',
                                mode='lines', line=dict(color='magenta', width=3, dash='dot'), )

            # type-1 anova summary
            ols_txt = select_property + ' ~ C(Class_1, Sum)'
            model = ols(ols_txt, data=df_chart1).fit()
            table_type_1 = sm.stats.anova_lm(model, typ=1)

            graph_detail = "# OLS Analyze Result --------------------------------------------------- \n \n " + str(table_type_1)

        if select_graph=='Multi Regression':
            qry_reg_txt = qry_daterange + " and TOB in @select_tob"

            reg_items = regression_items_y + regression_items_x
            df_reg = df.query(qry_reg_txt)[reg_items].dropna()


            x = df_reg[regression_items_x]
            y = df_reg[regression_items_y[0]]

            # with statsmodels
            x = sm.add_constant(x)  # adding a constant

            model = sm.OLS(y, x).fit()
            predictions = model.predict(x)

            print_model = model.summary()
            print(print_model)
            graph_detail = str(print_model)

            # X = x.reshape(-1, 1)
            #
            # model = LinearRegression()
            # model.fit(X, y)
            #
            # x_range = np.linspace(X.min(), X.max(), 100)
            # y_range = model.predict(x_range.reshape(-1, 1))

            chart_1 = px.scatter_matrix(df_reg)
            # chart_1.add_traces(go.Scatter(x=x_range, y=y_range, name='Regression Fit'))


        if select_graph=='Process Capability':
            qry_cpk_txt = qry_daterange + " and TOB in @select_tob"

            df_cpk = df.query(qry_cpk_txt)

            # if len(spec_min) < 1: y_spec_min = []
            # else: y_spec_min = [spec_min[0] for i in df_cpk[Period]]
            # if len(spec_max) < 1: y_spec_max = []
            # else: y_spec_max = [spec_max[0] for i in df_cpk[Period]]

            Cpk = cal_cpk(data=df_cpk[select_property].dropna().values, low_spec=spec_min[0], up_spec=spec_max[0])
            ppm = cpk_to_ppm(Cpk)

            chart_1 = px.histogram(df_cpk[select_property], x=select_property,title=select_property + " of Ppk: " + "{:,.4f}".format(Cpk))
            if spec_min[0]>0: chart_1.add_vline(x=spec_min[0], line_width=3, line_dash="dash", line_color="red", )
            if spec_max[0]>0: chart_1.add_vline(x=spec_max[0], line_width=3, line_dash="dash", line_color="purple", )
            # chart_1.add_vline(x=spec_max[0], line_width=3, line_dash="dash", line_color="red", name='upper Limit')

            graph_detail = select_property + " of Ppk: " + "{:,.4f} \n \n ==> Defect ratio: {:,.0f} ppm".format(Cpk, ppm) \
                + ""


        return [select_graph, chart_1, list_TOB, list_Property, list_Class, graph_detail, list_Property, list_Property]
    except Exception as e:
        alert(e)
        return