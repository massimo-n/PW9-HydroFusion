# simulazione/main.py

import time, threading, random
from config.config import NUM_SERRE, SENSORI_PER_SERRA, NUM_PESCINE, SENSORI_PER_PESCI, NUM_PANNELLI
from simulazione.motore import esegui_ciclo_sensore
from simulazione.generatori import GeneratoreSensore
from simulazione.produzione import avvia_thread_produzione
from infrastruttura.database import setup_database
from infrastruttura.logger import setup_logging, log_system_message

def avvia_thread_sensore(sorgente_id, tipo_sensore, intervallo_secondi):
    try:
        generatore = GeneratoreSensore(tipo_sensore, inerzia=random.uniform(0.92, 0.98), prob_anomalia=random.uniform(0.01, 0.04))
        generatore.mu += random.uniform(-generatore.sigma * 0.2, generatore.sigma * 0.2)
        log_system_message(f"Thread avviato per: {sorgente_id} - {tipo_sensore}")
    except ValueError as e:
        log_system_message(f"[ERRORE] Creazione generatore fallita per {tipo_sensore}: {e}"); return
    while True:
        try: esegui_ciclo_sensore(sorgente_id, tipo_sensore, generatore); time.sleep(intervallo_secondi)
        except Exception as e: log_system_message(f"[ERRORE] Thread {sorgente_id}-{tipo_sensore}: {e}"); time.sleep(60)

def main():
    setup_logging()
    log_system_message("==========================================")
    log_system_message("  Avvio del Simulatore HydroFusion      ")
    log_system_message("==========================================")
    setup_database()

    threads, sensori_da_simulare = [], []
    for i in range(1, NUM_SERRE + 1): sensori_da_simulare.extend([(f"Serra_{i}", tipo, 5) for tipo in SENSORI_PER_SERRA])
    for i in range(1, NUM_PESCINE + 1): sensori_da_simulare.extend([(f"Pesci_{i}", tipo, 7) for tipo in SENSORI_PER_PESCI])
    for i in range(1, NUM_PANNELLI + 1): sensori_da_simulare.append((f"Pannello_{i}", "Produzione", 10))
    
    for sorgente, tipo, intervallo in sensori_da_simulare:
        thread = threading.Thread(target=avvia_thread_sensore, args=(sorgente, tipo, intervallo), daemon=True)
        threads.append(thread)
    
    threads.append(threading.Thread(target=avvia_thread_produzione, args=(15,), daemon=True))
    
    for t in threads: t.start(); time.sleep(0.1)
    
    log_system_message(f"Simulazione avviata. {len(threads)} thread attivi. Premi Ctrl+C per terminare.")
    try:
        while True: time.sleep(3600)
    except KeyboardInterrupt:
        log_system_message("\nSimulazione terminata.")

if __name__ == "__main__":
    main()