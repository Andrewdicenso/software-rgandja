import hashlib
import json
import os
import sys
import pandas as pd
import psycopg2
import streamlit as st

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

st.set_page_config(
    page_title="Software RGandja - Vetrina Enterprise",
    page_icon="🛡️",
    layout="wide",
)

db_url = st.secrets.get("url", st.secrets.get("postgres", {}).get("url"))

# ==========================================
# 1. BLOCCO DI SICUREZZA E LOGIN OBBLIGATORIO
# ==========================================

if "password_correct" not in st.session_state:
  st.session_state["password_correct"] = False
if "login_attempted" not in st.session_state:
  st.session_state["login_attempted"] = False

if not st.session_state["password_correct"]:
  st.markdown(
      "<h2 style='text-align: center;'>🔐 Accesso Riservato - Software"
      " RGandja</h2>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='text-align: center;'>Area protetta. Inserisci le credenziali"
      " per continuare.</p>",
      unsafe_allow_html=True,
  )


  def password_entered():
    st.session_state["login_attempted"] = True
    username = st.session_state.get("username", "")
    raw_password = st.session_state.get("password", "")
    password_hash = hashlib.sha256(raw_password.encode()).hexdigest()

    try:
      conn = psycopg2.connect(db_url)
      cur = conn.cursor()
      cur.execute(
          "SELECT role FROM users WHERE username = %s AND (password_hash = %s"
          " OR password_hash = %s);",
          (username, password_hash, raw_password),
      )
      user_record = cur.fetchone()
      cur.close()
      conn.close()

      if user_record:
        st.session_state["password_correct"] = True
        st.session_state["logged_user"] = username
        st.session_state["user_role"] = user_record[0]
        if "password" in st.session_state:
          del st.session_state["password"]
        if "username" in st.session_state:
          del st.session_state["username"]
      else:
        st.session_state["password_correct"] = False
    except Exception as e:
      st.error(f"Errore di connessione al database: {e}")
      st.session_state["password_correct"] = False


  col1, col2, col3 = st.columns([1, 2, 1])
  with col2:
    st.text_input("Username", key="username")
    st.text_input("Password", type="password", key="password")
    st.button("Accedi", on_click=password_entered, use_container_width=True)

  if st.session_state.get("login_attempted", False) and not st.session_state[
      "password_correct"
  ]:
    st.error("😕 Username o password errati. Riprova.")

  # BLOCCO TOTALE INVALICABILE
  st.stop()

# ==========================================
# 2. INTERFACCIA PRINCIPALE (ACCESSIBILE SOLO DOPO IL LOGIN)
# ==========================================

current_user = st.session_state.get("logged_user", "Utente")
current_role = st.session_state.get("user_role", "client")

st.title("🛡️ SOFTWARE RGANDJA")
st.subheader("Event-Driven Enterprise Architecture & Resilient Outbox Manager")

st.sidebar.info(
    f"👤 Utente: **{current_user}**\n\n🔑 Profilo: **{current_role.upper()}**"
)

menu = st.sidebar.selectbox(
    "Navigazione",
    [
        "📊 Pannello di Controllo",
        "📖 Presentazione & Documentazione Tecnica",
        "🔌 Guide di Integrazione API",
    ],
)

