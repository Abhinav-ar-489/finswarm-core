import os
import uvicorn
import logging
import duckdb
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from datetime import datetime

# Setup explicit telemetry logging for backend monitoring
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FinSwarmCore.WebhookGateway")

app = FastAPI(
    title="FinSwarm Streaming Ingestion Gateway",
    description="Production-grade real-time corporate ledger data ingestion engine",
    version="1.0.0"
)

DB_PATH = "data/processed/audit.db"

# =====================================================================
# 📋 PERIMETER SCHEMA VALIDATION MATRIX
# =====================================================================
class TransactionPayload(BaseModel):
    transaction_id: str = Field(..., example="TX_882910")
    employee_id: str = Field(..., example="EMP_1042")
    cost_center: str = Field(..., example="6040-IT")
    vendor_name: str = Field(..., example="Amazon Web Services")
    bank_routing_account: str = Field(..., example="ACC_ROUTING_77211")
    amount: float = Field(..., example=4950.00, gt=0)
    timestamp: str = Field(..., example="2026-07-15T14:30:00")

@app.on_event("startup")
def verify_persistence_layer():
    """Validates target processing engine database has been fully initialized."""
    if not os.path.exists(DB_PATH):
        logger.warning(f"Database context missing at {DB_PATH}. Initializing fresh schema container...")
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        conn = duckdb.connect(DB_PATH)
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
    logger.info("Persistence layer connection array verified and active.")

# =====================================================================
# 🔌 LIVE STREAMING INGESTION ENDPOINT
# =====================================================================
@app.post("/webhook/v1/ingest", status_code=status.HTTP_201_CREATED)
async def ingest_ledger_webhook(payload: TransactionPayload):
    """Processes, sanitizes, and appends incoming transactional payloads directly into DuckDB."""
    logger.info(f"Intercepted transaction broadcast stream: {payload.transaction_id}")
    
    try:
        # Standardize incoming time formatting cleanly to ISO standard
        parsed_ts = datetime.fromisoformat(payload.timestamp.replace('Z', '+00:00'))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid ISO 8601 timestamp configuration format."
        )

    # Open data gate using shared context blocks to prevent data locking conflicts
    conn = duckdb.connect(DB_PATH)
    try:
        # Parameterized execution queries block malicious injection vectors natively
        conn.execute("""
            INSERT INTO ledger (transaction_id, employee_id, cost_center, vendor_name, bank_routing_account, amount, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            payload.transaction_id,
            payload.employee_id,
            payload.cost_center,
            payload.vendor_name,
            payload.bank_routing_account,
            payload.amount,
            parsed_ts
        ))
        logger.info(f"Transaction {payload.transaction_id} bound cleanly to disk cache array.")
        return {"status": "SUCCESS", "message": f"Record {payload.transaction_id} ingested securely."}
    except duckdb.ConstraintException:
        logger.warning(f"Duplicate packet drop: Transaction {payload.transaction_id} already exists.")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Transaction ID {payload.transaction_id} already exists in the data persistence array."
        )
    except Exception as e:
        logger.error(f"Perimeter error during streaming execution: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal streaming engine error."
        )
    finally:
        conn.close()

if __name__ == "__main__":
    # Local fallback execution module
    uvicorn.run("webhook_gateway:app", host="127.0.0.1", port=8000, reload=True)