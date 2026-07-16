import pandas as pd
import random
from datetime import datetime, timedelta
import os

def generate_production_test_data(output_path="data/raw/corporate_ledger.csv"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Establish base tracking arrays
    employees = [f"EMP_{1000 + i}" for i in range(15)]
    cost_centers = ["6040-IT", "5010-HR", "7020-MKTG", "4030-OPS", "8050-R&D"]
    vendors = ["Amazon Web Services", "Global Logistics Inc", "Staples Corp", "Oracle Utilities", "TechCorp Solutions", "Delta Air"]
    bank_accounts = [f"ACC_ROUTING_{77000 + i}" for i in range(len(vendors))]
    
    vendor_bank_map = dict(zip(vendors, bank_accounts))
    
    start_time = datetime(2026, 7, 1, 9, 0, 0)
    data = []

    # 1. Generate 2,000 normal operational transactions
    print("Generating baseline operational logs...")
    for i in range(2000):
        tx_id = f"TX_{100000 + i}"
        emp = random.choice(employees)
        cc = random.choice(cost_centers)
        vendor = random.choice(vendors)
        bank = vendor_bank_map[vendor]
        amount = round(random.uniform(50.0, 4500.0), 2)
        ts = start_time + timedelta(minutes=random.randint(1, 20000))
        
        data.append([tx_id, emp, cc, vendor, bank, amount, ts.isoformat()])

    # 2. Inject Level 1 Duplicate Billing Anomalies (Global Logistics Inc)
    print("Injecting Level 1 structural duplicates...")
    dup_ts = datetime(2026, 7, 10, 14, 30, 0)
    data.append(["TX_DUP_REG_01", "EMP_1002", "4030-OPS", "Global Logistics Inc", vendor_bank_map["Global Logistics Inc"], 8950.00, dup_ts.isoformat()])
    data.append(["TX_DUP_REG_02", "EMP_1002", "4030-OPS", "Global Logistics Inc", vendor_bank_map["Global Logistics Inc"], 8950.00, (dup_ts + timedelta(seconds=12)).isoformat()])

    # 3. Inject Level 2 Advanced Multi-Entity Collusion Ring (Targeting a shared bank account)
    print("Injecting Level 2 heterogeneous collusion ring...")
    collusion_bank = "ACC_ROUTING_SHARED_999"
    collusion_ts = datetime(2026, 7, 12, 11, 15, 0)
    
    # Three different employees paying three separate vendors within 10 minutes
    # All three vendors route their funds directly into the matching bank endpoint
    data.append(["TX_RING_01", "EMP_1005", "6040-IT", "TechCorp Solutions", collusion_bank, 4900.00, collusion_ts.isoformat()])
    data.append(["TX_RING_02", "EMP_1009", "7020-MKTG", "Oracle Utilities", collusion_bank, 4950.00, (collusion_ts + timedelta(minutes=4)).isoformat()])
    data.append(["TX_RING_03", "EMP_1012", "8050-R&D", "Delta Air", collusion_bank, 4800.00, (collusion_ts + timedelta(minutes=7)).isoformat()])

    # Compile dataset to disk
    df = pd.DataFrame(data, columns=["transaction_id", "employee_id", "cost_center", "vendor_name", "bank_routing_account", "amount", "timestamp"])
    df.to_csv(output_path, index=False)
    print(f"🎉 Production test environment generated successfully at: {output_path} ({len(df)} rows)")

if __name__ == "__main__":
    generate_production_test_data()