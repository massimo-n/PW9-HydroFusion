# simulazione/launcher.py

import subprocess
import threading
import time
import sys
import os

def avvia_modulo(nome, modulo):
    print(f"🟢 Avvio {nome} ({modulo})")
    subprocess.Popen([sys.executable, "-m", modulo], cwd=ROOT)

# Root assoluta del progetto
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if __name__ == "__main__":
    print("🎛️ Avvio integrato HydroFusion: Simulazione + Dashboard\n")

    threading.Thread(
        target=avvia_modulo,
        args=("Simulazione Sensori", "simulazione.main"),
        daemon=True
    ).start()

    time.sleep(2)

    threading.Thread(
        target=avvia_modulo,
        args=("Dashboard", "dashboard.app"),
        daemon=True
    ).start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n⛔ Interruzione avvio integrato.")