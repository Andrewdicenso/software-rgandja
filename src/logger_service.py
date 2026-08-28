from database import get_connection

def log_event(event_type, description):
    connection = get_connection()
    if connection is None:
        print("Connessione non disponibile per la scrittura del log.")
        return

    try:
        cursor = connection.cursor()
        query = "INSERT INTO system_logs (event_type, description) VALUES (%s, %s);"
        cursor.execute(query, (event_type, description))

        connection.commit()
        print(f"Log registrato con successo: [{event_type}] {description}")

        cursor.close()
        connection.close()
    except Exception as error:
        print(f"Errore durante l'inserimento del log: {error}")

if __name__ == "__main__":
    # Test rapido del servizio di log
    log_event("STARTUP", "Avvio del modulo di log di RGandja completato.")