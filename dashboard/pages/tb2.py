from dash_charlotte.components.table import (
    Table,
    TableTextCol,
    TableButtonCol,
    TableCheckBoxCol,
    TableDropdownCol,
    TableInputCol
)
from dash_charlotte.themes import charlotte_dark as cd
from dash import dcc
from dash import (
    register_page,
    html,
    callback,
    callback_context,
    Output,
    Input,
    ALL,
)
import dash_bootstrap_components as dbc
import numpy as np
import sqlite3
import pandas as pd

register_page(
    __name__,
    path = '/tb2',
    title = 'Forward Test Table'
)

CELL_STYLE = {
    'padding': 10,
    'text-align': 'center'
}

HEADER_STYLE = {
    'padding': 5,
    'text-align': 'center',
    'background-color': str(cd.BLUE)
}

BODY_STYLE = {
    'background-color': 'white',
    'cursor': 'pointer'
}


table_location = "/home/ash/Desktop/project/forward_test/trades.db"
table_name = "trades"
data = {}
df = None
column_names = []


def get_tbl_cols():
    conn = sqlite3.connect(table_location)
    query = f"select * from {table_name}"
    res = conn.execute(query)
    column_names = [i[0] for i in res.description]
    res = res.fetchall() #[(), (), ()]

    if not res:
        data = None
    else:
        tb_data = zip(*res)
        data = { col : next(tb_data) for col in column_names}
        df = pd.DataFrame(data)

    conn.close()

    return [
    TableTextCol(
    header = col,
    header_style = HEADER_STYLE,
    cell_style = CELL_STYLE,
    text = df[col],
    text_formatting = "" if "price" not  in col else '{:,.2f} $'.format
    ) for col in column_names

    ]


layout = dbc.Container([
        html.Div(
                children = [
                html.Div(
                id = "fd-table",
                ),
            dcc.Interval(
                    id = 'table-update',
                    interval = 1000,
                    n_intervals = 0
		        )
                ],
            className = 'shadow mt-5'
        )

    ])



@callback(Output('fd-table', 'children'), [Input('table-update', 'n_intervals')])
def update_table(n):
    return Table(
        columns = get_tbl_cols(),
        body_style = BODY_STYLE,
        bordered = True,
        dark = True,
        hover = True,
        responsive = True,
        striped = True,
        className = 'mb-0'
    )
