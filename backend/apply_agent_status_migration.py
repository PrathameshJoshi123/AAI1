import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ps21_insurance.db")

def migrate():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    def add_col(table, col, col_def):
        cursor.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cursor.fetchall()]
        if col not in cols:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_def}")
            print(f"Added column {col} to {table}.")
        else:
            print(f"Column {col} already exists in {table}.")

    add_col("agent_configurations", "status", "VARCHAR(30) NOT NULL DEFAULT 'active'")
    add_col("agent_configurations", "last_executed_at", "DATETIME")
    add_col("agent_configurations", "total_executions", "INTEGER NOT NULL DEFAULT 0")
    add_col("agent_configurations", "successful_executions", "INTEGER NOT NULL DEFAULT 0")
    add_col("agent_configurations", "failed_executions", "INTEGER NOT NULL DEFAULT 0")
    add_col("agent_configurations", "avg_latency_ms", "INTEGER")

    conn.commit()
    conn.close()
    print("Migration finished successfully.")

if __name__ == "__main__":
    migrate()

