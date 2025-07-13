# dashboard/pages/monitoraggio.py

import dash
from dash import html, dcc, Input, Output, callback, State
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from dashboard.utils.grafici import linea_temporale_sensori, subplot_per_sorgente, crea_grafico_vuoto
from dashboard.utils.layout import titolo_sezione, stato_badge
from config.config import SENSOR_CONFIG, PANNELLO_CONFIG, NUM_SERRE, NUM_PESCINE, NUM_PANNELLI
from config.classificatore import classifica_stato

dash.register_page(__name__, path="/monitoraggio", name="Monitoraggio", title="HydroFusion | Monitoraggio", icon="bi bi-bar-chart-line-fill")
DB_PATH = "hydrofusion.db"

def carica_dati_filtrati(filtro_tipo, valore_filtro, limit=1000):
    if not valore_filtro: return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query(f"SELECT timestamp, sorgente_id, tipo, valore FROM misurazioni WHERE {filtro_tipo} = ? ORDER BY timestamp DESC LIMIT ?", conn, params=(valore_filtro, limit))
        conn.close()
        if not df.empty: df['stato'] = df.apply(lambda row: classifica_stato(row['tipo'], row['valore']), axis=1)
    except Exception as e:
        print(f"Errore caricamento dati: {e}"); df = pd.DataFrame()
    return df

def leggi_stati_attuali_da_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT sorgente_id, tipo, stato FROM stati_attuali", conn, index_col=['sorgente_id', 'tipo'])
        conn.close(); return df.to_dict()['stato']
    except Exception: return {}

opzioni_per_tipo = [{"label": k, "value": k} for k in sorted({**SENSOR_CONFIG, **PANNELLO_CONFIG}.keys())]
opzioni_per_sorgente = [{"label": f"Serra {i}", "value": f"Serra_{i}"} for i in range(1, NUM_SERRE + 1)] + \
                       [{"label": f"Pesci {i}", "value": f"Pesci_{i}"} for i in range(1, NUM_PESCINE + 1)] + \
                       [{"label": f"Pannello {i}", "value": f"Pannello_{i}"} for i in range(1, NUM_PANNELLI + 1)]

layout = dbc.Container([
    titolo_sezione("Monitoraggio Sensori in Tempo Reale", icona="bi bi-broadcast"),
    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col([html.Label("Modalità di Visualizzazione:"), dbc.RadioItems(id="selettore-vista", options=[{"label": "Per Tipo Sensore", "value": "tipo"}, {"label": "Per Sorgente", "value": "sorgente_id"}], value="tipo", inline=True)], md=6),
            dbc.Col([html.Label("Seleziona una voce da analizzare:"), dcc.Dropdown(id="dropdown-principale", clearable=False)], md=6),
        ]),
        html.Div(dcc.Loading(dcc.Graph(id="grafico-principale-monitoraggio")), className="mt-3", style={"maxHeight": "600px", "overflowY": "auto"})
    ])),
    html.Hr(),
    titolo_sezione("Stato Attuale di Tutti gli Impianti", icona="bi bi-hdd-stack-fill"),
    dcc.Loading(html.Div(id="contenitore-stati-attuali")),
    dcc.Interval(id="aggiorna-monitoraggio-interval", interval=5000, n_intervals=0)
], fluid=True)

@callback(Output("dropdown-principale", "options"), Output("dropdown-principale", "value"), Input("selettore-vista", "value"))
def aggiorna_opzioni_dropdown(vista_selezionata):
    if vista_selezionata == "tipo": return opzioni_per_tipo, opzioni_per_tipo[0]['value']
    else: return opzioni_per_sorgente, opzioni_per_sorgente[0]['value']

@callback(Output("grafico-principale-monitoraggio", "figure"), Input("dropdown-principale", "value"), Input("aggiorna-monitoraggio-interval", "n_intervals"), State("selettore-vista", "value"))
def aggiorna_grafico_principale(valore_selezionato, n, tipo_vista):
    df_dati = carica_dati_filtrati(tipo_vista, valore_selezionato)
    if df_dati.empty: return crea_grafico_vuoto(f"In attesa di dati per '{valore_selezionato}'...")
    
    df_dati['timestamp'] = pd.to_datetime(df_dati['timestamp'])
    fine_finestra = datetime.now()
    inizio_finestra = fine_finestra - timedelta(minutes=10)
    range_x = [inizio_finestra, fine_finestra]
        
    if tipo_vista == "tipo": return linea_temporale_sensori(df_dati, valore_selezionato, range_x=range_x)
    else: return subplot_per_sorgente(df_dati, valore_selezionato, range_x=range_x)

@callback(Output("contenitore-stati-attuali", "children"), Input("aggiorna-monitoraggio-interval", "n_intervals"))
def aggiorna_display_stati(n):
    stati = leggi_stati_attuali_da_db()
    if not stati: return dbc.Alert("In attesa dei dati di stato...", color="info")
    cards = [dbc.Col(dbc.Card(dbc.CardBody([
        html.H6(f"{sorgente_id}", className="card-title mb-1"),
        html.P(tipo, className="text-muted small mb-2"),
        stato_badge(stato)
    ]), className="text-center shadow-sm"), xs=6, sm=4, md=3, lg=2, className="mb-3") for (sorgente_id, tipo), stato in sorted(stati.items())]
    return dbc.Row(cards)