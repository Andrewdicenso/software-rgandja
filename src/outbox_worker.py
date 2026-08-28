from database import db_transaction
from logger_enterprise import get_logger

logger = get_logger()

def process_pending_events():
    """Legge ed elabora gli eventi pendenti dalla tabella outbox."""
    try:
        processed_count = 0
        with db_transaction() as cursor:
            # Seleziona gli eventi in stato PENDING
            cursor.execute("SELECT id, aggregate_type, payload FROM event_outbox WHERE status = 'PENDING' FOR UPDATE SKIP LOCKED;")
            events = cursor.fetchall()

            if not events:
                logger.info("Nessun evento pendente da elaborare nell'Outbox.")
                return 0

            for event_id, aggregate_type, payload in events:
                logger.info(f"Elaborazione evento ID {event_id} [{aggregate_type}]: {payload}")

                # Simulazione di elaborazione asincrona avvenuta con successo

                # Aggiornamento dello stato a PROCESSED
                cursor.execute("UPDATE event_outbox SET status = 'PROCESSED' WHERE id = %s;", (event_id,))
                processed_count += 1

        logger.info(f"Worker completato: elaborati con successo {processed_count} eventi.")
        return processed_count
    except Exception as error:
        logger.error(f"Errore durante l'esecuzione del worker outbox: {error}")
        return 0

if __name__ == "__main__":
    process_pending_events()