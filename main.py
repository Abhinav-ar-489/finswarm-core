import os
import sys
import subprocess

def main():
    print("=" * 60)
    print("🛡️  WELCOME TO FINSWARM ENGINE LAUNCHER")
    print("=" * 60)
    print("1. Run Full Analytical Pipeline Core (Terminal Output Only)")
    print("2. Launch Enterprise SaaS UI Analytics Dashboard")
    print("=" * 60)
    
    choice = input("Select an execution mode (1 or 2): ").strip()
    
    if choice == "1":
        # Import internally to trigger the terminal pipeline execution we verified earlier
        from src.database.duckdb_core import DuckDBEngine
        from src.database.graph_core import GraphFraudCore
        from src.agents.compliance_swarm import ComplianceSwarm
        
        print("\n⚡ Running core processing engines...")
        # (This runs the pipeline logic we established in main previously)
        db_engine = DuckDBEngine()
        try:
            db_engine.ingest_raw_ledger()
            math_anomalies = db_engine.run_mathematical_audit()
        finally:
            db_engine.close()
            
        graph_engine = GraphFraudCore()
        graph_engine.build_transaction_network()
        network_anomalies = graph_engine.detect_threshold_splitting()
        
        print(f"\n[Engine Stats] Logged {len(math_anomalies)} duplicate bills and {len(network_anomalies)} relational splits.")
        
    elif choice == "2":
        print("\n🖥️  Spinning up local web interface dashboard server...")
        # Triggers the Streamlit subprocess execution shell automatically
        subprocess.run(["py", "-m", "streamlit", "run", "src/ui/dashboard.py"])
    else:
        print("❌ Invalid selection. Exiting launcher.")

if __name__ == "__main__":
    main()