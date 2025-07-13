# simulazione/serre.py

import random
from datetime import datetime
from config.config import SENSOR_CONFIG
from config.classificatore import classifica_stato, azioni_correttive
from infrastruttura.database import insert_misurazione, insert_stato_sensore
from infrastruttura.logger import log_misurazione, log_azione


class GeneratoreSensoriale:
    def __init__(self, tipo, normale_range, sballo_range, soglia_inizio=10, soglia_fine=5, prob_inizio=0.2):
        self.tipo = tipo
        self.normale_range = normale_range
        self.sballo_range = sballo_range
        self.fase = "normale"
        self.contatore = 0
        self.soglia_inizio = soglia_inizio
        self.soglia_fine = soglia_fine
        self.prob_inizio = prob_inizio

    def genera(self, precedente):
        if self.fase == "normale":
            valore = random.gauss(*self.normale_range)
            self.contatore += 1
            if self.contatore > self.soglia_inizio and random.random() < self.prob_inizio:
                self.fase = "sballo"
                self.contatore = 0
        else:
            valore = precedente + random.uniform(*self.sballo_range)
            self.contatore += 1
            if self.contatore > self.soglia_fine and random.random() < 0.5:
                self.fase = "normale"
                self.contatore = 0
        return valore


class SimulatoreSerra:
    def __init__(self, config):
        self.config = config
        self.stato_attuale = {}  # (serra_id, tipo) -> valore

        self.generatori = {
            "pH": GeneratoreSensoriale("pH", (7.2, 0.2), (-2.0, 3.0)),
            "Temperatura": GeneratoreSensoriale("Temperatura", (22, 1.0), (-4.0, 6.0)),
            "Ossigeno": GeneratoreSensoriale("Ossigeno", (6.0, 0.5), (-2.0, 2.5)),
            "Ammoniaca": GeneratoreSensoriale("Ammoniaca", (0.3, 0.1), (0.5, 1.5)),
            "Produzione": GeneratoreSensoriale("Produzione", (50, 5.0), (-15.0, 30.0))
        }

    def variazione_stagionale(self, tipo, base_mu):
        mese = datetime.now().month
        if tipo == "Temperatura":
            if mese in [12, 1, 2]:
                return base_mu - 4
            elif mese in [6, 7, 8]:
                return base_mu + 3
        elif tipo == "Ossigeno":
            if mese in [6, 7, 8]:
                return base_mu - 0.5
        elif tipo == "Produzione":
            if mese in [11, 12, 1]:
                return base_mu * 0.6
            elif mese in [6, 7, 8]:
                return base_mu * 1.2
        return base_mu

    def genera_valore(self, serra_id, tipo):
        cfg = self.config[tipo]
        base_mu = self.variazione_stagionale(tipo, cfg["mu"])
        sigma = cfg["sigma"]

        key = (serra_id, tipo)
        precedente = self.stato_attuale.get(key, base_mu)

        generatore = self.generatori.get(tipo)
        if generatore:
            valore = generatore.genera(precedente)
        else:
            valore = precedente + random.gauss(0, sigma / 3)
            if random.random() < 0.03:
                valore += random.uniform(-3.0, 3.0)

        low, high = cfg["critical"]
        valore = max(min(valore, high + 2), low - 2)
        valore = round(valore, 2)
        self.stato_attuale[key] = valore
        return valore

    def get_fasi_attive(self):
        fasi = {}
        for (serra_id, tipo), _ in self.stato_attuale.items():
            gen = self.generatori.get(tipo)
            if gen:
                fasi[(serra_id, tipo)] = gen.fase
        return fasi


def analizza_sensore(serra_id, sensore_id, tipo, simulatore):
    valore = simulatore.genera_valore(serra_id, tipo)
    stato = classifica_stato(tipo, valore)
    timestamp = datetime.now().isoformat()

    insert_misurazione(serra_id, sensore_id, tipo, valore, timestamp)
    log_misurazione(serra_id, sensore_id, tipo, valore, stato)

    if stato != "OK":
        azioni = azioni_correttive(tipo, stato)
        azioni_str = "; ".join(azioni)
        insert_stato_sensore(serra_id, sensore_id, tipo, stato, azioni_str, timestamp)
        log_azione(stato, azioni)