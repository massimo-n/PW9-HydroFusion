# dashboard/pages/monitoraggio.py

import dash
from dash import html, dcc, Input, Output, callback, State, ctx
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np # Importiamo numpy per usare np.nan
import sqlite3
from datetime import datetime, timedelta

# Import delle utility e configurazioni
from dashboard.utils.grafici import linea_temporale_sensori, subplot_per_sorgente, crea_grafico_vuoto
from dashboard.utils.layout import titolo_sezione, stato_badge
from config.config import SENSOR_CONFIG, PANNELLO_CONFIG, NUM_SERRE, NUM_PESCINE, NUM_PANNELLI
from config.classificatore import classifica_stato

# Registrazione della pagina
dash.register_page(
    __name__,
    path="/monitoraggio",
    name="Monitoraggio",
    title="HydroFusion | Monitoraggio",
    icon="bi bi-bar-chart-line-fill"
)

DB_PATH = "hydrofusion.db"
MAX_DATAPOINTS_IN_STORE = 2000
MAX_TIME_GAP_MINUTES = 15 # Se il gap è > di questo, interrompiamo la linea

# --- FUNZIONI DI PREPARAZIONE DATI ---

def prepara_dati_per_grafico(df: pd.DataFrame) -> pd.DataFrame:
    """
     Inserisce dei NaN per interrompere le linee nei grafici
    dove ci sono lunghi intervalli senza dati.
    """
    if df.empty:
        return df

    # Assicuriamoci che il df sia ordinato per tempo
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')

    processed_dfs = []
    # Raggruppiamo per ogni singola linea che verrà disegnata (per ogni sorgente e tipo)
    for group_keys, group_df in df.groupby(['sorgente_id', 'tipo']):
        # Calcoliamo la differenza di tempo tra righe consecutive
        time_diffs = group_df['timestamp'].diff()
        
        # Identifichiamo i punti in cui il gap è troppo grande
        break_points_indices = time_diffs[time_diffs > timedelta(minutes=MAX_TIME_GAP_MINUTES)].index
        
        if not break_points_indices.empty:
            rows_to_insert = []
            for index in break_points_indices:
                # Creiamo una riga "fantasma" con valore NaN per spezzare la linea
                original_row = group_df.loc[index]
                # Inseriamo il NaN un secondo dopo l'ultimo punto valido
                nan_timestamp = original_row['timestamp'] - timedelta(seconds=1)
                
                # Creiamo la riga da inserire
                nan_row = {
                    'timestamp': nan_timestamp,
                    'sorgente_id': group_keys[0],
                    'tipo': group_keys[1],
                    'valore': np.nan, 
                    'stato': 'N/D'
                }
                rows_to_insert.append(nan_row)
            
            # Aggiungiamo le nuove righe e riordiniamo
            group_df = pd.concat([group_df, pd.DataFrame(rows_to_insert)], ignore_index=True)
            group_df = group_df.sort_values('timestamp')
        
        processed_dfs.append(group_df)
    
    return pd.concat(processed_dfs, ignore_index=True) if processed_dfs else pd.DataFrame()


# --- FUNZIONI DI CARICAMENTO DATI (rimangono uguali) ---
def carica_dati_filtrati(filtro_tipo, valore_filtro, limit=1000):
    
    if not valore_filtro: return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT timestamp, sorgente_id, tipo, valore FROM misurazioni WHERE {filtro_tipo} = ? ORDER BY timestamp DESC LIMIT ?"
        df = pd.read_sql_query(query, conn, params=(valore_filtro, limit))
        conn.close()
        if not df.empty:
            df['stato'] = df.apply(lambda row: classifica_stato(row['tipo'], row['valore']), axis=1)
    except Exception as e:
        print(f"Errore caricamento dati iniziali: {e}"); df = pd.DataFrame()
    return df

def carica_nuovi_dati(filtro_tipo, valore_filtro, ultimo_timestamp):
    
    if not valore_filtro or not ultimo_timestamp: return pd.DataFrame()
    try:
        conn = sqlite3.connect(DB_PATH)
        query = f"SELECT timestamp, sorgente_id, tipo, valore FROM misurazioni WHERE {filtro_tipo} = ? AND timestamp > ? ORDER BY timestamp ASC"
        df = pd.read_sql_query(query, conn, params=(valore_filtro, ultimo_timestamp))
        conn.close()
        if not df.empty:
            df['stato'] = df.apply(lambda row: classifica_stato(row['tipo'], row['valore']), axis=1)
    except Exception as e:
        print(f"Errore caricamento nuovi dati: {e}"); df = pd.DataFrame()
    return df

def leggi_stati_attuali_da_db():
    
    try:
        conn = sqlite3.connect(DB_PATH)
        df = pd.read_sql_query("SELECT sorgente_id, tipo, stato FROM stati_attuali", conn, index_col=['sorgente_id', 'tipo'])
        conn.close(); return df.to_dict()['stato']
    except Exception: return {}

# --- OPZIONI E LAYOUT (con modifica su Graph) ---
opzioni_per_tipo = [{"label": k, "value": k} for k in sorted({**SENSOR_CONFIG, **PANNELLO_CONFIG}.keys())]
opzioni_per_sorgente = [{"label": f"Serra {i}", "value": f"Serra_{i}"} for i in range(1, NUM_SERRE + 1)] + \
                       [{"label": f"Pesci {i}", "value": f"Pesci_{i}"} for i in range(1, NUM_PESCINE + 1)] + \
                       [{"label": f"Pannello {i}", "value": f"Pannello_{i}"} for i in range(1, NUM_PANNELLI + 1)]

