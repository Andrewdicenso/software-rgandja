import logging
import os

# Creazione della cartella logs se non esiste
os.makedirs("logs", exist_ok=True)

# Configurazione del logger enterprise
logging.basicConfig(
    filename="logs/rgandja_production.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Aggiungiamo anche l'output su console per visibilità immediata
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s [%(levelname)s]: %(message)s")
console_handler.setFormatter(formatter)

logger = logging.getLogger("RGandjaEngine")
if not logger.hasHandlers():
    logger.addHandler(console_handler)

def get_logger():
    return logger

if __name__ == "__main__":
    log = get_logger()
    log.info("Test del sistema di logging strutturato completato con successo.")