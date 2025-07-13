# infrastruttura/database.py

import sqlite3
import threading

DB_PATH = "hydrofusion.db"
_db_lock = threading.Lock()

def get_db_connection():
    return sqlite3.connect(DB_PATH, timeout=10)

def setup_database():
    with _db_lock:
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS misurazioni (id INTEGER PRIMARY KEY, sorgente_id TEXT NOT NULL, tipo TEXT NOT NULL, valore REAL NOT NULL, timestamp TEXT NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS stati_attuali (sorgente_id TEXT NOT NULL, tipo TEXT NOT NULL, stato TEXT NOT NULL, timestamp TEXT NOT NULL, PRIMARY KEY (sorgente_id, tipo))")
            cursor.execute("CREATE TABLE IF NOT EXISTS storico_allarmi (id INTEGER PRIMARY KEY, sorgente_id TEXT NOT NULL, tipo TEXT NOT NULL, stato TEXT NOT NULL, azioni TEXT, timestamp TEXT NOT NULL)")
            cursor.execute("CREATE TABLE IF NOT EXISTS dati_finanziari (id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, ricavi REAL NOT NULL, costi REAL NOT NULL, profitto_parziale REAL NOT NULL, profitto_cumulativo REAL NOT NULL, descrizione TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS dati_produzione (id INTEGER PRIMARY KEY, timestamp TEXT NOT NULL, biomassa_pesci_kg REAL, raccolto_pronto_kg REAL, descrizione TEXT)")
            conn.commit()
            print("[DB] Database impostato correttamente.")
        finally:
            conn.close()

def execute_query(query, params=()):
    with _db_lock:
        conn = get_db_connection()
        try:
            conn.execute(query, params)
            conn.commit()
        finally:
            conn.close()

def insert_misurazione(sorgente_id, tipo, valore, timestamp):
    execute_query("INSERT INTO misurazioni (sorgente_id, tipo, valore, timestamp) VALUES (?, ?, ?, ?)", (sorgente_id, tipo, valore, timestamp))

def aggiorna_stato_attuale(sorgente_id, tipo, stato, timestamp):
    execute_query("INSERT OR REPLACE INTO stati_attuali (sorgente_id, tipo, stato, timestamp) VALUES (?, ?, ?, ?)", (sorgente_id, tipo, stato, timestamp))

def insert_allarme(sorgente_id, tipo, stato, azioni_json, timestamp):
    if stato in ["WARNING", "CRITICAL"]:
        execute_query("INSERT INTO storico_allarmi (sorgente_id, tipo, stato, azioni, timestamp) VALUES (?, ?, ?, ?, ?)", (sorgente_id, tipo, stato, azioni_json, timestamp))