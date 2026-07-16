import json
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger("FinSwarmCore.AgentSwarm")

class SwarmOrchestrator:
    def __init__(self):
        self.system_ready = True
        
    def agent_profiler(self, employee_id: str) -> str:
        """Agent 1: Looks at the employee's historical behavior."""
        logger.info(f"🕵️‍♂️ [Agent 1: Profiler] Pulling HR and historical ledger data for {employee_id}...")
        time.sleep(1.2) # Simulate LLM thinking/API latency
        
        # In production, this agent queries the database and summarizes the results via an LLM.
        return f"Historical analysis indicates 0 prior offenses. This sudden structuring behavior is a severe behavioral anomaly."

    def agent_vendor_sleuth(self, vendor_name: str) -> str:
        """Agent 2: Investigates the destination company."""
        logger.info(f"🔎 [Agent 2: Vendor Sleuth] Scanning global registries and OFAC lists for '{vendor_name}'...")
        time.sleep(1.5)
        
        return f"WARNING: '{vendor_name}' was registered 14 days ago in a known offshore tax haven. High probability of being a shell entity."

    def agent_cco_synthesizer(self, incident_data: dict, profiler_report: str, vendor_report: str) -> dict:
        """Agent 3: The Chief Compliance Officer. Synthesizes everything into a final verdict."""
        logger.info(f"⚖️ [Agent 3: CCO Synthesizer] Compiling findings into executive dossier...")
        time.sleep(1.2)
        
        dossier = {
            "INCIDENT_TYPE": "Layering / Structuring Attack",
            "SEVERITY": "CRITICAL (98% Confidence)",
            "EXECUTIVE_SUMMARY": f"Employee {incident_data['employee_id']} successfully bypassed the $10,000 alert threshold by structuring {incident_data['transaction_count']} transactions totaling ${incident_data['cumulative_amount']:,.2f}.",
            "AGENT_1_PROFILER_NOTES": profiler_report,
            "AGENT_2_VENDOR_NOTES": vendor_report,
            "RECOMMENDED_ACTION": "Automatically freeze corporate card, halt pending outbound wires, and notify Delta Air HR."
        }
        return dossier

    def investigate_anomaly(self, flagged_cluster: dict) -> dict:
        """The main orchestration pipeline that routes the data between the swarm."""
        print(f"\n🚨 WAKING UP MICRO-AGENT SWARM FOR INCIDENT OVER ${flagged_cluster['cumulative_amount']:,.2f}...\n")
        
        # 1. Parallel Investigation Phase
        prof_report = self.agent_profiler(flagged_cluster['employee_id'])
        vend_report = self.agent_vendor_sleuth(flagged_cluster['vendor_name'])
        
        # 2. Synthesis Phase
        final_dossier = self.agent_cco_synthesizer(flagged_cluster, prof_report, vend_report)
        
        return final_dossier

if __name__ == "__main__":
    # --- Local Sandbox Test ---
    # We are mocking the exact JSON output your Smurfing Detector generated!
    test_incident = {
        "employee_id": "EMP_DELTA_007",
        "vendor_name": "Ghost-Corp-LLC",
        "cumulative_amount": 12000.0,
        "transaction_count": 3
    }
    
    swarm = SwarmOrchestrator()
    dossier = swarm.investigate_anomaly(test_incident)
    
    print("\n" + "="*50)
    print(" 🛑 FINAL EXECUTIVE DOSSIER GENERATED")
    print("="*50)
    print(json.dumps(dossier, indent=4))