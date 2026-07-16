import os
import sqlite3  # Using SQLite locally to simulate PostgreSQL tenant partitions
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinSwarmCore.MultiTenantDB")

DB_PATH = "data/processed/saas_audit.db"

class MultiTenantDatabase:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._initialize_schema()

    def _get_connection(self):
        return sqlite3.connect(self.db_path)

    def _initialize_schema(self):
        """Initializes tables with strict tenant isolation fields."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Enable write-ahead logging (WAL) for high-performance SaaS read/write concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        
        # Every table in the SaaS environment MUST include a tenant_id column
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tenants (
                tenant_id TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                subscription_status TEXT DEFAULT 'active',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS isolated_ledger (
                transaction_id TEXT PRIMARY KEY,
                tenant_id TEXT NOT NULL,
                employee_id TEXT,
                cost_center TEXT,
                vendor_name TEXT,
                bank_routing_account TEXT,
                amount REAL,
                timestamp TIMESTAMP,
                FOREIGN KEY (tenant_id) REFERENCES tenants(tenant_id)
            );
        """)
        conn.commit()
        conn.close()
        logger.info("Multi-tenant database schema verified and isolated.")

    # =====================================================================
    # 🔒 STRICT TENANT-SCOPED DATA OPERATIONS
    # =====================================================================
    def register_new_tenant(self, tenant_id: str, company_name: str):
        """Registers a new paying SaaS client."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO tenants (tenant_id, company_name) VALUES (?, ?)", 
                (tenant_id, company_name)
            )
            conn.commit()
            logger.info(f"Successfully onboarded Tenant Space: {company_name} [{tenant_id}]")
        except sqlite3.IntegrityError:
            logger.warning(f"Tenant {tenant_id} registration failed: Already exists.")
        finally:
            conn.close()

    def write_transaction(self, tenant_id: str, data: dict):
        """Writes a transaction record, explicitly stamping it with the owner's tenant_id."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO isolated_ledger (
                    transaction_id, tenant_id, employee_id, cost_center, 
                    vendor_name, bank_routing_account, amount, timestamp
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                data["transaction_id"],
                tenant_id, # Strict architectural stamp
                data["employee_id"],
                data["cost_center"],
                data["vendor_name"],
                data["bank_routing_account"],
                data["amount"],
                data["timestamp"]
            ))
            conn.commit()
        finally:
            conn.close()

    def fetch_tenant_ledger(self, tenant_id: str) -> list:
        """Fetches transactions, enforcing a hard filter boundary so data never bleeds."""
        conn = self._get_connection()
        cursor = conn.cursor()
        try:
            # Parametrizing the tenant_id prevents any cross-tenant SQL injection attacks
            cursor.execute(
                "SELECT * FROM isolated_ledger WHERE tenant_id = ?", 
                (tenant_id,)
            )
            columns = [col[0] for col in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
        finally:
            conn.close()