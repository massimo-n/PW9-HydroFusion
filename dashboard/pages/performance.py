# dashboard/pages/performance.py

import dash
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
from dashboard.utils.layout import titolo_sezione, kpi_card
from dashboard.utils.grafici import grafico_produzione, grafico_finanziario

dash.register_page(__name__, path="/performance", name="Performance", title="HydroFusion | Performance", icon="bi bi-graph-up-arrow")
DB_PATH = "hydrofusion.db"

def carica_dati_performance():
    try:
        conn = sqlite3.connect(DB_PATH)
        df_produzione = pd.read_sql_query("SELECT * FROM dati_produzione ORDER BY timestamp DESC LIMIT 300", conn)
        df_finanziario = pd.read_sql_query("SELECT * FROM dati_finanziari ORDER BY timestamp DESC LIMIT 300", conn)
        conn.close(); return df_produzione, df_finanziario
    except Exception as e:
        print(f"Errore caricamento dati performance: {e}"); return pd.DataFrame(), pd.DataFrame()

layout = dbc.Container([
    titolo_sezione("Analisi delle Performance Aziendali", icona="bi bi-graph-up-arrow"),
    dbc.Row(id="kpi-container", className="mb-4"),
    dbc.Row([
        dbc.Col(dcc.Loading(dcc.Graph(id="grafico-performance-produzione")), lg=6),
        dbc.Col(dcc.Loading(dcc.Graph(id="grafico-performance-finanziaria")), lg=6),
    ]),
    dcc.Interval(id="aggiorna-performance-interval", interval=15000, n_intervals=0)
], fluid=True)

@callback(Output("kpi-container", "children"), Output("grafico-performance-produzione", "figure"), Output("grafico-performance-finanziaria", "figure"), Input("aggiorna-performance-interval", "n_intervals"))
def aggiorna_pagina_performance(n):
    df_prod, df_fin = carica_dati_performance()

    profitto = f"{df_fin['profitto_cumulativo'].iloc[0]:,.2f}" if not df_fin.empty else "N/D"
    ricavi = f"{df_fin[df_fin['ricavi'] > 0]['ricavi'].sum():,.2f}" if not df_fin.empty else "N/D"
    biomassa = f"{df_prod['biomassa_pesci_kg'].iloc[0]:,.2f}" if not df_prod.empty else "N/D"
    raccolto = f"{df_prod['raccolto_pronto_kg'].iloc[0]:,.2f}" if not df_prod.empty else "N/D"
    
    kpi_cards = [
        dbc.Col(kpi_card("Profitto Cumulativo", profitto, "bi bi-cash-stack", unita="€", colore="primary"), md=3),
        dbc.Col(kpi_card("Ricavi (ultimi cicli)", ricavi, "bi bi-currency-euro", unita="€"), md=3),
        dbc.Col(kpi_card("Biomassa Pesci", biomassa, "bi bi-clipboard-data", unita="kg"), md=3),
        dbc.Col(kpi_card("Raccolto Pronto", raccolto, "bi bi-basket2-fill", unita="kg"), md=3),
    ]

    return kpi_cards, grafico_produzione(df_prod), grafico_finanziario(df_fin)