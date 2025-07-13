# infrastruttura/logger.py

import logging
import threading
from datetime import datetime

_header_lock = threading.Lock()
_header_printed = False

class TabularFormatter(logging.Formatter):
    def format(self, record):
        log_data = record.msg
        if isinstance(log_data, dict) and "sorgente_id" in log_data:
            valore_str = f"{log_data.get('valore', 0.0):.2f}"
            stato_str = log_data.get('stato', 'N/D')
            return f"| {log_data.get('timestamp', ''):<19} | {log_data.get('sorgente_id', ''):<15} | {log_data.get('tipo', ''):<15} | {valore_str:<10} | {stato_str:<10} |"
        else:
            return f"[SYSTEM] {log_data}"

def print_header():
    header = f"| {'Timestamp':<19} | {'Sorgente ID':<15} | {'Tipo Sensore':<15} | {'Valore':<10} | {'Stato':<10} |"
    separator = "-" * len(header)
    print(separator); print(header); print(separator)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    if logger.hasHandlers(): logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(TabularFormatter())
    logger.addHandler(handler)

def log_misurazione(sorgente_id, tipo, valore, stato):
    global _header_printed
    with _header_lock:
        if not _header_printed:
            print_header()
            _header_printed = True
    logging.info({"timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "sorgente_id": sorgente_id, "tipo": tipo, "valore": valore, "stato": stato})

def log_system_message(message):
    logging.info(message)