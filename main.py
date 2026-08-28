import sys
import os

# Aggiunge la cartella src al path per permettere l'importazione dei moduli
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from logger_enterprise import get_logger
from outbox_init import create_outbox_table
from outbox_publisher import publish_event
from outbox_worker import process_pending_events

logger = get_logger()

def main():
    logger.info("=== Avvio di SOFTWARE RGANDJA (Event-Driven Enterprise) ===")

    # 1. Inizializzazione della infrastruttura Outbox
    create_outbox_table()

    # 2. Pubblicazione di un evento di sistema asincrono
    publish_event("SYSTEM_BOOT_EVENT", "Avvio del sistema orchestrato tramite Transactional Outbox.")

    # 3. Esecuzione del Worker per smaltire gli eventi pendenti
    logger.info("Avvio del Dispatcher/Worker per gli eventi asincroni...")
    processed = process_pending_events()

    logger.info(f"=== Ciclo operativo completato. Eventi elaborati: {processed} ===")

if __name__ == "__main__":
    main()