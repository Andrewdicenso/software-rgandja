# SOFTWARE RGANDJA

Motore di elaborazione e gestione basato su Python e database PostgreSQL.

## Architettura del Progetto
- `main.py`: Punto d'ingresso principale che orchestra i flussi di log, configurazione ed elaborazione.
- `src/database.py`: Modulo centralizzato per la gestione della connessione al database PostgreSQL tramite `psycopg2` e `.env`.
- `src/init_db.py`: Script di inizializzazione delle tabelle di sistema.
- `src/config_loader.py`: Modulo di gestione e caricamento delle configurazioni.
- `src/engine_core.py`: Modulo di elaborazione della logica di business e salvataggio dei risultati.

## Requisiti
- Python 3.x
- PostgreSQL 15+
- Librerie Python: `psycopg2-binary`, `python-dotenv`

## Configurazione
Assicurati di avere il file `.env` compilato correttamente nella root del progetto con i parametri di connessione al database:
```env
DB_HOST=localhost
DB_PORT=5432
DB_NAME=rgandja_engine_db
DB_USER=postgres
DB_PASSWORD=tua_password