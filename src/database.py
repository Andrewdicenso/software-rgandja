import os
from contextlib import contextmanager
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def get_raw_connection():
    """Apre una connessione grezza al database PostgreSQL."""
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )

@contextmanager
def db_transaction():
    """Context Manager enterprise per la gestione atomica delle transazioni.
    Gestisce automaticamente COMMIT in caso di successo e ROLLBACK in caso di eccezione,
    garantendo la chiusura sicura di cursore e connessione.
    """
    connection = get_raw_connection()
    cursor = connection.cursor()
    try:
        yield cursor
        connection.commit()
    except Exception as error:
        connection.rollback()
        print(f"[ERRORE TRANSAZIONE] Rollback eseguito a causa di: {error}")
        raise
    finally:
        cursor.close()
        connection.close()

if __name__ == "__main__":
    # Test del Context Manager
    try:
        with db_transaction() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"Connessione con Context Manager riuscita! Versione DB: {version[0]}")
    except Exception:
        print("Test fallito.")