# simulazione/pesci.py

import random
from datetime import datetime
from config.config import PESCI_SENSORI, SENSOR_CONFIG
from config.classificatore import classifica_stato, azioni_correttive
from infrastruttura.database import insert_misurazione, insert_stato_sensore
from infrastruttura.logger import log_misurazione, log_azione


class SimulatorePesci:
    def __init__(self, config):
        self.config = config
        self.stato_attuale = {}  # (vasca_id, tipo) -> valore

    def genera_valore(self, vasca_id, tipo):
        chiave = (vasca_id, tipo)
        cfg = self.config[tipo]
        precedente = self.stato_attuale.get(chiave, cfg["mu"])
        nuovo = precedente + random.gauss(0, cfg["sigma"] / 2)

        # 5% di possibilità di disturbo improvviso
        if random.random() < 0.05:
            nuovo += random.uniform(-1.5, 1.5)

        # Limita valore nei limiti hard critici + margine
        low, high = cfg["critical"]
        nuovo = max(min(nuovo, high + 0.5), low - 0.5)
        nuovo = round(nuovo, 2)
        self.stato_attuale[chiave] = nuovo
        return nuovo

def analizza_sensore_pesce(vasca_id, sensore_id, tipo, simulatore):
    """
    Simula una lettura da un sensore pescina, valuta, logga e salva.
    """
    valore = simulatore.genera_valore(vasca_id, tipo)
    stato = classifica_stato(tipo, valore)
    timestamp = datetime.now().isoformat()

    insert_misurazione(vasca_id, sensore_id, tipo, valore, timestamp)
    log_misurazione(vasca_id, sensore_id, tipo, valore, stato)

    if stato != "OK":
        azioni = azioni_correttive(tipo, stato)
        azioni_str = "; ".join(azioni)
        insert_stato_sensore(vasca_id, sensore_id, tipo, stato, azioni_str, timestamp)
        log_azione(stato, azioni)