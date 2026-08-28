from database import db_transaction
from logger_enterprise import get_logger

logger = get_logger()

def publish_event(aggregate_type: str, payload: str):
    """Inserisce un evento nella tabella outbox in modo atomico."""
    try:
        with db_transaction() as cursor:
            query = "INSERT INTO event_outbox (aggregate_type, payload, status) VALUES (%s, %s, 'PENDING');"
            cursor.execute(query, (aggregate_type, payload))
        logger.info(f"Evento accodato con successo nell'Outbox: [{aggregate_type}] -> {payload}")
        return True
    except Exception as error:
        logger.error(f"Errore durante l'accodamento dell'evento outbox: {error}")
        return False

if __name__ == "__main__":
    publish_event("SYSTEM_EVENT", "Test di pubblicazione asincrona tramite Outbox Pattern.")