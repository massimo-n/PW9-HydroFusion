# dashboard/pages/allarmi.py

import dash, json
from dash import html, dcc, Input, Output, callback
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
from dashboard.utils.layout import titolo_sezione, stato_badge

dash.register_page(__name__, path="/allarmi", name="Allarmi", title="HydroFusion | Allarmi", icon="bi bi-exclamation-triangle-fill")

DB_PATH = "hydrofusion.db"

def carica_allarmi_da_db(limit=50):
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT timestamp, sorgente_id, tipo, stato, azioni FROM storico_allarmi ORDER BY timestamp DESC LIMIT {limit}", conn)
        conn.close()
    except Exception as e:
        print(f"Errore caricamento allarmi: {e}"); df = pd.DataFrame(columns=["timestamp", "sorgente_id", "tipo", "stato", "azioni"])
    return df

def crea_tabella_allarmi(df):
    if df.empty: return dbc.Alert("✅ Nessun allarme recente registrato. L'impianto è in salute!", color="success")
    return dbc.Table([
        html.Thead(html.Tr([html.Th("⏱️ Orario"), html.Th("📍 Sorgente"), html.Th("🧪 Tipo Sensore"), html.Th("⚠️ Stato"), html.Th("🛠️ Azioni Suggerite")])),
        html.Tbody([
            html.Tr([
                html.Td(row["timestamp"]), html.Td(row["sorgente_id"]), html.Td(row["tipo"]),
                html.Td(stato_badge(row["stato"])), html.Td("; ".join(json.loads(row["azioni"])))
            ], className=f"table-{'danger' if row['stato'] == 'CRITICAL' else 'warning'}") for _, row in df.iterrows()
        ])
    ], bordered=True, hover=True, size="sm", responsive=True)

layout = dbc.Container([
    titolo_sezione("Storico degli Allarmi Recenti", icona="bi bi-exclamation-triangle-fill"),
    dbc.Alert("Questa tabella mostra gli ultimi 50 eventi con stato 'WARNING' o 'CRITICAL'.", color="info"),
    dcc.Loading(html.Div(id="tabella-allarmi-container"), type="default"),
    dcc.Interval(id="aggiorna-allarmi-interval", interval=10000, n_intervals=0)
], fluid=True)

@callback(Output("tabella-allarmi-container", "children"), Input("aggiorna-allarmi-interval", "n_intervals"))
def aggiorna_tabella_allarmi(n):
    return crea_tabella_allarmi(carica_allarmi_da_db())