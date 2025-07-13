# dashboard/utils/layout.py

from dash import html
import dash_bootstrap_components as dbc

def titolo_sezione(testo: str, icona: str = "bi bi-bar-chart-line-fill"):
    return html.H2([html.I(className=f"{icona} me-2"), testo], className="mb-4 mt-2")

def stato_badge(stato: str) -> dbc.Badge:
    colori = {"OK": "success", "WARNING": "warning", "CRITICAL": "danger", "UNKNOWN": "secondary"}
    return dbc.Badge(stato, color=colori.get(stato, "secondary"), className="ms-1")

def kpi_card(titolo, valore, icona, unita="", colore="success"):
    return dbc.Card(dbc.CardBody([
        html.H6(titolo, className="card-title text-muted"),
        html.H3(f"{valore} {unita}", className=f"text-{colore}"),
        html.I(className=f"{icona} position-absolute top-0 end-0 p-3 h1 text-muted opacity-25")
    ]), className="position-relative")