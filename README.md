# HydroFusion AI - Simulatore Avanzato di Impianto Acquaponico

![Python](https://img.shields.io/badge/Python-3.13%2B-blue?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30-red?logo=streamlit&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

## 📖 Panoramica

HydroFusion AI è un sistema completo di simulazione e monitoraggio per impianti di **agricoltura sostenibile**, scritto interamente in Python. Il progetto integra tre ecosistemi interconnessi:

🌱 **Serre Idroponiche** - Coltivazione senza suolo con controllo precisione  
🐟 **Acquacoltura** - Allevamento ittico sostenibile  
☀️ **Energia Solare** - Pannelli fotovoltaici per autosufficienza energetica  

### Componenti Principali

1. **Backend di Simulazione**: Genera dati realistici con variazioni stagionali, anomalie e pattern di produzione
2. **Database SQLite**: Storicizzazione di misurazioni, allarmi e stati dei sensori
3. **Dashboard Streamlit**: Interfaccia web interattiva per monitoraggio in tempo reale
## 🌟 Caratteristiche Principali

### 🔬 Simulazione Avanzata
- **Generatori Sensoriali Intelligenti**: Dati realistici con distribuzioni gaussiane e fasi di anomalia
- **Variazioni Stagionali**: Adattamento automatico dei parametri in base al mese corrente
- **Pattern di Produzione**: Simulazione cicli produttivi per biomassa e raccolti

### 🗄️ Gestione Dati
- **Database SQLite**: Storage persistente per misurazioni, allarmi e stati
- **Classificazione Automatica**: Sistema di soglie (OK, WARNING, CRITICAL)
- **Logging Strutturato**: Tracciamento completo delle operazioni

### 📊 Dashboard Interattiva
- **Monitoraggio Real-time**: Visualizzazione dati sensori in tempo reale
- **Analisi Storiche**: Grafici temporali e trend analysis
- **Sistema di Allarmi**: Notifiche automatiche con azioni correttive
- **Performance KPI**: Metriche di produzione e efficienza energetica

### ⚙️ Architettura Modulare
- **Configurazione Centralizzata**: Soglie e parametri modificabili da file config
- **Separazione delle Responsabilità**: Moduli indipendenti per ogni componente
- **Estensibilità**: Facile aggiunta di nuovi sensori e simulatori
## 🛠️ Stack Tecnologico

| Componente      | Tecnologia     | Descrizione |
|-----------------|--------------- |------------------------------------------|
| **Backend**     | Python 3.13    | Motore di simulazione e logica business  |
| **Database**    | SQLite 3       | Database embedded per persistenza dati   |
| **Frontend**    | Streamlit      | Framework per dashboard web interattiva  |
| **Simulazione** | Random/NumPy   | Generazione dati scientifici realistici  |
| **Logging**     | Python Logging | Sistema di tracciamento strutturato      |
| **Config**      | Python Modules | Configurazione centralizzata del sistema |

### Sensori Monitorati

| Tipo Sensore           | Range Normale | Soglie Critiche | Unità di Misura |
|------------------------|---------------|-----------------|-----------------|
| **pH**                 | 6.8 - 7.6     | < 6.0 o > 8.0   | pH              |
| **Temperatura**        | 20°C - 25°C   | < 15°C o > 30°C | °C              |
| **Ossigeno Disciolto** | 5.0 - 7.0     | < 4.0 o > 8.5   | mg/L            |
| **Ammoniaca**          | 0.1 - 0.5     | > 1.0           | mg/L            |
| **Produzione Energia** | 40 - 60       | < 20 o > 80     | kWh             |
## 🚀 Installazione e Avvio

### Prerequisiti
- **Python 3.13+** installato sul sistema
- **Git** per clonare il repository
- **Ambiente virtuale** (raccomandato)

### 1. 📥 Clona il Repository
```bash
git clone https://github.com/massimo-n/PW9-HydroFusion.git
cd HydroFusion-AI
```

### 2. 🔧 Configura l'Ambiente Virtuale

**Windows:**
```powershell
python -m venv hydrofusion-env
.\hydrofusion-env\Scripts\Activate.ps1
```

**macOS/Linux:**
```bash
python3 -m venv hydrofusion-env
source hydrofusion-env/bin/activate
```

### 3. 📦 Installa le Dipendenze
```bash
pip install -r requirements.txt
```

### 4. ▶️ Avvia il Sistema

**Opzione A - Simulazione + Dashboard:**
```bash
python simulazione/launcher.py
```

**Opzione B - Solo Simulazione:**
```bash
python simulazione/main.py
```

**Opzione C - Solo Dashboard:**
```bash
streamlit run dashboard/app.py
```

### 5. 🌐 Accedi alla Dashboard
Apri il browser e naviga su: **http://localhost:8501**

> 💡 **Tip**: La simulazione genererà automaticamente il database `hydrofusion.db` al primo avvio

## 📂 Struttura del Progetto

```
HydroFusion AI/
├── 📁 config/                 # Configurazione del sistema
│   ├── config.py             #   Parametri sensori e soglie
│   ├── classificatore.py     #   Logica classificazione stati
│   └── __init__.py
│
├── 📁 infrastruttura/         # Servizi base
│   ├── database.py          #   Gestione SQLite thread-safe
│   └── logger.py            #   Sistema di logging
│
├── 📁 simulazione/           # Motore di simulazione
│   ├── main.py              #   Coordinatore principale
│   ├── launcher.py          #   Script di avvio sistema
│   ├── serre.py             #   Simulazione idroponica
│   ├── pesci.py             #   Simulazione acquacoltura
│   ├── pannelli.py          #   Simulazione fotovoltaico
│   └── generatori.py        #   Generatori dati base
│
├── 📁 dashboard/             # Frontend Streamlit
│   ├── app.py               #   Applicazione principale
│   ├── 📁 pages/            #   Pagine della dashboard
│   │   ├── home.py          #     Home e overview
│   │   ├── monitoraggio.py  #     Monitoraggio real-time
│   │   └── allarmi.py       #     Gestione allarmi
│   ├── 📁 utils/            #   Utilities condivise
│   │   ├── grafici.py       #     Generazione grafici
│   │   └── layout.py        #     Layout comuni
│   └── 📁 assets/           #   Risorse statiche
│       └── style.css        #     Styling personalizzato
│
├── 🗄️ hydrofusion.db        # Database SQLite (auto-generato)
├── 📋 requirements.txt       # Dipendenze Python
├── 📄 README.md             # Documentazione
└── 🔧 concatenate_project.py # Utility concatenazione codice
```

### 🎯 Responsabilità dei Moduli

| Modulo             | Responsabilità                      | File Chiave                           |
|--------------------|-------------------------------------|---------------------------------------|
| **Config**         | Parametri sistema, soglie sensori   | `config.py`, `classificatore.py`      |
| **Infrastruttura** | Database, logging, utilities        | `database.py`, `logger.py`            |
| **Simulazione**    | Generazione dati, simulatori        | `serre.py`, `pesci.py`, `pannelli.py` |
| **Dashboard**      | Interfaccia utente, visualizzazioni | `app.py`, `pages/`, `utils/`          |
## 📊 Dashboard Features

### 🏠 Home Page
- **Panoramica Sistema**: Stato generale di tutti i sensori
- **KPI Real-time**     : Metriche di performance istantanee
- **Alert Summary**     : Riepilogo allarmi attivi

### 📈 Monitoraggio
- **Grafici Temporali** : Visualizzazione dati storici
- **Filtri Avanzati**   : Per sensore, data range, stato
- **Export Dati**       : Download in formato CSV/Excel

### 🚨 Gestione Allarmi
- **Alert Dashboard**   : Tutti gli allarmi attivi e risolti
- **Azioni Correttive** : Suggerimenti automatici per ogni anomalia
- **Storico Interventi**: Log completo delle azioni intraprese

## 🧪 Esempi di Utilizzo

### Monitoraggio pH delle Serre
```python
# Esempio di verifica stato pH
ph_valore = 7.8
stato = classifica_stato("pH", ph_valore)
# Risultato: "WARNING" (soglia superata)
```

### Simulazione Produzione Energia
```python
# Variazione stagionale automatica
produzione_estate = genera_valore_pannello(mese=7)  # Luglio
produzione_inverno = genera_valore_pannello(mese=12)  # Dicembre
# Estate: ~72 kWh, Inverno: ~30 kWh
```

## 🔧 Configurazione Avanzata

### Modifica Soglie Sensori
Edita il file `config/config.py`:
```python
SENSOR_CONFIG = {
    "pH": {
        "normal": (6.8, 7.6),
        "critical": (6.0, 8.0),
        "mu": 7.2,
        "sigma": 0.2
    }
}
```

### Aggiunta Nuovi Sensori
1. Aggiungi configurazione in `config/config.py`
2. Implementa logica in `config/classificatore.py`
3. Crea simulatore in `simulazione/`
4. Aggiungi visualizzazione in `dashboard/`

## 🛣️ Roadmap Futura

- [ ] **Machine Learning**: Previsione anomalie con algoritmi ML
- [ ] **API REST**: Endpoint per integrazione sistemi esterni
- [ ] **Notifiche Push**: Alert via email/SMS per allarmi critici
- [ ] **Multi-tenant**: Supporto per più impianti in parallelo
- [ ] **Mobile App**: Companion app per monitoraggio mobile
- [ ] **Docker**: Containerizzazione per deployment cloud

## 📝 Licenza

Questo progetto è rilasciato sotto licenza **MIT**. Vedi il file `LICENSE` per i dettagli.

## 👨‍💻 Autore

**Razorback_it**
- 🐙 GitHub: [@massimo-n](https://github.com/massimo-n)

---

⭐ **Se questo progetto ti è stato utile, considera di lasciare una stella!** ⭐
