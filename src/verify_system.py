from database import db_transaction
from logger_enterprise import get_logger

logger = get_logger()

def verify_database_state():
    logger.info("Avvio della verifica dello stato del database...")
    try:
        with db_transaction() as cursor:
            # 1. Verifica enterprise_logs
            cursor.execute("SELECT COUNT(*) FROM enterprise_logs;")
            logs_count = cursor.fetchone()[0]

            # 2. Verifica event_outbox e stati
            cursor.execute("SELECT status, COUNT(*) FROM event_outbox GROUP BY status;")
            outbox_stats = cursor.fetchall()

            print("\n================ REPORT DI VERIFICA SISTEMA ================")
            print(f"[*] Totale record in 'enterprise_logs': {logs_count}")
            print("[*] Stati nella tabella 'event_outbox':")
            for status, count in outbox_stats:
                print(f"    - {status}: {count}")
            print("============================================================\n")

        logger.info("Verifica dello stato del database completata con successo.")
        return True
    except Exception as error:
        logger.critical(f"Errore durante la verifica del database: {error}")
        return False

if __name__ == "__main__":
    verify_database_state()