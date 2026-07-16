import requests
import time
from src.database.multi_tenant_core import MultiTenantDatabase
from src.utils.auth import generate_saas_token

db = MultiTenantDatabase()

def provision_mock_tenants_and_get_tokens():
    print("--- 🏢 Onboarding SaaS Tenants & Generating JWT Access Keys ---")
    
    # Onboard Delta Airlines
    db.register_new_tenant(tenant_id="tenant_delta", company_name="Delta Air")
    delta_jwt = generate_saas_token(tenant_id="tenant_delta", company_name="Delta Air")
    print(f"🔑 Delta Access Token Generated: {delta_jwt[:40]}...[TRUNCATED]")
    
    # Onboard TechCorp Solutions
    db.register_new_tenant(tenant_id="tenant_techcorp", company_name="TechCorp Solutions")
    tech_jwt = generate_saas_token(tenant_id="tenant_techcorp", company_name="TechCorp Solutions")
    print(f"🔑 TechCorp Access Token Generated: {tech_jwt[:40]}...[TRUNCATED]\n")
    
    return delta_jwt, tech_jwt

def simulate_webhook_ingestion(delta_token, techcorp_token):
    print("--- 🔌 Simulating Isolated Webhook Streams (JWT Auth) ---")
    gateway_url = "http://127.0.0.1:8000/api/v1/ingest"
    
    # Stream Delta Air Transaction (Signed with Delta Bearer Token)
    delta_payload = {
        "employee_id": "EMP_DELTA_99",
        "cost_center": "Aviation-Ops",
        "vendor_name": "JetFuel-Corp",
        "bank_routing_account": "US-ROUT-112233",
        "amount": 45000.00
    }
    print("Sending Delta transaction with Authorization Bearer Token...")
    r1 = requests.post(
        gateway_url, 
        json=delta_payload, 
        headers={"Authorization": f"Bearer {delta_token}"}
    )
    print(f"Gateway Response: {r1.json()}\n")
    
    # Stream TechCorp Transaction (Signed with TechCorp Bearer Token)
    techcorp_payload = {
        "employee_id": "EMP_TECH_04",
        "cost_center": "R&D-SaaS",
        "vendor_name": "CloudHosting-LLC",
        "bank_routing_account": "US-ROUT-445566",
        "amount": 1200.00
    }
    print("Sending TechCorp transaction with Authorization Bearer Token...")
    r2 = requests.post(
        gateway_url, 
        json=techcorp_payload, 
        headers={"Authorization": f"Bearer {techcorp_token}"}
    )
    print(f"Gateway Response: {r2.json()}\n")

def verify_logical_isolation():
    print("--- 🔒 Verifying Database Isolation Boundaries ---")
    delta_records = db.fetch_tenant_ledger(tenant_id="tenant_delta")
    techcorp_records = db.fetch_tenant_ledger(tenant_id="tenant_techcorp")
    
    print(f"Delta Air Ledger Record Count: {len(delta_records)}")
    for record in delta_records:
        print(f"  [Delta Space] Found Transaction: {record['transaction_id']} | Amount: ${record['amount']} | Vendor: {record['vendor_name']}")
        
    print(f"\nTechCorp Solutions Ledger Record Count: {len(techcorp_records)}")
    for record in techcorp_records:
        print(f"  [TechCorp Space] Found Transaction: {record['transaction_id']} | Amount: ${record['amount']} | Vendor: {record['vendor_name']}")

if __name__ == "__main__":
    # Onboard and retrieve signing keys
    delta_token, tech_token = provision_mock_tenants_and_get_tokens()
    
    # Execute the live ingestion verify pipelines
    simulate_webhook_ingestion(delta_token, tech_token)
    verify_logical_isolation()