layout = dbc.Container([
    titolo_sezione("Monitoraggio Sensori in Tempo Reale", icona="bi bi-broadcast"),
    dbc.Card(dbc.CardBody([
        dbc.Row([
            dbc.Col(dbc.RadioItems(id="selettore-vista", options=[{"label": "Per Tipo Sensore", "value": "tipo"}, {"label": "Per Sorgente", "value": "sorgente_id"}], value="tipo", inline=True), md=6),
            dbc.Col(dcc.Dropdown(id="dropdown-principale", clearable=False), md=6),
        ]),
        html.Div(dcc.Loading(
            #  Aggiunta di uirevision per ridurre il flash
            dcc.Graph(id="grafico-principale-monitoraggio", config={'scrollZoom': True})
        ), className="mt-3", style={"maxHeight": "600px", "overflowY": "auto"})
    ])),
    dcc.Store(id='dati-grafico-store'),
    dcc.Interval(id="aggiorna-dati-interval", interval=5000, n_intervals=0),
    html.Hr(),
    titolo_sezione("Stato Attuale di Tutti gli Impianti", icona="bi bi-hdd-stack-fill"),
    dcc.Loading(html.Div(id="contenitore-stati-attuali")),
    dcc.Interval(id="aggiorna-stati-interval", interval=5000, n_intervals=0)
], fluid=True)


# --- CALLBACKS ---

@callback(Output("dropdown-principale", "options"), Output("dropdown-principale", "value"), Input("selettore-vista", "value"))
def aggiorna_opzioni_dropdown(vista_selezionata):
    if vista_selezionata == "tipo": return opzioni_per_tipo, opzioni_per_tipo[0]['value']
    return opzioni_per_sorgente, opzioni_per_sorgente[0]['value']

@callback(
    Output('dati-grafico-store', 'data'),
    Input('aggiorna-dati-interval', 'n_intervals'),
    Input("selettore-vista", "value"),
    Input("dropdown-principale", "value"),
    State('dati-grafico-store', 'data')
)
def aggiorna_dati_nello_store(n, tipo_vista, valore_selezionato, dati_attuali):
    trigger = ctx.triggered_id
    
    if trigger in ["selettore-vista", "dropdown-principale"]:
        df = carica_dati_filtrati(tipo_vista, valore_selezionato)
        return df.to_dict('records') if not df.empty else []

    if trigger == 'aggiorna-dati-interval':
        if not dati_attuali: return dash.no_update
        df_vecchio = pd.DataFrame(dati_attuali)
        if df_vecchio.empty: return dash.no_update
        
        ultimo_timestamp = df_vecchio['timestamp'].max()
        df_nuovo = carica_nuovi_dati(tipo_vista, valore_selezionato, ultimo_timestamp)

        if df_nuovo.empty: return dash.no_update
        
        df_completo = pd.concat([df_vecchio, df_nuovo]).drop_duplicates(subset=['timestamp', 'sorgente_id', 'tipo']).sort_values('timestamp')
        
        if len(df_completo) > MAX_DATAPOINTS_IN_STORE:
            df_completo = df_completo.tail(MAX_DATAPOINTS_IN_STORE)
            
        return df_completo.to_dict('records')

    return dash.no_update

@callback(
    Output("grafico-principale-monitoraggio", "figure"),
    Input('dati-grafico-store', 'data'),
    State("selettore-vista", "value"),
    State("dropdown-principale", "value"),
    State("grafico-principale-monitoraggio", "relayoutData")
)
def aggiorna_grafico_da_store(dati_json, tipo_vista, valore_selezionato, relayout_data):
    if not dati_json:
        return crea_grafico_vuoto(f"In attesa di dati per '{valore_selezionato}'...")

    df_dati_grezzi = pd.DataFrame(dati_json)
    
    #  Prepariamo i dati inserendo i NaN dove necessario
    df_dati_preparati = prepara_dati_per_grafico(df_dati_grezzi)

    range_x = None
    if relayout_data and 'xaxis.range[0]' in relayout_data:
        range_x = [relayout_data['xaxis.range[0]'], relayout_data['xaxis.range[1]']]
    else:
        fine_finestra = datetime.now()
        inizio_finestra = fine_finestra - timedelta(minutes=10)
        range_x = [inizio_finestra, fine_finestra]

    if tipo_vista == "tipo":
        fig = linea_temporale_sensori(df_dati_preparati, valore_selezionato, range_x=range_x)
    else:
        fig = subplot_per_sorgente(df_dati_preparati, valore_selezionato, range_x=range_x)

    #  Aggiungiamo uirevision per un aggiornamento più fluido
    fig.update_layout(uirevision=valore_selezionato)

    return fig

@callback(
    Output("contenitore-stati-attuali", "children"),
    Input("aggiorna-stati-interval", "n_intervals")
)
def aggiorna_display_stati(n):
    stati = leggi_stati_attuali_da_db()
    if not stati: return dbc.Alert("In attesa dei dati di stato...", color="info")
    
    cards = [
        dbc.Col(dbc.Card(dbc.CardBody([
            html.H6(f"{sorgente_id}", className="card-title mb-1"),
            html.P(tipo, className="text-muted small mb-2"),
            stato_badge(stato)
        ]), className="text-center shadow-sm"), xs=6, sm=4, md=3, lg=2, className="mb-3")
        for (sorgente_id, tipo), stato in sorted(stati.items())
    ]
    return dbc.Row(cards)