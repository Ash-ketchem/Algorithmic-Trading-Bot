from dash import register_page
import dash_bootstrap_components as dbc
from dash import html

register_page(__name__, path="/", title="PLUTUS")

home_screen = html.Div(
    "",
    style={
        "overflow": "hidden",
        "background-image": "url('assets/img/eren2.jpg')",
        "background-size": "cover",
        "background-repeat": "no-repeat",
        "height": "90vh",
        "border-radius": "10px",
        #  "filter": "blur(0.55px)",
        # "-webkit-filter": "blur(0.55px)"
    },
)


layout = home_screen
