# simulazione/motore.py

from datetime import datetime
from config.classificatore import classifica_stato, get_azioni_correttive, azioni_correttive_to_json
from infrastruttura.database import insert_misurazione, aggiorna_stato_attuale, insert_allarme
from infrastruttura.logger import log_misurazione, log_system_message

def esegui_ciclo_sensore(sorgente_id, tipo_sensore, generatore):
    valore = generatore.genera()
    stato = classifica_stato(tipo_sensore, valore)
    timestamp = datetime.now().isoformat()
    log_misurazione(sorgente_id, tipo_sensore, valore, stato)
    insert_misurazione(sorgente_id, tipo_sensore, valore, timestamp)
    aggiorna_stato_attuale(sorgente_id, tipo_sensore, stato, timestamp)
    if stato != "OK":
        azioni = get_azioni_correttive(tipo_sensore, stato)
        if azioni:
            log_system_message(f"[AZIONE] {sorgente_id} | {tipo_sensore} in {stato}. Suggerimenti: {'; '.join(azioni)}")
            azioni_json = azioni_correttive_to_json(tipo_sensore, stato)
            insert_allarme(sorgente_id, tipo_sensore, stato, azioni_json, timestamp)