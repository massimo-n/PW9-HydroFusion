# config/config.py

SENSOR_CONFIG = {
    "pH": {"mu": 7.0, "sigma": 0.2, "ok": (6.5, 7.5), "warning": (6.0, 8.0)},
    "Temperatura": {"mu": 25.0, "sigma": 1.0, "ok": (22.0, 28.0), "warning": (20.0, 30.0)},
    "Umidità": {"mu": 60.0, "sigma": 5.0, "ok": (50.0, 70.0), "warning": (40.0, 80.0)},
    "Ossigeno": {"mu": 7.0, "sigma": 0.5, "ok": (5.5, 8.5), "warning": (4.0, 10.0)},
    "Ammoniaca": {"mu": 0.4, "sigma": 0.1, "ok": (0.0, 0.8), "warning": (0.0, 1.5)}
}

PANNELLO_CONFIG = {
    "Produzione": {"mu": 5.0, "sigma": 1.5, "ok": (2.5, 6.5), "warning": (0.0, 8.0)}
}

NUM_SERRE = 3
SENSORI_PER_SERRA = ["pH", "Temperatura", "Umidità"]
NUM_PESCINE = 2
SENSORI_PER_PESCI = ["Temperatura", "Ossigeno", "Ammoniaca", "pH"]
NUM_PANNELLI = 5

AZIONI_CORRETTIVE = {
    "pH": {"WARNING": ["Monitorare valore.", "Verificare soluzione nutritiva."], "CRITICAL": ["Correggere pH con agenti specifici.", "Cambiare l'acqua."]},
    "Temperatura": {"WARNING": ["Controllare ventilazione.", "Verificare termostato."], "CRITICAL": ["Attivare raffreddamento/riscaldamento.", "Isolare la serra."]},
    "Umidità": {"WARNING": ["Verificare irrigazione.", "Controllare condensa."], "CRITICAL": ["Attivare deumidificatore.", "Aggiungere nebulizzatori."]},
    "Ossigeno": {"WARNING": ["Controllare pompe.", "Monitorare piante/pesci."], "CRITICAL": ["Ripristinare pompa.", "Aggiungere ossigeno attivo."]},
    "Ammoniaca": {"WARNING": ["Controllare filtraggio.", "Ridurre alimentazione."], "CRITICAL": ["Sostituire parte dell'acqua.", "Controllare biofiltro."]},
    "Produzione": {"WARNING": ["Pulire i pannelli.", "Verificare ombreggiamenti."], "CRITICAL": ["Controllare inverter.", "Sostituire moduli."]}
}