import streamlit as st
import os
import sys
import json
import pandas as pd

# Aggiungiamo la cartella src al path per importare i moduli interni se necessario
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

# Configurazione della pagina
st.set_page_config(
    page_title="Software RGandja - Vetrina Enterprise",
    page_icon="🛡️",
    layout="wide"
)

# ==========================================
# CONNESSIONE AL DATABASE NEON
# ==========================================
db_url = st.secrets.get("url", st.secrets.get("postgres", {}).get("url"))

# ==========================================
# 1. SISTEMA DI SICUREZZA E AUTENTICAZIONE
# ==========================================
def check_password():
    """Restituisce True se l'utente ha inserito la password corretta."""

    try:
        app_user = st.secrets["APP_USER"]
        app_password = st.secrets["APP_PASSWORD"]
    except Exception:
        app_user = "admin"
        app_password = "RgandjaSecurePassword2026!"

    def password_entered():
        if st.session_state["username"] == app_user and st.session_state["password"] == app_password:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
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

if not check_password():
    st.stop()

# ==========================================
# 2. INTERFACCIA PRINCIPALE (DOPO IL LOGIN)
# ==========================================

st.title("🛡️ SOFTWARE RGANDJA")
st.subheader("Event-Driven Enterprise Architecture & Resilient Outbox Manager")

# Sidebar di navigazione interna
menu = st.sidebar.selectbox("Navigazione", ["📊 Pannello di Controllo", "📖 Presentazione & Documentazione Tecnica", "🔌 Guide di Integrazione API"])

