# dashboard/pages/home.py

import dash
from dash import html
import dash_bootstrap_components as dbc
from dashboard.utils.layout import titolo_sezione

dash.register_page(__name__, path="/", name="Home", title="HydroFusion | Home", icon="bi bi-house-door-fill")

descrizione = "Benvenuto in HydroFusion, il centro di controllo per la gestione intelligente del tuo impianto acquaponico. Da questa interfaccia potrai monitorare in tempo reale lo stato di salute dei tuoi sensori, analizzare lo storico degli allarmi e valutare le performance produttive e finanziarie della tua azienda."

layout = dbc.Container([
    titolo_sezione("Benvenuto nel Sistema HydroFusion", icona="bi bi-house-door-fill"),
    dbc.Row(dbc.Col(dbc.Card(dbc.CardBody([
        html.P(descrizione, className="lead"),
        html.Hr(),
        html.P("Usa la barra di navigazione in alto per esplorare le diverse sezioni:"),
        html.Ul([
            html.Li("📡 Monitoraggio: Controlla i dati dei sensori in tempo reale."),
            html.Li("🚨 Allarmi: Visualizza lo storico degli eventi critici."),
            html.Li("📈 Performance: Analizza i dati di produzione e i risultati finanziari."),
        ])
    ])), md=8), justify="center")
], fluid=True)