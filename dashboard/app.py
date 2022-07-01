from dash import Dash
import dash_bootstrap_components as dbc
import dash_labs as dl

from dash_charlotte import themes
from dash_charlotte.components import (
    Dashboard,
    Drawer,
    DrawerSingleItem,
    DrawerMultiItem,
    DrawerSubItem,
    DrawerFooter,
    Navbar
)


app = Dash(
    name = __name__,
    title = 'PLutus Dashboard',
    plugins = [dl.plugins.pages],
    external_stylesheets = [
        dbc.themes.BOOTSTRAP,
        themes.BOOTSTRAP,
        themes.BOXICONS,
        themes.FONTAWESOME,
        themes.CHARLOTTE_DARK
    ]
)



nav_links = [
    DrawerSingleItem(
        name = 'Login',
        icon = 'bx bx-log-in',
        href = '/login'
    ),
    DrawerMultiItem(
        name = 'Analytics',
        icon = 'bx bx-line-chart',
        href = '/trade',
        submenu = [
            DrawerSubItem(
                name = 'Model',
                href = '/model'
            ),
            DrawerSubItem(
                name = 'Backtest',
                href = '/backtest'
            ),
            DrawerSubItem(
                name = 'Forward Test',
                href = '/trade'
            ),
        ]
    ),
    DrawerMultiItem(
        name = 'Tables',
        icon = 'bx bx-table',
        href = '/tb2',
        submenu = [
            DrawerSubItem(
                name = "Backtest Table",
                href = "/tb1"
            ),
            DrawerSubItem(
                name = "Trades Table",
                href = "/tb2"
            )
        ]
    ),
    DrawerSingleItem(
        name = 'About',
        icon = 'bx bx-book',
        href = '/about'
    ),
    DrawerFooter(
        title = 'plutus',
        subtitle = 'GOD of Wealth'
    )
]



app.layout = Dashboard(
    children = dl.plugins.page_container,
    navbar = Navbar(
        title = '   Plutus'
    ),
    drawer = Drawer(
        menu = nav_links,
        logo_name = 'Plutus',
        logo_icon = 'fas fa-rocket'
    )
)


server = app.server


# if __name__ == '__main__':
#     app.run_server(host='127.0.0.1', debug=True)


if __name__ == '__main__':
    app.run_server(
        host = '0.0.0.0',
        port = 8000
    )
