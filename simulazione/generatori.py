# simulazione/generatori.py

import random
import numpy as np
from config.config import SENSOR_CONFIG, PANNELLO_CONFIG

CONFIGURAZIONI = {**SENSOR_CONFIG, **PANNELLO_CONFIG}

class GeneratoreSensore:
    def __init__(self, tipo_sensore, inerzia=0.95, prob_anomalia=0.02, durata_media_anomalia=5):
        if tipo_sensore not in CONFIGURAZIONI: raise ValueError(f"Tipo sensore '{tipo_sensore}' non trovato.")
        self.tipo, self.config = tipo_sensore, CONFIGURAZIONI[tipo_sensore]
        self.mu, self.sigma = self.config['mu'], self.config['sigma']
        self.valore_attuale, self.inerzia = self.mu, inerzia
        warn_min, warn_max = self.config['warning']
        self.limite_minimo, self.limite_massimo = warn_min - (self.sigma * 2), warn_max + (self.sigma * 2)
        self.fase, self.contatore_fase, self.durata_anomalia_corrente = "normale", 0, 0
        self.prob_anomalia, self.durata_media_anomalia = prob_anomalia, durata_media_anomalia

    def genera(self):
        if self.fase == "normale":
            if random.random() < self.prob_anomalia:
                self.fase, self.contatore_fase = "anomalia", 0
                self.durata_anomalia_corrente = max(1, int(random.gauss(self.durata_media_anomalia, 1)))
        elif self.contatore_fase >= self.durata_anomalia_corrente:
            self.fase, self.contatore_fase = "normale", 0
        self.contatore_fase += 1 if self.fase == "anomalia" else 0

        target_mu = self.mu
        if self.fase == "anomalia":
            ok_min, ok_max = self.config['ok']
            target_mu = ok_max + self.sigma if random.choice([True, False]) else ok_min - self.sigma
        
        fluttuazione = np.random.normal(loc=target_mu, scale=self.sigma)
        nuovo_valore = (self.valore_attuale * self.inerzia) + (fluttuazione * (1 - self.inerzia))
        self.valore_attuale = np.clip(nuovo_valore, self.limite_minimo, self.limite_massimo)
        return round(self.valore_attuale, 2)