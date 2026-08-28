from database import get_connection

def create_tables():
    connection = get_connection()
    if connection is None:
        print("Impossibile procedere: connessione al database fallita.")
        return

    try:
        cursor = connection.cursor()

        # Creazione della prima tabella operativa del software
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id SERIAL PRIMARY KEY,
                event_type VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        connection.commit()
        print("Tabella 'system_logs' creata con successo (o già esistente).")

        cursor.close()
        connection.close()
    except Exception as error:
        print(f"Errore durante la creazione delle tabelle: {error}")

if __name__ == "__main__":
    create_tables()