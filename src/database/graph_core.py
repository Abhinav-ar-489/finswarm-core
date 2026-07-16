import os
import duckdb
import networkx as nx
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("FinSwarmCore.GraphCore")

class HeterogeneousFraudCore:
    def __init__(self, db_path: str = "data/processed/audit.db"):
        self.db_path = db_path
        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Missing target database at: {db_path}. Please initialize the database first.")
        self.graph = nx.MultiDiGraph()

    def build_multi_entity_network(self):
        """Streams transactional rows into a heterogeneous graph network safely."""
        logger.info("Extracting transactional elements across shared read paths...")
        
        # Open in read-only mode to prevent parallel dashboard file locking conflicts
        conn = duckdb.connect(self.db_path, read_only=True)
        try:
            cursor = conn.execute("SELECT transaction_id, employee_id, cost_center, vendor_name, bank_routing_account, amount, timestamp FROM ledger")
            rows = cursor.fetchall()
        finally:
            conn.close()

        for row in rows:
            tx_id, emp_id, cost_ctr, vendor, bank_acc, amount, ts = row
            
            # Inject distinct entity node classes
            self.graph.add_node(emp_id, type="EMPLOYEE")
            self.graph.add_node(cost_ctr, type="COST_CENTER")
            self.graph.add_node(vendor, type="VENDOR")
            self.graph.add_node(bank_acc, type="BANK_ACCOUNT")

            ts_str = ts.isoformat() if hasattr(ts, 'isoformat') else str(ts)
            
            # Map structural flow pathways across the entity chains
            self.graph.add_edge(emp_id, cost_ctr, transaction_id=tx_id, amount=float(amount), timestamp=ts_str)
            self.graph.add_edge(cost_ctr, vendor, transaction_id=tx_id, amount=float(amount), timestamp=ts_str)
            self.graph.add_edge(vendor, bank_acc, transaction_id=tx_id, amount=float(amount), timestamp=ts_str)

        logger.info(f"Heterogeneous matrix generated: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges.")

    def detect_collusion_rings(self, threshold: float = 10000.0, time_window_mins: int = 30) -> list[dict]:
        """Traverses network paths to isolate multiple vendors routing money into matching banking endpoints."""
        flagged_alerts = []
        
        # Track targeted target bank account nodes
        bank_nodes = [n for n, attr in self.graph.nodes(data=True) if attr.get("type") == "BANK_ACCOUNT"]
        
        for bank in bank_nodes:
            in_edges = self.graph.in_edges(bank, data=True)
            if len(in_edges) < 2:
                continue
            
            tx_list = []
            for u, v, data in in_edges:
                tx_list.append({
                    "tx_id": data['transaction_id'],
                    "vendor": u,
                    "amount": data['amount'],
                    "timestamp": datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                })
            
            tx_list = sorted(tx_list, key=lambda x: x['timestamp'])
            
            # Sliding time-series window validation
            for i in range(len(tx_list)):
                cluster = [tx_list[i]]
                t1 = tx_list[i]['timestamp']
                
                for j in range(i + 1, len(tx_list)):
                    t2 = tx_list[j]['timestamp']
                    if (t2 - t1).total_seconds() / 60.0 <= time_window_mins:
                        cluster.append(tx_list[j])
                    else:
                        break
                
                total_cluster_value = sum(c['amount'] for c in cluster)
                if total_cluster_value >= threshold:
                    unique_vendors = set(c['vendor'] for c in cluster)
                    tx_ids = [c['tx_id'] for c in cluster]
                    
                    flagged_alerts.append({
                        "vendor_name": ", ".join(list(unique_vendors)),  # Format cleanly for compliance swarm matching
                        "amount": total_cluster_value,
                        "anomaly_type": "COLLUSION_RING",
                        "severity": "CRITICAL",
                        "description": f"Bank account terminal {bank} flagged for rapid routing aggregation totaling ${total_cluster_value:,.2f} from vendors {list(unique_vendors)} inside a {time_window_mins} min structural window. Linked Tx: {tx_ids}"
                    })
        return flagged_alerts