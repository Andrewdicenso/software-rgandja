from database import db_transaction

def verify_logs():
    with db_transaction() as cursor:
        cursor.execute("SELECT id, event_type, description, created_at FROM enterprise_logs ORDER BY id DESC LIMIT 5;")
        rows = cursor.fetchall()
        print("\n--- ULTIMI LOG REGISTRATI NELLA TABELLA ENTERPRISE_LOGS ---")
        for row in rows:
            print(f"ID: {row[0]} | Tipo: {row[1]} | Descrizione: {row[2]} | Timestamp: {row[3]}")
        print("----------------------------------------------------------\n")

if __name__ == "__main__":
    verify_logs()