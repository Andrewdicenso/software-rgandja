import streamlit as st
import sys
import os

# Aggiunge la cartella src al percorso per importare i tuoi moduli
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from logger_enterprise import get_logger
from outbox_init import create_outbox_table
from outbox_worker import process_pending_events

st.set_page_config(page_title="Software RGandja", page_icon="🛡️", layout="centered")

st.title("🛡️ SOFTWARE RGANDJA")
st.subheader("Event-Driven Enterprise Architecture")

st.markdown("""
Questa è la vetrina ufficiale del sistema. Qui sotto puoi verificare lo stato dell'infrastruttura Outbox e dei worker di sistema.
""")

if st.button("🚀 Inizializza Tabelle Outbox"):
    try:
        create_outbox_table()
        st.success("Tabella Outbox inizializzata con successo nel database!")
    except Exception as e:
        st.error(f"Errore durante l'inizializzazione: {e}")

if st.button("⚙️ Esegui Worker Eventi Pendenti"):
    try:
        processed = process_pending_events()
        st.info(f"Ciclo completato. Eventi elaborati: {processed}")
    except Exception as e:
        st.error(f"Errore nell'esecuzione del worker: {e}")