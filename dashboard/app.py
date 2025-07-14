# dashboard/app.py

import dash
from dash import Dash, html, dcc, page_container, callback, Input, Output, State, no_update
import dash_bootstrap_components as dbc
import sqlite3

# Registrazione dell'app
app = Dash(
    __name__, 
    use_pages=True, 
    external_stylesheets=[dbc.themes.FLATLY, dbc.icons.BOOTSTRAP], 
    suppress_callback_exceptions=True
)
app.title = "HydroFusion | Control Center"

DB_PATH = "hydrofusion.db" # Percorso al database

# --- NAVBAR (rimane invariata) ---
nav_links = [
    dbc.NavItem(dbc.NavLink([html.I(className=f"{page.get('icon', 'bi bi-file-earmark')} me-2"), page["name"]], href=page["relative_path"], active="exact"))
    for page in dash.page_registry.values() if page["path"] != "/"
]

navbar = dbc.NavbarSimple(
    brand=html.Span([html.I(className="bi bi-water me-2"), "HydroFusion "]),
    brand_href="/", children=nav_links, color="success", dark=True, sticky="top", className="mb-4 shadow"
)


# --- LAYOUT PRINCIPALE CON I NUOVI COMPONENTI PER GLI ALERT ---
app.layout = html.Div([
    navbar, 
    dbc.Container(page_container, fluid=True, className="p-4"),

    # MODIFICA 1: Aggiunta dei componenti per i toast
    dcc.Store(id='last-alert-id-store', data=0), # Memorizza l'ID dell'ultimo allarme mostrato
    dcc.Interval(id='alert-interval', interval=7000, n_intervals=0), # Controlla ogni 7 secondi
    
    # Il componente Toast. È "nascosto" finché la sua `is_open` non diventa True.
    dbc.Toast(
        id="alert-toast",
        header="Nuovo Allarme",
        is_open=False,
        duration=8000, # Il toast scompare dopo 8 secondi
        dismissable=True,
        icon="danger", # L'icona di default è 'danger', la cambieremo dinamicamente
        # Posiziona il toast 
        style={"position": "fixed", "top": 66, "right": 10, "width": 350, "zIndex": 9999},
    ),
])


# --- FUNZIONE HELPER PER INTERROGARE IL DB ---
def get_latest_alert(last_id=0):
    """
    Controlla se c'è un allarme con ID > last_id.
    Restituisce i dati dell'allarme più recente, o None se non ce ne sono.
    """
    try:
        conn = sqlite3.connect(DB_PATH)
        # Usiamo ORDER BY id DESC e LIMIT 1 per prendere solo l'ultimo allarme nuovo,
        # evitando una "tempesta" di toast se si verificano più allarmi contemporaneamente.
        query = "SELECT id, sorgente_id, tipo, stato FROM storico_allarmi WHERE id > ? ORDER BY id DESC LIMIT 1"
        cursor = conn.cursor()
        # Usiamo i parametri per la sicurezza
        res = cursor.execute(query, (last_id,)).fetchone()
        conn.close()
        return res
    except Exception as e:
        print(f"Errore controllo allarmi: {e}")
        return None


# --- CALLBACK PER GESTIRE I TOAST ---
@callback(
    Output("alert-toast", "is_open"),
    Output("alert-toast", "header"),
    Output("alert-toast", "children"),
    Output("alert-toast", "icon"),
    Output("last-alert-id-store", "data"),
    Input("alert-interval", "n_intervals"),
    State("last-alert-id-store", "data")
)
def show_alert_toast(n, last_shown_id):
    """
    Questa callback si attiva a intervalli regolari per controllare se ci sono nuovi allarmi.
    """
    # Inizializziamo l'ID se è la prima esecuzione
    last_id = last_shown_id if last_shown_id is not None else 0

    latest_alert = get_latest_alert(last_id)

    # Se non ci sono nuovi allarmi, non facciamo nulla (no_update è molto efficiente)
    if not latest_alert:
        return no_update, no_update, no_update, no_update, no_update

    # Se c'è un nuovo allarme, estraiamo i dati
    new_id, sorgente, tipo_sensore, stato = latest_alert
    
    # Prepariamo il contenuto del toast
    header_text = f"⚠️ ALLARME {stato}"
    icon_color = "danger" if stato == "CRITICAL" else "warning"
    
    toast_body = dbc.Alert(
        f"Rilevato stato {stato} per il sensore {tipo_sensore} in {sorgente}!",
        color=icon_color,
        className="m-0" # Rimuove margini per un look pulito dentro il toast
    )

    # Ritorniamo i nuovi valori per aprire e popolare il toast, e aggiorniamo l'ID dell'ultimo allarme
    return True, header_text, toast_body, icon_color, new_id


# --- ESECUZIONE DELL'APP (rimane invariata) ---
if __name__ == "__main__":
    app.run(debug=True, port=8050)