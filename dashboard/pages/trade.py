import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf

import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html, callback
from dash_charlotte.components import Box
import dash_charlotte.themes.charlotte_light as cl

import sys
sys.path.append("..")

import bybit_functions as bf


df = yf.download("ETH-USD", period="1d", interval="1m")
ticker = "ETHUSD"


dash.register_page(
    __name__,
    path = '/trade',
    title = 'Forward Test'
)


COLORS = [
    str(cl.YELLOW),
    str(cl.ORANGE),
    str(cl.RED),
    str(cl.BLUE),
    str(cl.PURPLE)
]

# header = dbc.Container("Prediction Model", className="header")

# card contents

content = [
    dbc.CardHeader("Trade Details"),
    dbc.CardBody(
        [
            html.H5("ETHERIUM / USD", className="card-title"),
            html.P("", className="alignment",),
            html.P("Time Frame : 5m ", className="card-text",),
            html.P("", className="alignment",),
            html.P("Stop loss: 0.4 % ", className="card-text",),
            html.P("Take profit: 0.5 % ", className="card-text",),
            html.P("Strategy Used : 3 EMA Crossover  ", className="card-text",),
            html.P("Model Used : LSTM model ", className="card-text",),
        ]
    ),
]



layout = [
    dbc.Row([
        dbc.Col(
            Box(
                children = [
                dcc.Graph(id = 'live-graph', animate = True),
		        dcc.Interval(
                    id = 'graph-update',
                    interval = 1000,
                    n_intervals = 0
		        ),
            ]
            ),
            width = 12,
            lg = 10,
            style={
                "margin": "2rem auto"
            }
        ),

        ],

        className = 'g-0'
    ),

    dbc.Row([
        dbc.Col(
            Box(
                children = dbc.Card(content, color="dark", inverse=True)
            ),
            width = 12,
            lg = 3
        ),

        dbc.Col([
            Box(
            id = "account_data",
            children =[]
            # children = dbc.Card(account_content, color="dark", inverse=True)
            ),
            dcc.Interval(
                 id = 'account-update',
                 interval = 1000 * 10,
                 n_intervals = 0
             )],
            width = 12,
            lg = 8,
            style={
                "margin-left" : "2rem"
            }
        )],

        className = 'g-0'
    )

]


@callback(
    Output("live-graph", "figure"),
    [ Input('graph-update', 'n_intervals') ]
)

def update_graph(n):
    df[-1:] = yf.download("ETH-USD", period="1d", interval="1m" )[-1:]
    data = px.line(df, x=df.index, y=df.Close, labels={
                        "Datetime" : "Date"
                    }, title="ETH-USD Close Prices")

    return data


# account_data callback
@callback(
    Output("account_data", "children"),
    [ Input('account-update', 'n_intervals') ]
)

def update_account(n):
    # print('card content updated')
    account_data = bf.get_position(ticker)
    print(account_data)
    # input('wait')

    account_content = [
        dbc.CardHeader("Account Info"),
        dbc.CardBody(
            [
                html.P(f"{col} : {val} ", className="card-text",) for col,val in account_data.items()
            ]
            if account_data else html.H5("Sorry No Data Available...")
        ),
    ]

    return dbc.Card(account_content, color="dark", inverse=True)