if menu == "📊 Pannello di Controllo":
    st.markdown("### Stato del Sistema e Gestione Coda Resiliente")
    st.write("Area operativa avanzata con gestione dei tentativi (Retry) e isolamento degli errori (Dead Letter Queue).")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Inizializza / Aggiorna Tabelle Outbox (Con Retry & DLQ)", use_container_width=True):
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                # Schema avanzato con retry_count per la gestione della resilienza
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS outbox_events (
                        id SERIAL PRIMARY KEY,
                        event_type VARCHAR(255) NOT NULL,
                        payload JSONB NOT NULL,
                        status VARCHAR(50) DEFAULT 'PENDING',
                        retry_count INT DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                cur.close()
                conn.close()
                st.success("Tabelle Outbox aggiornate con supporto a Retry e Dead Letter Queue su Neon!")
            except Exception as e:
                st.error(f"Errore di connessione o inizializzazione: {e}")

        if st.button("📥 Inserisci Evento di Test Normale (PENDING)", use_container_width=True):
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                payload_test = json.dumps({"user_id": "test_user_999", "action": "SIMULATED_TRANSACTION"})
                cur.execute(
                    "INSERT INTO outbox_events (event_type, payload, status, retry_count) VALUES (%s, %s, %s, %s);",
                    ("TEST_EVENT", payload_test, "PENDING", 0)
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Evento di test regolare inserito con successo.")
            except Exception as e:
                st.error(f"Errore durante l'inserimento dell'evento: {e}")

    with col2:
        if st.button("⚙️ Esegui Worker Resiliente (Con Gestione Fallimenti)", use_container_width=True):
            try:
                import psycopg2
                import random
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()

                # Seleziona gli eventi in stato PENDING
                cur.execute("SELECT id, event_type, payload, retry_count FROM outbox_events WHERE status = 'PENDING';")
                events = cur.fetchall()

                if not events:
                    st.info("Nessun evento pendente trovato nella coda Outbox.")
                else:
                    processed_count = 0
                    failed_count = 0
                    dlq_count = 0

                    for event in events:
                        event_id, event_type, payload, retry_count = event

                        # Simulazione di instabilità di rete o errore di elaborazione (es. 20% di probabilità di errore)
                        # Per testare la DLQ puoi forzare il fallimento simulato
                        simulated_failure = False # Metti True se vuoi testare il fallimento forzato

                        if simulated_failure:
                            new_retry = retry_count + 1
                            if new_retry >= 3:
                                # Spostato in Dead Letter Queue (DLQ) logica impostando lo stato a FAILED
                                cur.execute("UPDATE outbox_events SET status = 'FAILED', retry_count = %s WHERE id = %s;", (new_retry, event_id))
                                dlq_count += 1
                            else:
                                # Incrementa i tentativi lasciandolo in PENDING per il prossimo giro
                                cur.execute("UPDATE outbox_events SET retry_count = %s WHERE id = %s;", (new_retry, event_id))
                                failed_count += 1
                        else:
                            # Elaborazione riuscita con successo
                            cur.execute("UPDATE outbox_events SET status = 'PROCESSED', retry_count = %s WHERE id = %s;", (retry_count + 1, event_id))
                            processed_count += 1

                    conn.commit()
                    st.success(f"Worker completato: {processed_count} elaborati con successo, {failed_count} in retry, {dlq_count} inviati in Dead Letter Queue (FAILED).")

                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Errore durante l'esecuzione del worker resiliente: {e}")

    st.markdown("---")
    st.markdown("### 📋 Monitoraggio in Tempo Reale (Audit Log Avanzato)")

    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        query = "SELECT id, event_type, payload, status, retry_count, created_at FROM outbox_events ORDER BY id DESC LIMIT 20;"
        df_events = pd.read_sql(query, conn)
        conn.close()

        if df_events.empty:
            st.info("La tabella degli eventi è attualmente vuota. Inizializza le tabelle o inserisci un evento di test.")
        else:
            st.dataframe(df_events, use_container_width=True)
    except Exception:
        st.warning("Impossibile caricare la tabella di audit. Assicurati che le tabelle Outbox siano state aggiornate.")

elif menu == "📖 Presentazione & Documentazione Tecnica":
    st.markdown("## 📖 Informazioni sul Progetto e Specifiche Architetturali Avanzate")
    st.write("""
    **Software RGandja** implementa un pattern architetturale di livello industriale orientato alla tolleranza agli errori
    e alla garanzia di recapito dei messaggi nei sistemi distribuiti.
    """)

    st.markdown("### 🔄 Resilienza, Retry Pattern e Dead Letter Queue (DLQ)")
    st.markdown("""
    L'architettura supera il semplice Outbox Pattern introducendo politiche di protezione contro i malfunzionamenti esterni:
    1. **Transactional Outbox:** Scrittura atomica iniziale in stato `PENDING` legata alla transazione applicativa principale.
    2. **Tentativi Controllati (Retry Logic):** In caso di interruzione temporanea del servizio di destinazione, il worker incrementa il contatore `retry_count` senza perdere il contesto dell'operazione.
    3. **Isolamento della Dead Letter Queue (DLQ):** Superata la soglia critica dei tentativi falliti (es. 3 retry), l'evento viene marcato come `FAILED` (DLQ). Questo evita che un messaggio corrotto o un endpoint permanentemente offline blocchino indefinitamente l'intera coda di elaborazione asincrona, consentendo analisi forensi successive sui payload anomali.
    """)

elif menu == "🔌 Guide di Integrazione API":
    st.markdown("## 🔌 Come Integrare e Usare il Sistema")
    st.write("Questa sezione fornisce le specifiche tecniche per connettere servizi esterni o client di terze parti all'infrastruttura RGandja.")

    st.markdown("### 1. Connessione ai Flussi Event-Driven")
    st.code("""
# Esempio di payload JSON per l'invio di un evento nel sistema Outbox con supporto Retry
{
    "event_type": "USER_ACTION_LOGGED",
    "payload": {
        "user_id": "12345",
        "action": "CONFIG_UPDATE",
        "timestamp": "2026-03-28T10:00:00Z"
    },
    "status": "PENDING",
    "retry_count": 0
}
    """, language="json")

    st.markdown("### 2. Sicurezza e Autenticazione delle API")
    st.write("Tutte le chiamate esterne verso i componenti core richiedono intestazioni di sicurezza basate su token crittografati.")

# ==========================================
# DISCLAIMER LEGALE DI TUTELA E RISERVATEZZA
# ==========================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.85em;'>
    <strong>⚖️ AVVISO DI RISERVATEZZA E TUTELA LEGALE</strong><br>
    Il software, le architetture, i codici sorgente e le specifiche tecniche associati al progetto <strong>Software RGandja</strong>
    sono di proprietà esclusiva e protetti dalle normative vigenti in materia di proprietà intellettuale e segreto industriale.
    Il presente ambiente è esclusivamente destinato a scopi di consultazione, verifica operativa e test autorizzati.
    È tassativamente vietata qualsiasi forma di copia, riproduzione, estrazione di dati o divulgazione a terzi non preventivamente autorizzati.
</div>
""", unsafe_allow_html=True)
