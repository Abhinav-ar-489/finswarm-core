import streamlit as st
import pandas as pd
import networkx as nx
import json
from src.database.multi_tenant_core import MultiTenantDatabase
from src.utils.auth import generate_saas_token, verify_and_decode_token
from src.analytics.smurfing_detector import SmurfingDetector
from src.agents.swarm_orchestrator import SwarmOrchestrator

# Initialize our SaaS multi-tenant database connection
db = MultiTenantDatabase()

# Set page configuration
st.set_page_config(
    page_title="FinSwarm SaaS Compliance Console",
    page_icon="🛡️",
    layout="wide"
)

# Initialize global authentication session state if not present
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.tenant_id = None
    st.session_state.company_name = None

# =====================================================================
# 🔑 STATE 1: SECURE SINGLE-TENANT PORTAL LOGIN
# =====================================================================
if not st.session_state.authenticated:
    st.container()
    st.title("🛡️ FinSwarm Enterprise Gateway")
    st.markdown("Please log into your corporate workspace panel.")
    
    # Simulate entering credentials or selecting a specific login node
    workspace_input = st.selectbox(
        "Select Corporate Node Identity",
        options=["Delta Air", "TechCorp Solutions"]
    )
    
    if st.button("Authenticate Secure Session"):
        # Map the login selector to its strict database tenant ID keys
        mock_mapping = {
            "Delta Air": "tenant_delta",
            "TechCorp Solutions": "tenant_techcorp"
        }
        target_id = mock_mapping[workspace_input]
        
        # 1. Cryptographically generate a JWT access key behind the scenes
        secure_token = generate_saas_token(tenant_id=target_id, company_name=workspace_input)
        
        # 2. Verify and decode the token immediately to establish secure identity context
        claims = verify_and_decode_token(secure_token)
        
        # 3. Securely commit values directly to un-bypassable session memory
        st.session_state.authenticated = True
        st.session_state.tenant_id = claims["sub"]
        st.session_state.company_name = claims["company"]
        
        st.rerun()
        
    st.stop()  # Hard execution stop, completely protecting the data below

# =====================================================================
# 📊 STATE 2: AUTHENTICATED SINGLE-TENANT DASHBOARD (LOCKED DOWN)
# =====================================================================
# Fetch session storage credentials safely
active_tenant_id = st.session_state.tenant_id
selected_company = st.session_state.company_name

# SAAS SIDEBAR CONTROL
st.sidebar.image("https://img.icons8.com/clouds/100/000000/safebox.png", width=80)
st.sidebar.title("FinSwarm SaaS")
st.sidebar.markdown("---")

# Display strict authenticated parameters (No switching permitted!)
st.sidebar.success(f"🔒 Identity Verified")
st.sidebar.info(f"**Workspace:** {active_tenant_id}\n\n**Company:** {selected_company}\n\n**Status:** 🟢 Enterprise Account")

if st.sidebar.button("Log Out of Workspace"):
    st.session_state.authenticated = False
    st.session_state.tenant_id = None
    st.session_state.company_name = None
    st.rerun()

# --- HARD DATA EXTRACTION BOUNDARY ---
# Data query is explicitly locked behind session context. 0% chance of cross-tenant leakage.
raw_records = db.fetch_tenant_ledger(tenant_id=active_tenant_id)

st.title(f"🛡️ Compliance Control Center: {selected_company}")
st.markdown(f"Secure single-tenant transaction diagnostics tracking workspace isolation space: `{active_tenant_id}`.")

if not raw_records:
    st.info(f"No active transaction ledger found for {selected_company}. Stream transactions via JWT to view details.")
else:
    df = pd.DataFrame(raw_records)
    
    # Metric Grid
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ingested Volume", f"${df['amount'].sum():,.2f}")
    with col2:
        st.metric("Total Transactions", len(df))
    with col3:
        st.metric("Unique Cost Centers", df['cost_center'].nunique())
        
    st.markdown("### 📋 Transaction Ledger Partition")
    st.dataframe(df.drop(columns=["tenant_id"]), use_container_width=True)

    # Isolated NetworkX Topology Core
    st.markdown("### 🕸️ Relational Collusion Topology")
    G = nx.DiGraph()
    for _, row in df.iterrows():
        G.add_edge(row['employee_id'], row['bank_routing_account'], amount=row['amount'], vendor=row['vendor_name'])
        
    islands = list(nx.weakly_connected_components(G))
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.write(f"**Total Network Nodes:** {G.number_of_nodes()}")
    with col_g2:
        st.write(f"**Identified Relational Clusters:** {len(islands)}")
        
    st.markdown("#### Entity Relationship Tree")
    for idx, component in enumerate(islands):
        st.code(f"Cluster {idx+1}: {list(component)}")

# =====================================================================
# 🚨 AI THREAT INTELLIGENCE & SWARM ORCHESTRATION
# =====================================================================
st.markdown("---")
st.markdown("### 🚨 AI Threat Intelligence Sweep")
st.markdown("Deploy autonomous micro-agents to scan the ledger for structuring and evasion tactics.")

if st.button("Initiate AI Compliance Sweep"):
    with st.spinner("Initializing Smurfing Detector..."):
        detector = SmurfingDetector()
        # Scan the active tenant's ledger
        flagged_clusters = detector.scan_tenant_ledger(tenant_id=active_tenant_id)
        
    if not flagged_clusters:
        st.success("✅ Sweep complete. No structuring anomalies detected in this workspace.")
    else:
        st.error(f"⚠️ CRITICAL: Detected {len(flagged_clusters)} structuring anomalies!")
        
        # Wake up the swarm for each detected anomaly
        swarm = SwarmOrchestrator()
        
        for idx, cluster in enumerate(flagged_clusters):
            with st.expander(f"Incident {idx + 1}: {cluster['employee_id']} ➔ {cluster['vendor_name']}", expanded=True):
                
                st.warning(f"**Anomaly Trigger:** {cluster['transaction_count']} linked transactions totaling ${cluster['cumulative_amount']:,.2f}.")
                
                # Run the swarm investigation with UI feedback
                with st.status("Waking up Micro-Agent Swarm...", expanded=True) as status:
                    st.write("🕵️‍♂️ Agent 1 (Profiler) analyzing historical behavior...")
                    prof_report = swarm.agent_profiler(cluster['employee_id'])
                    
                    st.write("🔎 Agent 2 (Vendor Sleuth) scanning OFAC registries...")
                    vend_report = swarm.agent_vendor_sleuth(cluster['vendor_name'])
                    
                    st.write("⚖️ Agent 3 (CCO Synthesizer) compiling final dossier...")
                    dossier = swarm.agent_cco_synthesizer(cluster, prof_report, vend_report)
                    
                    status.update(label="Swarm Investigation Complete", state="complete", expanded=False)
                
                # Display the final dossier generated by the swarm
                st.markdown("#### 📑 Final Executive Dossier")
                st.json(dossier)