# analizza_db.py

import sqlite3
import pandas as pd

DB_PATH = "hydrofusion.db"
pd.set_option('display.max_rows', 50) # Mostriamo fino a 50 righe per non tagliare l'output
pd.set_option('display.width', 120)  # Aumentiamo la larghezza della visualizzazione

def analizza_tabella(nome_tabella, conn):
    """Legge una tabella e la stampa in modo leggibile."""
    print("=" * 50)
    print(f"ANALISI TABELLA: {nome_tabella.upper()}")
    print("=" * 50)
    try:
        # Usiamo read_sql_query per leggere l'intera tabella in un DataFrame Pandas
        df = pd.read_sql_query(f"SELECT * FROM {nome_tabella}", conn)
        
        if df.empty:
            print("La tabella è vuota.\n")
            return
            
        print(f"Prime 15 righe:\n{df.head(15).to_string()}\n")
        print(f"Ultime 15 righe:\n{df.tail(15).to_string()}\n")
        print(f"Informazioni generali sulla tabella ({len(df)} righe totali):")
        df.info()
        print("\n")
        
    except Exception as e:
        print(f"Errore durante l'analisi della tabella {nome_tabella}: {e}\n")

if __name__ == "__main__":
    try:
        conn = sqlite3.connect(DB_PATH)
        
        tabelle_da_analizzare = [
            "misurazioni",
            "stati_attuali",
            "storico_allarmi",
            "dati_produzione",
            "dati_finanziari"
        ]
        
        for tabella in tabelle_da_analizzare:
            analizza_tabella(tabella, conn)
            
        conn.close()
        
    except Exception as e:
        print(f"Errore generale durante la connessione al DB: {e}")