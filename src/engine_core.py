from database import get_connection
from logger_service import log_event

def process_engine_data(input_data):
    connection = get_connection()
    if connection is None:
        print("Impossibile elaborare i dati: connessione al database assente.")
        return None

    try:
        cursor = connection.cursor()

        # Creazione della tabella per i risultati dell'engine se non esiste
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS engine_results (
                id SERIAL PRIMARY KEY,
                input_payload TEXT NOT NULL,
                result_status VARCHAR(50) NOT NULL,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # Simulazione di elaborazione della logica di business
        status = "SUCCESS" if len(input_data) > 0 else "EMPTY_INPUT"

        # Salvataggio del risultato nel database
        query = "INSERT INTO engine_results (input_payload, result_status) VALUES (%s, %s);"
        cursor.execute(query, (input_data, status))

        connection.commit()
        log_event("ENGINE_PROCESS", f"Elaborazione completata per il payload: {input_data}")

        cursor.close()
        connection.close()
        return status
    except Exception as error:
        print(f"Errore durante l'elaborazione dell'engine: {error}")
        return "ERROR"

if __name__ == "__main__":
    process_engine_data("Test dati di input RGandja")