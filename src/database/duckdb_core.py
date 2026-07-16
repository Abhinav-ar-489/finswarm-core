import os
import duckdb
import logging

# Configure logging for production tracing
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FinSwarmCore.DuckDBCore")

class DuckDBEngine:
    def __init__(self, db_path: str = "data/processed/audit.db"):
        """Initializes the persistent local DuckDB storage database container."""
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        # Connect to a local database file structure
        self.conn = duckdb.connect(self.db_path)
        logger.info(f"Initialized persistent local DuckDB instance at: {self.db_path}")

    def ingest_raw_ledger(self, csv_path: str = "data/raw/corporate_ledger.csv"):
        """Ingests raw CSV ledger records directly into an optimized columnar database table."""
        if not os.path.exists(csv_path):
            logger.error(f"Ingestion failed: Target ledger file not found at {csv_path}")
            raise FileNotFoundError(f"Missing resource: {csv_path}")

        logger.info(f"Parsing and vectorizing raw data stream from: {csv_path}")
        
        # DuckDB auto-detects schemas and column types natively from CSV lines instantly
        self.conn.execute(f"""
            CREATE OR REPLACE TABLE ledger AS 
            SELECT * FROM read_csv_auto('{csv_path}');
        """)
        
        row_count = self.conn.execute("SELECT COUNT(*) FROM ledger;").fetchone()[0]
        logger.info(f"Successfully ingested {row_count} records into the columnar execution space.")

    def run_mathematical_audit(self) -> list[dict]:
        """Runs fast local SQL window analytics to spot hard anomalies (Duplicate Billing)."""
        logger.info("Executing Level 1 Mathematical Anomaly Detection Loop...")
        
        # Query to instantly isolate identical vendor, amount, description, and timestamp matches
        duplicate_query = """
            WITH DuplicateTraces AS (
                SELECT *, 
                       COUNT(*) OVER(PARTITION BY vendor_name, amount, timestamp, description) as occurrence_count
                FROM ledger
            )
            SELECT transaction_id, account_code, vendor_name, amount, timestamp, description
            FROM DuplicateTraces
            WHERE occurrence_count > 1
            ORDER BY vendor_name, timestamp;
        """
        
        results = self.conn.execute(duplicate_query).fetchall()
        
        flagged_anomalies = []
        for row in results:
            flagged_anomalies.append({
                "transaction_id": row[0],
                "account_code": row[1],
                "vendor_name": row[2],
                "amount": row[3],
                "timestamp": row[4].isoformat() if hasattr(row[4], 'isoformat') else str(row[4]),
                "description": row[5],
                "anomaly_type": "DUPLICATE_BILLING",
                "severity": "WARNING"
            })
            
        logger.info(f"Level 1 Audit finished. Flagged {len(flagged_anomalies)} mathematical anomalies.")
        return flagged_anomalies

    def close(self):
        """Safely closes the database connection file handles."""
        self.conn.close()
        logger.info("DuckDB engine session terminated cleanly.")

if __name__ == "__main__":
    engine = DuckDBEngine()
    try:
        engine.ingest_raw_ledger()
        anomalies = engine.run_mathematical_audit()
        print("\n--- 🔍 DETECTED LEVEL 1 MATHEMATICAL ANOMALIES ---")
        for anomaly in anomalies:
            print(f"[{anomaly['anomaly_type']}] Vendor: {anomaly['vendor_name']} | Amount: ${anomaly['amount']} | ID: {anomaly['transaction_id']}")
    finally:
        engine.close()