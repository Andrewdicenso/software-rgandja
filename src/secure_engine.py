from database import db_transaction
from logger_enterprise import get_logger
from models import EnginePayload

logger = get_logger()

def execute_secure_operation(event_type: str, description: str):
    # 1. Validazione preventiva con Pydantic (Data Contract)
    try:
        payload = EnginePayload(event_type=event_type, description=description)
    except Exception as validation_error:
        logger.error(f"Errore di validazione del payload: {validation_error}")
        return False

    # 2. Esecuzione atomica tramite Context Manager (Unit of Work)
    try:
        with db_transaction() as cursor:
            # Creazione tabella se non esiste
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS enterprise_logs (
                    id SERIAL PRIMARY KEY,
                    event_type VARCHAR(100) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Inserimento sicuro dei dati validati
            query = "INSERT INTO enterprise_logs (event_type, description) VALUES (%s, %s);"
            cursor.execute(query, (payload.event_type, payload.description))

        logger.info(f"Operazione enterprise completata con successo: [{payload.event_type}]")
        return True
    except Exception as db_error:
        logger.critical(f"Transazione fallita e rolled back: {db_error}")
        return False

if __name__ == "__main__":
    execute_secure_operation("ENTERPRISE_TEST", "Test architettura software di livello superiore completato.")