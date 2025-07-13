# config/classificatore.py

import json
from config.config import SENSOR_CONFIG, PANNELLO_CONFIG, AZIONI_CORRETTIVE

TUTTE_LE_CONFIG_SENSORI = {**SENSOR_CONFIG, **PANNELLO_CONFIG}

def classifica_stato(tipo, valore):
    soglie = TUTTE_LE_CONFIG_SENSORI.get(tipo)
    if not soglie: return "UNKNOWN"
    ok_min, ok_max = soglie["ok"]
    warning_min, warning_max = soglie["warning"]
    if ok_min <= valore <= ok_max: return "OK"
    elif warning_min <= valore <= warning_max: return "WARNING"
    else: return "CRITICAL"

def get_azioni_correttive(tipo, stato):
    return AZIONI_CORRETTIVE.get(tipo, {}).get(stato, [])

def azioni_correttive_to_json(tipo, stato):
    return json.dumps(get_azioni_correttive(tipo, stato))