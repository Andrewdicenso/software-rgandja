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
st.subheader("Event-Driven Enterprise Architecture & Outbox Pattern Manager")

# Sidebar di navigazione interna
menu = st.sidebar.selectbox("Navigazione", ["📊 Pannello di Controllo", "📖 Presentazione & Documentazione Tecnica", "🔌 Guide di Integrazione API"])

if menu == "📊 Pannello di Controllo":
    st.markdown("### Stato del Sistema e Gestione Coda")
    st.write("Benvenuto nell'area operativa protetta. Qui puoi monitorare, testare e controllare l'infrastruttura asincrona Outbox.")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🚀 Inizializza Tabelle Outbox", use_container_width=True):
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS outbox_events (
                        id SERIAL PRIMARY KEY,
                        event_type VARCHAR(255) NOT NULL,
                        payload JSONB NOT NULL,
                        status VARCHAR(50) DEFAULT 'PENDING',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """)
                conn.commit()
                cur.close()
                conn.close()
                st.success("Tabelle Outbox create e inizializzate con successo su Neon!")
            except Exception as e:
                st.error(f"Errore di connessione o inizializzazione: {e}")

        if st.button("📥 Inserisci Evento di Test (PENDING)", use_container_width=True):
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                payload_test = json.dumps({"user_id": "test_user_999", "action": "SIMULATED_TRANSACTION"})
                cur.execute(
                    "INSERT INTO outbox_events (event_type, payload, status) VALUES (%s, %s, %s);",
                    ("TEST_EVENT", payload_test, "PENDING")
                )
                conn.commit()
                cur.close()
                conn.close()
                st.success("Evento di test inserito con successo! Ora puoi eseguire il worker.")
            except Exception as e:
                st.error(f"Errore durante l'inserimento dell'evento: {e}")

    with col2:
        if st.button("⚙️ Esegui Worker Eventi Pendenti", use_container_width=True):
            try:
                import psycopg2
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                cur.execute("SELECT id, event_type, payload FROM outbox_events WHERE status = 'PENDING';")
                events = cur.fetchall()

                if not events:
                    st.info("Nessun evento pendente trovato nella coda Outbox.")
                else:
                    count = 0
                    for event in events:
                        event_id, event_type, payload = event
                        cur.execute("UPDATE outbox_events SET status = 'PROCESSED' WHERE id = %s;", (event_id,))
                        count += 1

                    conn.commit()
                    st.success(f"Worker completato con successo: elaborati {count} eventi pendenti.")

                cur.close()
                conn.close()
            except Exception as e:
                st.error(f"Errore durante l'esecuzione del worker: {e}")

    st.markdown("---")
    st.markdown("### 📋 Monitoraggio in Tempo Reale (Audit Log Coda Outbox)")

    # Sezione Tabella di Audit dello stato database
    try:
        import psycopg2
        conn = psycopg2.connect(db_url)
        query = "SELECT id, event_type, payload, status, created_at FROM outbox_events ORDER BY id DESC LIMIT 20;"
        df_events = pd.read_sql(query, conn)
        conn.close()

        if df_events.empty:
            st.info("La tabella degli eventi è attualmente vuota. Inizializza le tabelle o inserisci un evento di test.")
        else:
            st.dataframe(df_events, use_container_width=True)
    except Exception:
        st.warning("Impossibile caricare la tabella di audit. Assicurati che le tabelle Outbox siano state inizializzate.")

elif menu == "📖 Presentazione & Documentazione Tecnica":
    st.markdown("## 📖 Informazioni sul Progetto e Specifiche Architetturali")
    st.write("""
    **Software RGandja** è un'architettura enterprise event-driven progettata per garantire la massima affidabilità,
    tracciabilità transazionale e sicurezza nella gestione dei flussi critici di sistema.
    """)

    st.markdown("### 🔄 Come Funziona il Sistema (Flusso Operativo)")
    st.markdown("""
    Il sistema si basa sul **Transactional Outbox Pattern**, risolvendo il problema della sincronizzazione tra database e broker di messaggi:
    1. **Scrittura Atomica (PENDING):** Durante una transazione di business, l'evento viene salvato direttamente sul database relazionale (Neon) all'interno della tabella `outbox_events` con stato `PENDING`. Questo garantisce che nessun evento vada perso neanche in caso di crash della rete.
    2. **Elaborazione Asincrona (Worker):** Un processo worker autonomo interroga periodicamente la tabella alla ricerca di eventi non ancora elaborati (`PENDING`).
    3. **Consumazione e Transizione di Stato (PROCESSED):** Il worker preleva il payload JSON, lo spedisce al sistema ricevente (o lo simula) e aggiorna lo stato dell'evento in modo sicuro a `PROCESSED`, impedendo doppie elaborazioni (*at-least-once delivery* con gestione idempotente).
    """)

    st.markdown("### 🏛️ Componenti Principali")
    st.markdown("""
    * **Transactional Outbox:** Disaccoppia la scrittura dei dati dalla pubblicazione dei messaggi.
    * **Worker Resilienti:** Gestione dei batch di eventi in background.
    * **Audit Enterprise:** Tracciamento rigoroso di ogni singola transazione per fini legali e di conformità.
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
    st.write("Tutte le chiamate esterne verso i componenti core richiedono intestazioni di sicurezza basate su token crittografati e validazione rigorosa dei parametri.")

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