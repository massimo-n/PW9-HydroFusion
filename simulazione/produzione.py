# simulazione/produzione.py

import sqlite3, time, random, json
from datetime import datetime
import pandas as pd
from infrastruttura.database import get_db_connection, _db_lock, execute_query
from infrastruttura.logger import log_system_message

PREZZO_KG_RACCOLTO, PREZZO_KG_PESCE, COSTO_OPERATIVO_ORARIO = 3.5, 8.0, 5.0
stato_produzione = {"biomassa_pesci_kg": 100.0, "raccolto_pronto_kg": 0.0, "profitto_totale_eur": -1000.0}

def calcola_efficienza_impianto():
    conn = None
    try:
        conn = get_db_connection()
        df_stati = pd.read_sql_query("SELECT stato FROM stati_attuali", conn)
        if df_stati.empty: return 0.5
        stati_ok, totale_stati = (df_stati['stato'] == 'OK').sum(), len(df_stati)
        return stati_ok / totale_stati if totale_stati > 0 else 0.5
    except Exception as e:
        log_system_message(f"[ERRORE] Calcolo efficienza fallito: {e}")
        return 0.5
    finally:
        if conn: conn.close()

def simula_ciclo_produzione():
    global stato_produzione
    timestamp, efficienza = datetime.now().isoformat(), calcola_efficienza_impianto()
    log_system_message(f"Efficienza impianto: {efficienza:.2%}")

    stato_produzione["biomassa_pesci_kg"] += random.uniform(0.5, 1.5) * efficienza
    stato_produzione["raccolto_pronto_kg"] += random.uniform(1.0, 3.0) * efficienza
    execute_query("INSERT INTO dati_produzione (timestamp, biomassa_pesci_kg, raccolto_pronto_kg, descrizione) VALUES (?, ?, ?, ?)", (timestamp, stato_produzione["biomassa_pesci_kg"], stato_produzione["raccolto_pronto_kg"], "Crescita oraria"))

    costi_parziali, ricavi_parziali, descr = COSTO_OPERATIVO_ORARIO, 0.0, "Costi operativi"
    if random.random() < 0.1: # 10% probabilità di vendita
        raccolto_v, pesci_v = stato_produzione["raccolto_pronto_kg"], stato_produzione["biomassa_pesci_kg"] * 0.1
        ricavi_parziali = (raccolto_v * PREZZO_KG_RACCOLTO) + (pesci_v * PREZZO_KG_PESCE)
        descr = f"Vendita: {raccolto_v:.1f}kg piante, {pesci_v:.1f}kg pesci"
        stato_produzione["raccolto_pronto_kg"], stato_produzione["biomassa_pesci_kg"] = 0.0, stato_produzione["biomassa_pesci_kg"] - pesci_v
        log_system_message(f"[VENDITA] Effettuata! Ricavo: {ricavi_parziali:.2f}€")
    
    profitto_parziale = ricavi_parziali - costi_parziali
    stato_produzione["profitto_totale_eur"] += profitto_parziale
    execute_query("INSERT INTO dati_finanziari (timestamp, ricavi, costi, profitto_parziale, profitto_cumulativo, descrizione) VALUES (?, ?, ?, ?, ?, ?)", (timestamp, ricavi_parziali, costi_parziali, profitto_parziale, stato_produzione["profitto_totale_eur"], descr))
    log_system_message(f"Ciclo finanziario completato. Profitto cumulativo: {stato_produzione['profitto_totale_eur']:.2f}€")

def avvia_thread_produzione(intervallo_secondi):
    while True:
        try: simula_ciclo_produzione(); time.sleep(intervallo_secondi)
        except Exception as e: log_system_message(f"[ERRORE] Thread produzione: {e}"); time.sleep(60)