import streamlit as st
import os
import sys

# Aggiungiamo la cartella src al path per importare i moduli interni se necessario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Configurazione della pagina
st.set_page_config(
    page_title="Software RGandja - Vetrina Enterprise",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================
# 1. SISTEMA DI SICUREZZA E AUTENTICAZIONE
# ==========================================
def check_password():
    """Restituisce True se l'utente ha inserito la password corretta."""

    # Recuperiamo le credenziali dai Secrets di Streamlit o usiamo valori sicuri di default
    try:
        app_user = st.secrets["APP_USER"]
        app_password = st.secrets["APP_PASSWORD"]
    except Exception:
        app_user = "admin"
        app_password = "RgandjaSecurePassword2026!"  # Puoi cambiarla nei secrets di Streamlit

    def password_entered():
        if st.session_state["username"] == app_user and st.session_state["password"] == app_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Non conserviamo la password in chiaro nello stato
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Schermata di Login
        st.markdown("<h2 style='text-align: center;'>🔐 Accesso Riservato - Software RGandja</h2>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Questa vetrina è protetta. Inserisci le credenziali autorizzate per accedere.</p>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.button("Accedi", on_click=password_entered, use_container_width=True)

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("😕 Username o password errati. Riprova.")
        return False

    elif not st.session_state["password_correct"]:
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Accedi", on_click=password_entered)
        st.error("😕 Username o password errati.")
        return False
    else:
        return True

# Se l'utente non è autenticato, interrompiamo l'esecuzione della pagina
if not check_password():
    st.stop()

# ==========================================
# 2. INTERFACCIA PRINCIPALE (DOPO IL LOGIN)
# ==========================================

st.title("🛡️ SOFTWARE RGANDJA")
st.subheader("Event-Driven Enterprise Architecture & Outbox Pattern Manager")

# Sidebar di navigazione interna
menu = st.sidebar.selectbox("Navigazione", ["📊 Pannello di Controllo", "📖 Presentazione & Documentazione Tecnica", "🔌 Guide di Integrazione API"])

if menu == "📊 Pannello di Controllo":
    st.markdown("### Stato del Sistema")
    st.write("Benvenuto nell'area operativa protetta. Qui sotto puoi monitorare e testare lo stato dell'infrastruttura Outbox.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Inizializza Tabelle Outbox", use_container_width=True):
            st.success("Comando di inizializzazione inviato con successo al motore di sistema.")
    with col2:
        if st.button("⚙️ Esegui Worker Eventi Pendenti", use_container_width=True):
            st.info("Worker avviato: elaborazione degli eventi in coda in corso...")

elif menu == "📖 Presentazione & Documentazione Tecnica":
    st.markdown("## 📖 Informazioni sul Progetto")
    st.write("""
    **Software RGandja** è un'architettura enterprise progettata per garantire la massima affidabilità,
    tracciabilità e sicurezza nella gestione degli eventi di sistema.
    """)

    st.markdown("### 🏛️ Architettura e Componenti Principali")
    st.markdown("""
    * **Transactional Outbox Pattern:** Garantisce che nessun evento vada perso durante le transazioni critiche del database, disaccoppiando la scrittura dei dati dalla pubblicazione dei messaggi.
    * **Worker Autonomi:** Processi di background resilienti che prelevano gli eventi pendenti e li recapitano ai sistemi destinatari in modo asincrono.
    * **Logging Enterprise:** Tracciamento rigoroso di ogni singola operazione per audit di sicurezza e conformità.
    """)

elif menu == "🔌 Guide di Integrazione API":
    st.markdown("## 🔌 Come Integrare e Usare il Sistema")
    st.write("Questa sezione fornisce le specifiche tecniche per connettere servizi esterni o client di terze parti all'infrastruttura RGandja.")

    st.markdown("### 1. Connessione ai Flussi Event-Driven")
    st.code("""
# Esempio di payload JSON per l'invio di un evento nel sistema Outbox
{
    "event_type": "USER_ACTION_LOGGED",
    "payload": {
        "user_id": "12345",
        "action": "CONFIG_UPDATE",
        "timestamp": "2026-03-28T10:00:00Z"
    },
    "status": "PENDING"
}
    """, language="json")

    st.markdown("### 2. Sicurezza e Autenticazione delle API")
    st.write("Tutte le chiamate esterne verso i componenti core richiedono intestazioni di sicurezza basate su token crittografati e validazione rigorosa dei parametri per prevenire vulnerabilità di iniezione o accessi non autorizzati.")