# dashboard/utils/grafici.py

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from config.config import SENSOR_CONFIG, PANNELLO_CONFIG

TUTTE_LE_CONFIG_SENSORI = {**SENSOR_CONFIG, **PANNELLO_CONFIG}

def crea_grafico_vuoto(messaggio="Nessun dato disponibile"):
    fig = go.Figure()
    fig.update_layout(template="plotly_white", height=400, xaxis={"visible": False}, yaxis={"visible": False}, annotations=[{"text": messaggio, "xref": "paper", "yref": "paper", "showarrow": False, "font": {"size": 16}}])
    return fig

def linea_temporale_sensori(df, nome_grafico, range_x=None):
    if df.empty: return crea_grafico_vuoto(f"Nessun dato per '{nome_grafico}'")
    hovertemplate = "<b>Sorgente:</b> %{customdata[0]}<br><b>Valore:</b> %{y:.2f}<br><b>Stato:</b> %{customdata[1]}<br><b>Orario:</b> %{x|%Y-%m-%d %H:%M:%S}<extra></extra>"
    fig = px.line(df, x="timestamp", y="valore", color="sorgente_id", markers=True, title=f"Andamento Storico - {nome_grafico}", labels={"timestamp": "Data", "valore": "Valore", "sorgente_id": "Sorgente"}, custom_data=['sorgente_id', 'stato'])
    fig.update_traces(hovertemplate=hovertemplate)
    
    config = TUTTE_LE_CONFIG_SENSORI.get(nome_grafico)
    if config:
        ok_min, ok_max = config['ok']; warn_min, warn_max = config['warning']
        fig.add_hrect(y0=ok_min, y1=ok_max, fillcolor="green", opacity=0.1, line_width=0, layer="below", annotation_text="OK", annotation_position="top left", annotation_font_size=10)
        fig.add_hrect(y0=warn_min, y1=ok_min, fillcolor="yellow", opacity=0.1, line_width=0, layer="below", annotation_text="WARNING", annotation_position="bottom left", annotation_font_size=10)
        fig.add_hrect(y0=ok_max, y1=warn_max, fillcolor="yellow", opacity=0.1, line_width=0, layer="below")
    
    fig.update_layout(template="plotly_white", height=400, margin=dict(t=50, b=20, l=20, r=20), legend_title_text='Sorgenti')
    if range_x: fig.update_layout(xaxis_range=range_x)
    return fig

def subplot_per_sorgente(df, sorgente_id, range_x=None):
    if df.empty: return crea_grafico_vuoto(f"Nessun dato per '{sorgente_id}'")
    tipi = df['tipo'].unique()
    if len(tipi) == 0: return crea_grafico_vuoto(f"Nessun dato per '{sorgente_id}'")
    fig = make_subplots(rows=len(tipi), cols=1, subplot_titles=tipi, shared_xaxes=True)
    hovertemplate = "<b>Tipo:</b> %{customdata[0]}<br><b>Valore:</b> %{y:.2f}<br><b>Stato:</b> %{customdata[1]}<br><b>Orario:</b> %{x|%Y-%m-%d %H:%M:%S}<extra></extra>"
    
    for i, tipo in enumerate(tipi):
        df_sensore = df[df['tipo'] == tipo]
        fig.add_trace(go.Scatter(x=df_sensore['timestamp'], y=df_sensore['valore'], mode='lines+markers', name=tipo, customdata=df_sensore[['tipo', 'stato']], hovertemplate=hovertemplate), row=i + 1, col=1)
        config = TUTTE_LE_CONFIG_SENSORI.get(tipo)
        if config:
            ok_min, ok_max = config['ok']; warn_min, warn_max = config['warning']
            fig.add_hrect(y0=ok_min, y1=ok_max, fillcolor="green", opacity=0.1, line_width=0, row=i+1, col=1, layer="below")
            fig.add_hrect(y0=warn_min, y1=ok_min, fillcolor="yellow", opacity=0.1, line_width=0, row=i+1, col=1, layer="below")
            fig.add_hrect(y0=ok_max, y1=warn_max, fillcolor="yellow", opacity=0.1, line_width=0, row=i+1, col=1, layer="below")
            
    fig.update_layout(title_text=f"Parametri per {sorgente_id}", height=300 * len(tipi), showlegend=False, template="plotly_white")
    if range_x: fig.update_layout(xaxis_range=range_x)
    return fig

def grafico_produzione(df):
    if df.empty: return crea_grafico_vuoto("Nessun dato di produzione")
    fig = px.line(df, x="timestamp", y=["biomassa_pesci_kg", "raccolto_pronto_kg"], title="Andamento Produzione Fisica", labels={"timestamp": "Data", "value": "Peso (kg)", "variable": "Tipo Produzione"})
    fig.update_layout(template="plotly_white", height=400)
    return fig

def grafico_finanziario(df):
    if df.empty: return crea_grafico_vuoto("Nessun dato finanziario")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['ricavi'], name='Ricavi', marker_color='green'))
    fig.add_trace(go.Bar(x=df['timestamp'], y=df['costi'], name='Costi', marker_color='red'))
    fig.add_trace(go.Scatter(x=df['timestamp'], y=df['profitto_cumulativo'], name='Profitto Cumulativo', mode='lines+markers', line=dict(color='blue', width=3), yaxis='y2'))
    fig.update_layout(barmode='group', title_text='Analisi Finanziaria', template='plotly_white', yaxis=dict(title='Importo (€)'), yaxis2=dict(title='Profitto Cumulativo (€)', overlaying='y', side='right'), legend=dict(x=0, y=1.1, orientation='h'))
    return fig