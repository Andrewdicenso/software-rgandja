from database import db_transaction
from logger_enterprise import get_logger

logger = get_logger()

def create_outbox_table():
    try:
        with db_transaction() as cursor:
            # Creazione della tabella Outbox per la gestione asincrona degli eventi
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS event_outbox (
                    id SERIAL PRIMARY KEY,
                    aggregate_type VARCHAR(100) NOT NULL,
                    payload TEXT NOT NULL,
                    status VARCHAR(50) DEFAULT 'PENDING',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
        logger.info("Tabella event_outbox creata o verificata con successo.")
        return True
    except Exception as error:
        logger.critical(f"Errore nella creazione della tabella outbox: {error}")
        return False

if __name__ == "__main__":
    create_outbox_table()