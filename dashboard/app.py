# dashboard/app.py

import dash
from dash import Dash, html, page_container
import dash_bootstrap_components as dbc

app = Dash(__name__, use_pages=True, external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "HydroFusion  | Control Center"

nav_links = [
    dbc.NavItem(dbc.NavLink([html.I(className=f"{page.get('icon', 'bi bi-file-earmark')} me-2"), page["name"]], href=page["relative_path"], active="exact"))
    for page in dash.page_registry.values() if page["path"] != "/"
]

navbar = dbc.NavbarSimple(
    brand=html.Span([html.I(className="bi bi-water me-2"), "HydroFusion "]),
    brand_href="/", children=nav_links, color="success", dark=True, sticky="top", className="mb-4 shadow"
)

app.layout = html.Div([navbar, dbc.Container(page_container, fluid=True, className="p-4")])

if __name__ == "__main__":
    app.run(debug=True, port=8050)