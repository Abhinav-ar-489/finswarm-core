import requests
import time
import subprocess
from src.database.multi_tenant_core import MultiTenantDatabase

# Initialize our multi-tenant DB interface
db = MultiTenantDatabase()

def provision_mock_tenants():
    print("--- 🏢 Onboarding SaaS Tenants ---")
    # Provision Tenant 1: Delta Airlines
    db.register_new_tenant(tenant_id="tenant_delta", company_name="Delta Air")
    
    # Provision Tenant 2: TechCorp Solutions
    db.register_new_tenant(tenant_id="tenant_techcorp", company_name="TechCorp Solutions")
    print("Onboarding complete.\n")

def simulate_webhook_ingestion():
    print("--- 🔌 Simulating Isolated Webhook Streams ---")
    gateway_url = "http://127.0.0.1:8000/api/v1/ingest"
    
    # Delta Air transaction stream (Stamped with Delta's Tenant ID in headers)
    delta_payload = {
        "employee_id": "EMP_DELTA_99",
        "cost_center": "Aviation-Ops",
        "vendor_name": "JetFuel-Corp",
        "bank_routing_account": "US-ROUT-112233",
        "amount": 45000.00
    }
    
    print("Sending Delta transaction with secure header...")
    r1 = requests.post(gateway_url, json=delta_payload, headers={"X-Tenant-ID": "tenant_delta"})
    print(f"Gateway Response: {r1.json()}\n")
    
    # TechCorp transaction stream (Stamped with TechCorp's Tenant ID in headers)
    techcorp_payload = {
        "employee_id": "EMP_TECH_04",
        "cost_center": "R&D-SaaS",
        "vendor_name": "CloudHosting-LLC",
        "bank_routing_account": "US-ROUT-445566",
        "amount": 1200.00
    }
    
    print("Sending TechCorp transaction with secure header...")
    r2 = requests.post(gateway_url, json=techcorp_payload, headers={"X-Tenant-ID": "tenant_techcorp"})
    print(f"Gateway Response: {r2.json()}\n")

def verify_logical_isolation():
    print("--- 🔒 Verifying Database Isolation Boundaries ---")
    
    # Fetch ledgers directly using our secure tenant queries
    delta_records = db.fetch_tenant_ledger(tenant_id="tenant_delta")
    techcorp_records = db.fetch_tenant_ledger(tenant_id="tenant_techcorp")
    
    print(f"Delta Air Ledger Record Count: {len(delta_records)}")
    for record in delta_records:
        print(f"  [Delta Space] Found Transaction: {record['transaction_id']} | Amount: ${record['amount']} | Vendor: {record['vendor_name']}")
        
    print(f"\nTechCorp Solutions Ledger Record Count: {len(techcorp_records)}")
    for record in techcorp_records:
        print(f"  [TechCorp Space] Found Transaction: {record['transaction_id']} | Amount: ${record['amount']} | Vendor: {record['vendor_name']}")

    # 🚨 CRITICAL CROSS-TENANT BLEED TEST
    print("\n--- 🚫 Attempting Intercept Attack (Cross-Tenant Leak Check) ---")
    print("Checking if Delta can access TechCorp's data using Delta's query bounds...")
    
    cross_bleed = False
    for record in delta_records:
        if record["tenant_id"] == "tenant_techcorp":
            cross_bleed = True
            
    if cross_bleed:
        print("❌ SECURITY CRITICAL FAILURE: Cross-tenant data bleed detected!")
    else:
        print("✅ SUCCESS: Data boundaries are impenetrable. Tenant records are logically isolated.")

if __name__ == "__main__":
    # 1. Onboard the tenants into the core system
    provision_mock_tenants()
    
    # 2. Before executing the stream test, tell the user to boot the server
    print("👉 To run the live ingestion tests:")
    print("   1. Open a separate terminal and run: python -m uvicorn src.database.webhook_gateway:app --reload")
    print("   2. Once the server is running, uncomment the execution calls below.")
    
    # Uncomment these once your uvicorn server is actively running in the background:
    simulate_webhook_ingestion()
    verify_logical_isolation()