# dashboard/utils/grafici.py
"""
Modulo per la generazione di grafici Plotly per la dashboard HydroFusion AI.

Contiene funzioni per creare visualizzazioni interattive dei dati dei sensori,
inclusi grafici temporali, subplot per sorgente e analisi di produzione/finanziarie.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config.config import SENSOR_CONFIG, PANNELLO_CONFIG

# Configurazione unificata di tutti i sensori
TUTTE_LE_CONFIG_SENSORI = {**SENSOR_CONFIG, **PANNELLO_CONFIG}

def crea_grafico_vuoto(messaggio="Nessun dato disponibile"):
    """
    Crea un grafico Plotly vuoto con un messaggio personalizzato.
    
    Args:
        messaggio (str): Messaggio da visualizzare nel grafico vuoto
        
    Returns:
        plotly.graph_objects.Figure: Grafico vuoto formattato
    """
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white",
        height=400,
        xaxis={"visible": False},
        yaxis={"visible": False},
        annotations=[{
            "text": messaggio,
            "xref": "paper",
            "yref": "paper",
            "showarrow": False,
            "font": {"size": 16}
        }]
    )
    return fig

def linea_temporale_sensori(df, nome_grafico, range_x=None):
    """
    Crea un grafico a linee temporali per i dati dei sensori.
    
    Args:
        df (pandas.DataFrame): DataFrame con colonne timestamp, valore, sorgente_id, stato
        nome_grafico (str): Nome del tipo di sensore da visualizzare
        range_x (tuple, optional): Range temporale per l'asse X
        
    Returns:
        plotly.graph_objects.Figure: Grafico temporale con bande di soglia colorate
    """
    if df.empty:
        return crea_grafico_vuoto(f"Nessun dato per '{nome_grafico}'")
    
    # Recupera configurazione e unità di misura del sensore
    config = TUTTE_LE_CONFIG_SENSORI.get(nome_grafico, {})
    unita = config.get("unita", "")
    yaxis_title = f"{nome_grafico} ({unita})" if unita else nome_grafico

    # Template per hover personalizzato
    hovertemplate = (
        f"<b>Sorgente:</b> %{{customdata[0]}}<br>"
        f"<b>Valore:</b> %{{y:.2f}} {unita}<br>"
        f"<b>Stato:</b> %{{customdata[1]}}<br>"
        f"<b>Orario:</b> %{{x|%Y-%m-%d %H:%M:%S}}<extra></extra>"
    )
    
    # Creazione grafico principale
    fig = px.line(
        df, 
        x="timestamp", 
        y="valore", 
        color="sorgente_id", 
        markers=True, 
        title=f"Andamento Storico - {nome_grafico}", 
        labels={
            "timestamp": "Orario", 
            "valore": yaxis_title, 
            "sorgente_id": "Sorgente"
        },
        custom_data=['sorgente_id', 'stato']
    )
    
    fig.update_traces(hovertemplate=hovertemplate)
    
    # Aggiunta bande di soglia se configurazione disponibile
    if config:
        ok_min, ok_max = config['ok']
        warn_min, warn_max = config['warning']
        
        # Banda verde per valori OK
        fig.add_hrect(
            y0=ok_min, y1=ok_max, 
            fillcolor="green", opacity=0.1, line_width=0, 
            layer="below", 
            annotation_text="OK", 
            annotation_position="top left", 
            annotation_font_size=10
        )
        
        # Bande gialle per WARNING
        fig.add_hrect(
            y0=warn_min, y1=ok_min, 
            fillcolor="yellow", opacity=0.1, line_width=0, 
            layer="below", 
            annotation_text="WARNING", 
            annotation_position="bottom left", 
            annotation_font_size=10
        )
        fig.add_hrect(
            y0=ok_max, y1=warn_max, 
            fillcolor="yellow", opacity=0.1, line_width=0, 
            layer="below"
        )
    
    # Layout finale
    fig.update_layout(
        template="plotly_white", 
        height=400, 
        margin=dict(t=50, b=20, l=20, r=20), 
        legend_title_text='Sorgenti'
    )
    
    if range_x:
        fig.update_layout(xaxis_range=range_x)
        
    return fig

def subplot_per_sorgente(df, sorgente_id, range_x=None):
    """
    Crea subplot multipli per visualizzare tutti i sensori di una specifica sorgente.
    
    Args:
        df (pandas.DataFrame): DataFrame filtrato per una sorgente specifica
        sorgente_id (str): ID della sorgente (es. "Serra_1", "Pesci_2")
        range_x (tuple, optional): Range temporale per l'asse X
        
    Returns:
        plotly.graph_objects.Figure: Figura con subplot per ogni tipo di sensore
    """
    if df.empty:
        return crea_grafico_vuoto(f"Nessun dato per '{sorgente_id}'")
    
    tipi = sorted(df['tipo'].unique())
    if len(tipi) == 0:
        return crea_grafico_vuoto(f"Nessun dato per '{sorgente_id}'")
    
    # Prepara titoli subplot con unità di misura
    subplot_titles = []
    for tipo in tipi:
        unita = TUTTE_LE_CONFIG_SENSORI.get(tipo, {}).get("unita", "")
        subplot_titles.append(f"{tipo} ({unita})")

    # Crea subplot con assi X condivisi per zoom sincronizzato
    fig = make_subplots(
        rows=len(tipi), 
        cols=1, 
        subplot_titles=subplot_titles, 
        shared_xaxes=True
    )
    
    # Aggiungi trace per ogni tipo di sensore
    for i, tipo in enumerate(tipi):
        df_sensore = df[df['tipo'] == tipo]
        config = TUTTE_LE_CONFIG_SENSORI.get(tipo, {})
        unita = config.get("unita", "")
        
        # Hover template personalizzato
        hovertemplate = (
            f"<b>Valore:</b> %{{y:.2f}} {unita}<br>"
            f"<b>Stato:</b> %{{customdata[0]}}<br>"
            f"<b>Orario:</b> %{{x|%Y-%m-%d %H:%M:%S}}<extra></extra>"
        )
        
        # Aggiungi trace del sensore
        fig.add_trace(
            go.Scatter(
                x=df_sensore['timestamp'], 
                y=df_sensore['valore'], 
                mode='lines+markers', 
                name=tipo, 
                customdata=df_sensore[['stato']], 
                hovertemplate=hovertemplate
            ), 
            row=i + 1, 
            col=1
        )
        
        # Aggiorna etichette asse Y
        fig.update_yaxes(title_text="Valore", row=i + 1, col=1)

        # Aggiungi bande di soglia se configurazione disponibile
        if config:
            ok_min, ok_max = config['ok']
            warn_min, warn_max = config['warning']
            
            # Banda verde (OK)
            fig.add_hrect(
                y0=ok_min, y1=ok_max, 
                fillcolor="green", opacity=0.1, line_width=0, 
                row=i+1, col=1, layer="below"
            )
            
            # Bande gialle (WARNING)
            fig.add_hrect(
                y0=warn_min, y1=ok_min, 
                fillcolor="yellow", opacity=0.1, line_width=0, 
                row=i+1, col=1, layer="below"
            )
            fig.add_hrect(
                y0=ok_max, y1=warn_max, 
                fillcolor="yellow", opacity=0.1, line_width=0, 
                row=i+1, col=1, layer="below"
            )
            
    # Layout generale
    fig.update_layout(
        title_text=f"Parametri per {sorgente_id}", 
        height=300 * len(tipi), 
        showlegend=False, 
        template="plotly_white"
    )
    
    # Configura assi X con etichette visibili
    for i in range(1, len(tipi) + 1):
        title = "Orario" if i == len(tipi) else ""
        fig.update_xaxes(
            showticklabels=True,  # Forza visualizzazione etichette
            title_text=title,     # Titolo solo sull'ultimo asse
            row=i, 
            col=1
        )
        
    if range_x:
        fig.update_layout(xaxis_range=range_x)
        
    return fig
def grafico_produzione(df):
    """
    Crea un grafico per l'andamento della produzione fisica (biomassa e raccolti).
    
    Args:
        df (pandas.DataFrame): DataFrame con dati di produzione
        
    Returns:
        plotly.graph_objects.Figure: Grafico lineare della produzione
    """
    if df.empty:
        return crea_grafico_vuoto("Nessun dato di produzione")
    
    fig = px.line(
        df, 
        x="timestamp", 
        y=["biomassa_pesci_kg", "raccolto_pronto_kg"], 
        title="Andamento Produzione Fisica", 
        labels={
            "timestamp": "Data", 
            "value": "Peso (kg)", 
            "variable": "Tipo Produzione"
        }
    )
    
    fig.update_layout(template="plotly_white", height=400)
    return fig


def grafico_finanziario(df):
    """
    Crea un grafico combinato per l'analisi finanziaria con ricavi, costi e profitto.
    
    Args:
        df (pandas.DataFrame): DataFrame con dati finanziari
        
    Returns:
        plotly.graph_objects.Figure: Grafico combinato bar + line per analisi finanziaria
    """
    if df.empty:
        return crea_grafico_vuoto("Nessun dato finanziario")
    
    fig = go.Figure()
    
    # Barre per ricavi e costi
    fig.add_trace(
        go.Bar(
            x=df['timestamp'], 
            y=df['ricavi'], 
            name='Ricavi', 
            marker_color='green'
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=df['timestamp'], 
            y=df['costi'], 
            name='Costi', 
            marker_color='red'
        )
    )
    
    # Linea per profitto cumulativo (asse Y secondario)
    fig.add_trace(
        go.Scatter(
            x=df['timestamp'], 
            y=df['profitto_cumulativo'], 
            name='Profitto Cumulativo', 
            mode='lines+markers', 
            line=dict(color='blue', width=3), 
            yaxis='y2'
        )
    )
    
    # Layout con doppio asse Y
    fig.update_layout(
        barmode='group', 
        title_text='Analisi Finanziaria', 
        template='plotly_white',
        yaxis=dict(title='Importo (€)'), 
        yaxis2=dict(
            title='Profitto Cumulativo (€)', 
            overlaying='y', 
            side='right'
        ), 
        legend=dict(x=0, y=1.1, orientation='h')
    )
    
    return fig