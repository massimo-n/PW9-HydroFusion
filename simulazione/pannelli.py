# simulazione/pannelli.py

import random
from datetime import datetime
from config.config import PANNELLO_CONFIG, AZIONI_CORRETTIVE
from config.classificatore import classifica_stato, azioni_correttive
from infrastruttura.database import insert_misurazione, insert_stato_sensore
from infrastruttura.logger import log_misurazione, log_azione

def genera_produzione():
    """
    Simula un valore di produzione energetica (kWh) da pannello solare.
    """
    conf = PANNELLO_CONFIG["Produzione"]
    valore = random.gauss(conf["mu"], conf["sigma"])
    return round(valore, 2)

def analizza_pannello(pannello_id):
    """
    Simula, valuta e registra la produzione solare di un pannello.
    """
    valore = genera_produzione()
    stato = classifica_stato("Produzione", valore)
    timestamp = datetime.now().isoformat()

    insert_misurazione(pannello_id, f"{pannello_id}_Prod", "Produzione", valore, timestamp)
    log_misurazione(pannello_id, f"{pannello_id}_Prod", "Produzione", valore, stato)

    if stato != "OK":
        azioni = azioni_correttive("Produzione", stato)
        azioni_str = "; ".join(azioni)
        insert_stato_sensore(pannello_id, f"{pannello_id}_Prod", "Produzione", stato, azioni_str, timestamp)
        log_azione(stato, azioni)