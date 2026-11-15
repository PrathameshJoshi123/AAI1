"""Synchronous SQLite migration script for Phase 6 schema enhancements."""
import json
import sqlite3
import os
from datetime import datetime, timezone

DB_PATH = os.path.join(os.path.dirname(__file__), "ps21_insurance.db")

def migrate():
    print(f"Connecting to database at {DB_PATH}...")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create product_pricing_matrices table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS product_pricing_matrices (
        id VARCHAR(36) PRIMARY KEY,
        product_id VARCHAR(36) NOT NULL REFERENCES insurance_products(id) ON DELETE CASCADE,
        matrix_version VARCHAR(50) NOT NULL UNIQUE,
        is_active BOOLEAN NOT NULL DEFAULT 1,
        effective_from DATETIME NOT NULL,
        effective_to DATETIME,
        age_band_rates_json JSON NOT NULL,
        gender_multipliers_json JSON NOT NULL,
        smoker_loading_factors_json JSON NOT NULL,
        frequency_multipliers_json JSON NOT NULL,
        health_tier_loadings_json JSON NOT NULL,
        rider_rate_cards_json JSON NOT NULL,
        tax_rate_percent NUMERIC(5, 2) NOT NULL DEFAULT 18.00,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_product_pricing_matrices_product_id ON product_pricing_matrices (product_id);")
    cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_product_pricing_matrices_matrix_version ON product_pricing_matrices (matrix_version);")
    print("Table product_pricing_matrices verified.")

    # Helper function to add columns if missing
    def add_column_if_missing(table, col_name, col_def):
        cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in cursor.fetchall()]
        if col_name not in columns:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col_name} {col_def}")
            print(f"Added column {col_name} to {table}.")

    # 2. Add columns to insurance_products
    add_column_if_missing("insurance_products", "insurer_name", "VARCHAR(150) DEFAULT 'Star Union Life & General'")
    add_column_if_missing("insurance_products", "insurer_code", "VARCHAR(50) DEFAULT 'SULG-IN'")
    add_column_if_missing("insurance_products", "insurer_solvency_ratio", "NUMERIC(5, 2) DEFAULT 2.15")
    add_column_if_missing("insurance_products", "policy_type", "VARCHAR(50) DEFAULT 'individual'")
    add_column_if_missing("insurance_products", "coverage_summary_json", "JSON")
    add_column_if_missing("insurance_products", "benefits_list_json", "JSON")
    add_column_if_missing("insurance_products", "exclusions_list_json", "JSON")
    add_column_if_missing("insurance_products", "waiting_periods_json", "JSON")
    add_column_if_missing("insurance_products", "required_declarations_json", "JSON")
    add_column_if_missing("insurance_products", "required_documents_json", "JSON")

    # 3. Add columns to product_configurations
    add_column_if_missing("product_configurations", "sum_assured_step", "NUMERIC(14, 2) DEFAULT 500000.0")
    add_column_if_missing("product_configurations", "available_frequencies_json", "JSON")

    # 4. Add columns to recommendations
    add_column_if_missing("recommendations", "configuration_id", "INTEGER")
    add_column_if_missing("recommendations", "recommended_sum_assured", "NUMERIC(14, 2) DEFAULT 10000000.0")
    add_column_if_missing("recommendations", "recommended_term_years", "INTEGER DEFAULT 30")
    add_column_if_missing("recommendations", "match_factors_json", "JSON")
    add_column_if_missing("recommendations", "assumptions_json", "JSON")
    add_column_if_missing("recommendations", "limitations_json", "JSON")
    add_column_if_missing("recommendations", "alternative_options_json", "JSON")

    # 5. Add columns to quotes
    add_column_if_missing("quotes", "configuration_id", "INTEGER")
    add_column_if_missing("quotes", "pricing_matrix_version", "VARCHAR(50) DEFAULT 'v1.0.0-actuarial-2026'")
    add_column_if_missing("quotes", "selected_riders_json", "JSON")
    add_column_if_missing("quotes", "health_loading_amount", "NUMERIC(10, 2) DEFAULT 0.00")
    add_column_if_missing("quotes", "net_premium", "NUMERIC(10, 2) DEFAULT 0.00")

    conn.commit()

    # 6. Seed actuarial pricing matrices
    from app.db.seed_pricing_matrices import PRICING_MATRICES
    import uuid

    for m in PRICING_MATRICES:
        p_code = m["product_code"]
        cursor.execute("SELECT id, name FROM insurance_products WHERE code = ?", (p_code,))
        row = cursor.fetchone()
        if not row:
            print(f"Product {p_code} not found in DB.")
            continue
        p_id, p_name = row

        cursor.execute("SELECT id FROM product_pricing_matrices WHERE matrix_version = ?", (m["matrix_version"],))
        if not cursor.fetchone():
            matrix_id = str(uuid.uuid4())
            now_iso = datetime.now(timezone.utc).isoformat()
            cursor.execute("""
            INSERT INTO product_pricing_matrices (
                id, product_id, matrix_version, is_active, effective_from,
                age_band_rates_json, gender_multipliers_json, smoker_loading_factors_json,
                frequency_multipliers_json, health_tier_loadings_json, rider_rate_cards_json,
                tax_rate_percent, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                matrix_id,
                p_id,
                m["matrix_version"],
                1,
                now_iso,
                json.dumps(m["age_band_rates_json"]),
                json.dumps(m["gender_multipliers_json"]),
                json.dumps(m["smoker_loading_factors_json"]),
                json.dumps(m["frequency_multipliers_json"]),
                json.dumps(m["health_tier_loadings_json"]),
                json.dumps(m["rider_rate_cards_json"]),
                m["tax_rate_percent"],
                now_iso,
                now_iso,
            ))
            print(f"Seeded pricing matrix {m['matrix_version']} for {p_name}.")
        else:
            print(f"Pricing matrix {m['matrix_version']} already seeded.")

    # 7. Update insurance products with rich Phase 6 metadata
    from app.db.seed_products import PRODUCTS_CONFIG
    for p in PRODUCTS_CONFIG:
        cursor.execute("""
        UPDATE insurance_products SET
            insurer_name = ?,
            insurer_code = ?,
            insurer_solvency_ratio = ?,
            policy_type = ?,
            coverage_summary_json = ?,
            benefits_list_json = ?,
            exclusions_list_json = ?,
            waiting_periods_json = ?,
            required_declarations_json = ?,
            required_documents_json = ?,
            base_rules_json = ?
        WHERE code = ?
        """, (
            p["insurer_name"],
            p["insurer_code"],
            p["insurer_solvency_ratio"],
            p["policy_type"],
            json.dumps(p["coverage_summary_json"]),
            json.dumps(p["benefits_list_json"]),
            json.dumps(p["exclusions_list_json"]),
            json.dumps(p["waiting_periods_json"]),
            json.dumps(p["required_declarations_json"]),
            json.dumps(p["required_documents_json"]),
            json.dumps(p["base_rules_json"]),
            p["code"],
        ))
        print(f"Updated metadata for product {p['name']}.")

    conn.commit()
    conn.close()
    print("Phase 6 Migration and Seeding Completed Successfully!")

if __name__ == "__main__":
    migrate()