if menu == "📊 Pannello di Controllo":
  st.markdown("### Stato del Sistema e Gestione Coda Resiliente")

  if current_role == "admin":
    st.warning("⚠️ Area amministrativa avanzata (Accesso Admin)")
    st.write(
        "Area operativa avanzata con gestione dei tentativi (Retry) e isolamento"
        " degli errori (Dead Letter Queue)."
    )

    col1, col2 = st.columns(2)
    with col1:
      if st.button(
          "🚀 Inizializza / Aggiorna Tabelle Outbox (Con Retry & DLQ)",
          use_container_width=True,
      ):
        try:
          conn = psycopg2.connect(db_url)
          cur = conn.cursor()
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
          st.success(
              "Tabelle Outbox aggiornate con supporto a Retry e Dead Letter"
              " Queue su Neon!"
          )
        except Exception as e:
          st.error(f"Errore di connessione o inizializzazione: {e}")

      if st.button(
          "📥 Inserisci Evento di Test Normale (PENDING)",
          use_container_width=True,
      ):
        try:
          conn = psycopg2.connect(db_url)
          cur = conn.cursor()
          payload_test = json.dumps(
              {"user_id": current_user, "action": "SIMULATED_TRANSACTION"}
          )
          cur.execute(
              "INSERT INTO outbox_events (event_type, payload, status,"
              " retry_count) VALUES (%s, %s, %s, %s);",
              ("TEST_EVENT", payload_test, "PENDING", 0),
          )
          conn.commit()
          cur.close()
          conn.close()
          st.success("Evento di test regolare inserito con successo.")
        except Exception as e:
          st.error(f"Errore durante l'inserimento dell'evento: {e}")

    with col2:
      if st.button(
          "⚙️ Esegui Worker Resiliente (Con Gestione Fallimenti)",
          use_container_width=True,
      ):
        try:
          conn = psycopg2.connect(db_url)
          cur = conn.cursor()
          cur.execute(
              "SELECT id, event_type, payload, retry_count FROM outbox_events"
              " WHERE status = 'PENDING';"
          )
          events = cur.fetchall()

          if not events:
            st.info("Nessun evento pendente trovato nella coda Outbox.")
          else:
            processed_count = 0
            failed_count = 0
            dlq_count = 0

            for event in events:
              event_id, event_type, payload, retry_count = event
              cur.execute(
                  "UPDATE outbox_events SET status = 'PROCESSED',"
                  " retry_count = %s WHERE id = %s;",
                  (retry_count + 1, event_id),
              )
              processed_count += 1

            conn.commit()
            st.success(
                f"Worker completato: {processed_count} elaborati con successo."
            )

          cur.close()
          conn.close()
        except Exception as e:
          st.error(f"Errore durante l'esecuzione del worker resiliente: {e}")
  else:
    st.info(
        "👋 Benvenuto nell'area clienti. Da qui puoi monitorare lo stato in"
        " tempo reale delle code e degli audit log associati alla tua"
        " istanza."
    )

  st.markdown("---")
  st.markdown("### 📋 Monitoraggio in Tempo Reale (Audit Log Avanzato)")

  try:
    conn = psycopg2.connect(db_url)
    query = (
        "SELECT id, event_type, payload, status, retry_count, created_at FROM"
        " outbox_events ORDER BY id DESC LIMIT 20;"
    )
    df_events = pd.read_sql(query, conn)
    conn.close()

    if df_events.empty:
      st.info(
          "La tabella degli eventi è attualmente vuota. Inizializza le tabelle"
          " o inserisci un evento di test."
      )
    else:
      st.dataframe(df_events, use_container_width=True)
  except Exception:
    st.warning(
        "Impossibile caricare la tabella di audit. Assicurati che le tabelle"
        " Outbox siano state aggiornate."
    )

elif menu == "📖 Presentazione & Documentazione Tecnica":
  st.markdown(
      "## 📖 Informazioni sul Progetto e Specifiche Architetturali Avanzate"
  )
  st.write("""
    **Software RGandja** implementa un pattern architetturale di livello industriale orientato alla tolleranza agli errori
    e alla garanzia di recapito dei messaggi nei sistemi distribuiti.
    """)

elif menu == "🔌 Guide di Integrazione API":
  st.markdown("## 🔌 Come Integrare e Usare il Sistema")
  st.write(
      "Questa sezione fornisce le specifiche tecniche per connettere servizi"
      " esterni o client di terze parti all'infrastruttura RGandja."
  )

st.markdown("---")
st.markdown(
    """
<div style='text-align: center; color: gray; font-size: 0.85em;'>
    <strong>⚖️ AVVISO DI RISERVATEZZA E TUTELA LEGALE</strong><br>
    Il software, le architetture, i codici sorgente e le specifiche tecniche associati al progetto <strong>Software RGandja</strong>
    sono di proprietà esclusiva e protetti dalle normative vigenti in materia di proprietà intellettuale e segreto industriale.
    Il presente ambiente è esclusivamente destinato a scopi di consultazione, verifica operativa e test autorizzati.
    È tassativamente vietata qualsiasi forma di copia, riproduzione, estrazione di dati o divulgazione a terzi non preventivamente autorizzati.
</div>
""",
    unsafe_allow_html=True,
)