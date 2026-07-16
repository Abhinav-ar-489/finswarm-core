from fastapi import FastAPI, Header, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime
import uuid
from src.database.multi_tenant_core import MultiTenantDatabase
from src.utils.auth import verify_and_decode_token

app = FastAPI(title="FinSwarm Multi-Tenant SaaS Gateway")
db = MultiTenantDatabase()

# --- Schemas ---
class TransactionPayload(BaseModel):
    employee_id: str
    cost_center: str
    vendor_name: str
    bank_routing_account: str
    amount: float

# --- Security Dependency ---
def get_verified_tenant(authorization: str = Header(..., description="Authorization Bearer Token")):
    """
    SaaS Security Gate: Extracts and cryptographically verifies the JWT Bearer Token.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization format. Must use 'Bearer <token>'."
        )
    
    token = authorization.split(" ")[1]
    
    try:
        # Decrypt, verify signature integrity, and check expiration
        claims = verify_and_decode_token(token)
        tenant_id = claims["sub"]
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    
    # Check if this tenant exists and has an active status in our database registry
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tenant_id, subscription_status FROM tenants WHERE tenant_id = ?", (tenant_id,))
    tenant = cursor.fetchone()
    conn.close()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized or unprovisioned tenant workspace."
        )
        
    if tenant[1] != 'active':
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail="Tenant subscription is inactive. Please renew billing."
        )
        
    return tenant_id

# --- Endpoint ---
@app.post("/api/v1/ingest")
async def ingest_transaction(
    payload: TransactionPayload,
    tenant_id: str = Depends(get_verified_tenant) # Enforces dynamic security routing
):
    """
    Secure ingestion endpoint: Decodes JWT claims, checks tenant limits,
    and isolates transactions strictly into the verified tenant's ledger.
    """
    tx_id = f"TX_STREAM_{uuid.uuid4().hex[:6].upper()}"
    
    transaction_data = {
        "transaction_id": tx_id,
        "employee_id": payload.employee_id,
        "cost_center": payload.cost_center,
        "vendor_name": payload.vendor_name,
        "bank_routing_account": payload.bank_routing_account,
        "amount": payload.amount,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    db.write_transaction(tenant_id=tenant_id, data=transaction_data)
    
    return {
        "status": "SUCCESS",
        "message": f"Record {tx_id} ingested securely into isolated space.",
        "routing_boundary": tenant_id
    }