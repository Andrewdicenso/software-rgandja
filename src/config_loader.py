import os
from database import get_connection

def load_system_config():
    connection = get_connection()
    if connection is None:
        print("Impossibile caricare le configurazioni: connessione assente.")
        return None

    try:
        cursor = connection.cursor()

        # Creazione della tabella di configurazione se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_configs (
                id SERIAL PRIMARY KEY,
                config_key VARCHAR(100) UNIQUE NOT NULL,
                config_value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Inserimento di una configurazione di default se non presente
        cursor.execute("""
            INSERT INTO system_configs (config_key, config_value)
            VALUES ('APP_STATUS', 'ACTIVE')
            ON CONFLICT (config_key) DO NOTHING;
        """)

        connection.commit()

        # Recupero della configurazione
        cursor.execute("SELECT config_key, config_value FROM system_configs;")
        configs = cursor.fetchall()

        cursor.close()
        connection.close()
        return configs
    except Exception as error:
        print(f"Errore nel caricamento delle configurazioni: {error}")
        return None

if __name__ == "__main__":
    print(load_system_config())