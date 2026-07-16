import duckdb
import os

def init_production_db(db_path="data/processed/audit.db"):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = duckdb.connect(db_path)
    
    # Create the ledger table with specialized multi-entity columns
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ledger (
            transaction_id VARCHAR PRIMARY KEY,
            employee_id VARCHAR,
            cost_center VARCHAR,
            vendor_name VARCHAR,
            bank_routing_account VARCHAR,
            amount DOUBLE,
            timestamp TIMESTAMP
        );
    """)
    conn.close()
    print("🚀 Production DuckDB Schema initialization complete.")

if __name__ == "__main__":
    init_production_db()