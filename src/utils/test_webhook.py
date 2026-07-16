import urllib.request
import json
import time

def send_mock_webhook(payload):
    url = "http://127.0.0.1:8000/webhook/v1/ingest"
    req = urllib.request.Request(url, method="POST")
    req.add_header("Content-Type", "application/json")
    
    data = json.dumps(payload).encode("utf-8")
    
    try:
        with urllib.request.urlopen(req, data=data) as response:
            res_body = response.read().decode("utf-8")
            print(f"📡 Response Code {response.status}: {res_body}")
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP Error {e.code}: {e.read().decode('utf-8')}")

if __name__ == "__main__":
    print("🚀 Firing real-time collusion packet into FinSwarm Gateway...")
    
    # We will simulate three distinct transactions hitting the same bank routing account 
    # within seconds of each other to simulate a threshold-circumvention ring
    timestamp_base = "2026-07-15T21:30:"
    
    tx1 = {
        "transaction_id": "TX_STREAM_901",
        "employee_id": "EMP_3001",
        "cost_center": "6040-IT",
        "vendor_name": "CloudAlpha Corp",
        "bank_routing_account": "ACC_WEBHOOK_RING_888",
        "amount": 4900.00,
        "timestamp": f"{timestamp_base}01"
    }
    
    tx2 = {
        "transaction_id": "TX_STREAM_902",
        "employee_id": "EMP_3004",
        "cost_center": "4030-OPS",
        "vendor_name": "BetaSupply LLC",
        "bank_routing_account": "ACC_WEBHOOK_RING_888",
        "amount": 4950.00,
        "timestamp": f"{timestamp_base}15"
    }

    send_mock_webhook(tx1)
    time.sleep(1) # Small gap between requests
    send_mock_webhook(tx2)