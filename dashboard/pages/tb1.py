from dash_charlotte.components.table import (
    Table,
    TableTextCol,
    TableButtonCol,
    TableCheckBoxCol,
    TableDropdownCol,
    TableInputCol
)
from dash_charlotte.themes import charlotte_dark as cd

from dash import (
    register_page,
    html,
    callback,
    callback_context,
    Output,
    Input,
    ALL
)
import dash_bootstrap_components as dbc
import numpy as np
import sqlite3
import pandas as pd

register_page(
    __name__,
    path = '/tb1',
    title = 'Backtest Table'
)

CELL_STYLE = {
    'padding': 5,
    'text-align': 'center'
}

HEADER_STYLE = {
    'padding': 10,
    'text-align': 'center',
    'background-color': str(cd.BLUE)
}

BODY_STYLE = {
    'background-color': 'white',
    'cursor': 'pointer'
}



table_location = "/home/ash/Desktop/project/backtest/backtest.db"
table_name = "backtest"
data = {}
df = None

# SQL connection
conn = sqlite3.connect(table_location)
query = f"select * from {table_name}"
print(query)
res = conn.execute(query)
column_names = [i[0] for i in res.description]
res = res.fetchall() #[(), (), ()]

if not res:
    data = None
else:
    tb_data = zip(*res)
    data = { col : next(tb_data) for col in column_names}
    df = pd.DataFrame(data)

columns = []

# text_formatting = 'R$ {:,.2f}'.format

for col in column_names:
    columns.append(TableTextCol(
    header = col,
    header_style = HEADER_STYLE,
    cell_style = CELL_STYLE,
    text = df[col],
    text_formatting = "" if "price" not  in col else '{:,.2f} $'.format
    ))


layout = dbc.Container([
    html.Div(
        children = Table(
            columns = columns,
            body_style = BODY_STYLE,
            bordered = True,
            dark = True,
            hover = True,
            responsive = True,
            striped = True,
            className = 'mb-0'
        ),
        className = 'shadow mt-5'
    )

])

    # data = {
    # "id" : next(tb_data),
    # "id" : next(tb_data),
    # "id" : next(tb_data),
    # }


# df = pd.DataFrame()
# df["id"] = [i[0] for i in res]

#or

# data = zip(*res)
# df["id"] = next(data)


"""

data = {
    'id' : [i[0] for i in res]
}
df = pd.DataFRame(data)

"""

#
# for i in range(len(res)):
#     res[i] (id, type, *)
#     df
#     """
