from fastapi import FastAPI, Header, HTTPException, Depends, status
from pydantic import BaseModel
from datetime import datetime
import uuid
from src.database.multi_tenant_core import MultiTenantDatabase

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
def get_verified_tenant(x_tenant_id: str = Header(..., description="Secure SaaS Tenant Identifier")):
    """
    SaaS Security Gate: Extracts and verifies the Tenant ID from request headers.
    In production, this decodes a JWT bearer token instead.
    """
    if not x_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing secure tenant authorization header."
        )
    
    # Check if this tenant is provisioned in our system
    conn = db._get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT tenant_id, subscription_status FROM tenants WHERE tenant_id = ?", (x_tenant_id,))
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
        
    return x_tenant_id

# --- Endpoint ---
@app.post("/api/v1/ingest")
async def ingest_transaction(
    payload: TransactionPayload,
    tenant_id: str = Depends(get_verified_tenant) # Automatically isolates this request
):
    """
    Secure endpoint routing streams straight to the caller's isolated ledger.
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
    
    # Save the transaction, isolated under the verified tenant
    db.write_transaction(tenant_id=tenant_id, data=transaction_data)
    
    return {
        "status": "SUCCESS",
        "message": f"Record {tx_id} ingested securely into isolated space.",
        "routing_boundary": tenant_id
    }