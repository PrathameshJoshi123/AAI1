"""Synchronous SQLite migration script for Phase 11 Email Notification Engine schema."""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "ps21_insurance.db")

def migrate():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create email_delivery_logs table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS email_delivery_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
        recipient_email VARCHAR(255) NOT NULL,
        subject VARCHAR(255) NOT NULL,
        template_name VARCHAR(100) NOT NULL,
        status VARCHAR(50) NOT NULL,
        error_message TEXT,
        payload_json JSON,
        sent_at DATETIME,
        retry_count INTEGER NOT NULL DEFAULT 0,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_email_delivery_logs_user_id ON email_delivery_logs (user_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_email_delivery_logs_recipient_email ON email_delivery_logs (recipient_email);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_email_delivery_logs_template_name ON email_delivery_logs (template_name);")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_email_delivery_logs_status ON email_delivery_logs (status);")
    print("Table email_delivery_logs verified.")

    # 2. Create user_email_preferences table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS user_email_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id VARCHAR(36) NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
        notification_email VARCHAR(255),
        quote_alerts BOOLEAN NOT NULL DEFAULT 1,
        application_updates BOOLEAN NOT NULL DEFAULT 1,
        document_requests BOOLEAN NOT NULL DEFAULT 1,
        marketing_consent BOOLEAN NOT NULL DEFAULT 0,
        consent_timestamp DATETIME,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email_preferences_user_id ON user_email_preferences (user_id);")
    print("Table user_email_preferences verified.")

    conn.commit()
    conn.close()
    print("Phase 11 migration completed successfully!")

if __name__ == "__main__":
    migrate()

