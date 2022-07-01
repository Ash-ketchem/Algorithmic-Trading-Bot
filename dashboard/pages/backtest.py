import dash
from dash import dcc
import dash_bootstrap_components as dbc
from dash import Input, Output, State, dcc, html
import numpy as np
import plotly.graph_objects as go
from pickle import load

from dash_charlotte.components import Box
import dash_charlotte.themes.charlotte_light as cl


backtest_res_loc = "/home/ash/Desktop/project/backtest/backtest_results.txt"

dash.register_page(
    __name__,
    path = '/backtest',
    title = 'Backtest Results'
)


COLORS = [
    str(cl.RED),
    str(cl.YELLOW),
    str(cl.ORANGE),
    str(cl.BLUE)
]


with open(backtest_res_loc, "rb") as f:
    backtest_results = load(f)


results =  [
    dbc.CardHeader("Backtest Summary"),
    dbc.CardBody(
        [
            html.H5(backtest_results["asset"], className="card-title"),
            html.P("", className="alignment",),
            html.P(f"Time Frame : {backtest_results['asset']} ", className="card-text",),
            html.P(f"Time period :{backtest_results['time_period']} ", className="card-text",),
            html.P("", className="alignment",),
            html.P(f"Total Trades : {backtest_results['total_trades']} ", className="card-text",),
            html.P(f"Winners : {backtest_results['winners']} ", className="card-text",),
            html.P(f"Losers : {backtest_results['losers']} ", className="card-text",),
            html.P(f"Evens : {backtest_results['evens']} ", className="card-text",),
            html.P(f"Win rate :{backtest_results['total_trades']} % ", className="card-text",),
            html.P(f"Win rate (with evens) : {backtest_results['win_rate_with_even']} % ", className="card-text",),

        ]
    ),
]

add_info =  [
    dbc.CardHeader("Additional Info"),
    dbc.CardBody(
        [

            html.P("Win rate : 65 % ", className="card-text",),
            html.P("Win rate (with evens) : 68% ", className="card-text",),
        ]
    ),
]

layout = [
    dbc.Row([
       dbc.Col(
            Box(
                children = dcc.Graph(
                    figure = go.Figure(
                        data = go.Pie(
                            labels = ["Wins", "Losses", "Evens"],
                            values = [60, 35, 5],
                            marker = {
                                'colors': COLORS
                            }
                        ),
                        layout = {
                            'paper_bgcolor': 'rgba(0,0,0,0)',
                            'margin': {
                                't': 20, 'b': 20, 'l': 20, 'r': 20
                            }
                        }
                    )
                )
            ),
            width = 12,
            lg = 6
        ),

        dbc.Col(
            Box(
                children = dbc.Card(results, color="dark", inverse=True)
            ),
            width = 12,
            lg = 6
        )


    ]),

    dbc.Row([
       dbc.Col(
            Box(
                children = dcc.Graph(
                    figure = go.Figure(
                        data = go.Pie(
                            labels = ["Wins", "Losses", "Evens"],
                            values = [60, 35, 5],
                            marker = {
                                'colors': COLORS
                            }
                        ),
                        layout = {
                            'paper_bgcolor': 'rgba(0,0,0,0)',
                            'margin': {
                                't': 20, 'b': 20, 'l': 20, 'r': 20
                            }
                        }
                    )
                )
            ),
            width = 12,
            lg = 6
        ),

         dbc.Col(
            Box(
                children = dbc.Card(results, color="dark", inverse=True)
            ),
            width = 12,
            lg = 6
        )

    ]),
]
