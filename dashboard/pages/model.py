import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import numpy as np
import plotly.graph_objects as go
import plotly.express as px

from dash_charlotte.components import Box
import dash_charlotte.themes.charlotte_light as cl

import yfinance as yf
df = yf.download("ETH-USD", period="6d", interval="5m")


dash.register_page(
    __name__,
    path = '/model',
    title = 'Example Page 1'
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
    dbc.CardHeader("Asset Details and Backtest Result"),
    dbc.CardBody(
        [
            html.H5("ETHERIUM / USD", className="card-title"),
            html.P("", className="alignment",),
            html.P("Time Frame : 5m ", className="card-text",),
            html.P("Time period : 20/04/21 - 20/05/23 ", className="card-text",),
            html.P("Time Frame : 5m ", className="card-text",),
            html.P("", className="alignment",),
            html.P("Model Used : LSTM model ", className="card-text",),
            html.P("accuracy obtained : 90% ", className="card-text",),
            html.P("Training time : 30 min ", className="card-text",),
        ]
    ),
]



layout = [
    dbc.Row([
        dbc.Col(
            Box(
                children = dcc.Graph(
                    figure = px.line(df, x=df.index, y=df.Close, labels={
                        "Datetime" : "Date"
                    }, title="ETH-USD Close Prices")
                )
            ),
            width = 12,
            lg = 6
        ),

        dbc.Col(
            Box(
                children = dcc.Graph(
                    figure = px.line(df, x=df.index, y=df.Close, labels={
                        "Datetime" : "Date"
                    }, title="ETH-USD Close Prices(predicted)")
                )
            ),
            width = 12,
            lg = 6
        )],

        className = 'g-0'
    ),

    dbc.Row([
        dbc.Col(
            Box(
                children = dcc.Graph(
                    figure = px.line(df, x=df.index, y=df.Close, labels={
                        "Datetime" : "Date"
                    }, title="ETH-USD Close Prices(comparison)")
                )
            ),
            width = 8,
            # lg = 6
        ),

        dbc.Col(
            Box(
                children = dbc.Card(content, color="dark", inverse=True)
            ),
            width = 4,
            # lg = 6
        )],

        className = 'g-0'
    )

]
                




