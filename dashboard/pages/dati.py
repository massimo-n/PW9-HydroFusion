# dashboard/pages/dati.py

import dash
from dash import html, dcc, callback, Input, Output
from dash.dash_table import DataTable # <-- L'import corretto
import dash_bootstrap_components as dbc
import pandas as pd
import sqlite3

from dashboard.utils.layout import titolo_sezione

# Registriamo la nuova pagina. La navbar dinamica la troverà automaticamente.
dash.register_page(
    __name__,
    path="/dati",
    name="Esplora Dati",
    title="HydroFusion | Dati Grezzi",
    icon="bi bi-table"
)

DB_PATH = "hydrofusion.db"

def carica_tabella_completa(nome_tabella):
    """Carica un'intera tabella dal database in un DataFrame Pandas."""
    try:
        conn = sqlite3.connect(DB_PATH)
        # Usiamo una query sicura per evitare SQL injection
        # (anche se qui il nome tabella è controllato, è buona pratica)
        if nome_tabella in ["misurazioni", "stati_attuali", "storico_allarmi", "dati_produzione", "dati_finanziari"]:
            df = pd.read_sql_query(f"SELECT * FROM {nome_tabella}", conn)
        else:
            df = pd.DataFrame() # Ritorna un df vuoto se il nome non è valido
        conn.close()
        return df
    except Exception as e:
        print(f"Errore caricamento tabella {nome_tabella}: {e}")
        return pd.DataFrame()

# --- Layout della Pagina ---
layout = dbc.Container([
    titolo_sezione("Esplorazione Dati Grezzi", icona="bi bi-table"),
    
    dbc.Alert(
        "Questa sezione consente di visualizzare i dati grezzi registrati nel database. È uno strumento potente per analisi approfondite e debugging.",
        color="info"
    ),

    dbc.Row([
        dbc.Col([
            html.Label("Seleziona la tabella da visualizzare:", className="fw-bold"),
            dcc.Dropdown(
                id="selettore-tabella-dati",
                options=[
                    {"label": "Misurazioni Sensori", "value": "misurazioni"},
                    {"label": "Stati Attuali", "value": "stati_attuali"},
                    {"label": "Storico Allarmi", "value": "storico_allarmi"},
                    {"label": "Dati di Produzione", "value": "dati_produzione"},
                    {"label": "Dati Finanziari", "value": "dati_finanziari"},
                ],
                value="misurazioni", # Tabella di default
                clearable=False
            )
        ], md=6, className="mb-3")
    ]),
    
    html.Hr(),
    
    # Il contenitore dove verrà renderizzata la tabella
    dcc.Loading(
        html.Div(id='contenitore-tabella-dati')
    )
    
], fluid=True)

# --- Callback ---
@callback(
    Output('contenitore-tabella-dati', 'children'),
    Input('selettore-tabella-dati', 'value')
)
def aggiorna_tabella_dati(nome_tabella_selezionata):
    """Carica i dati e crea il componente DataTable."""
    
    df = carica_tabella_completa(nome_tabella_selezionata)
    
    if df.empty:
        return dbc.Alert(f"La tabella '{nome_tabella_selezionata}' è vuota o non esiste.", color="warning")

    return DataTable(
        id='tabella-dati-visualizzata',
        # I dati devono essere passati come lista di dizionari
        data=df.to_dict('records'),
        # Le colonne vengono create dinamicamente dai nomi delle colonne del DataFrame
        columns=[{"name": i, "id": i} for i in df.columns],
        
        # --- Funzionalità Interattive ---
        page_size=25,              # Mostra 25 righe per pagina
        sort_action="native",      # Abilita l'ordinamento nativo (cliccando sugli header)
        filter_action="native",    # Abilita il filtro nativo (caselle di testo sotto gli header)
        
        # --- Stile ---
        style_table={'overflowX': 'auto'}, # Abilita lo scroll orizzontale se ci sono troppe colonne
        style_cell={'textAlign': 'left', 'minWidth': '120px', 'width': '150px', 'maxWidth': '200px', 'whiteSpace': 'normal'},
        style_header={'backgroundColor': '#E9ECEF', 'fontWeight': 'bold', 'border': '1px solid black'},
        style_data_conditional=[{
            'if': {'row_index': 'odd'},
            'backgroundColor': 'rgb(248, 248, 248)'
        }]
    )