import streamlit as st
import pandas as pd
import networkx as nx
from src.database.multi_tenant_core import MultiTenantDatabase

# Initialize our SaaS multi-tenant database connection
db = MultiTenantDatabase()

# Set page configuration
st.set_page_config(
    page_title="FinSwarm SaaS Compliance Console",
    page_icon="🛡️",
    layout="wide"
)

# =====================================================================
# 🔒 SAAS SIDEBAR: WORKSPACE TENANT SELECTOR
# =====================================================================
st.sidebar.image("https://img.icons8.com/clouds/100/000000/safebox.png", width=80)
st.sidebar.title("FinSwarm SaaS")
st.sidebar.markdown("---")

# Fetch all registered tenants dynamically to simulate a tenant login session
conn = db._get_connection()
cursor = conn.cursor()
cursor.execute("SELECT tenant_id, company_name FROM tenants")
tenants_list = cursor.fetchall()
conn.close()

if not tenants_list:
    st.sidebar.warning("No active tenants found. Please run test_saas_isolation.py first to provision tenants.")
    st.stop()

# Build dictionary for clean UI display
tenant_map = {name: tid for tid, name in tenants_list}
selected_company = st.sidebar.selectbox(
    "🔑 Active Workspace",
    options=list(tenant_map.keys())
)
active_tenant_id = tenant_map[selected_company]

# Display authenticated tenant parameters
st.sidebar.info(f"**Workspace:** {active_tenant_id}\n\n**Status:** 🟢 Active Subscription")

# =====================================================================
# 📊 DYNAMIC DATA EXTRACTION & ANALYSIS PIPELINE
# =====================================================================
# Read ledger entries isolated ONLY under this tenant_id
raw_records = db.fetch_tenant_ledger(tenant_id=active_tenant_id)

st.title(f"🛡️ Compliance Control Center: {selected_company}")
st.markdown("Real-time transactional forensics, network graph analysis, and multi-agent compliance pipelines.")

if not raw_records:
    st.info(f"No active transaction ledger found for {selected_company}. Stream some transactions using JWT tokens first!")
else:
    # Convert records to DataFrame for analytics views
    df = pd.DataFrame(raw_records)
    
    # Show high-level metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Ingested Volume", f"${df['amount'].sum():,.2f}")
    with col2:
        st.metric("Total Transactions", len(df))
    with col3:
        st.metric("Unique Cost Centers", df['cost_center'].nunique())
        
    st.markdown("### 📋 Transaction Ledger Partition")
    st.dataframe(df.drop(columns=["tenant_id"]), use_container_width=True)

    # =====================================================================
    # 🧠 DYNAMIC GRAPH CORE BUILDING (Isolated NetworkX)
    # =====================================================================
    st.markdown("### 🕸️ Relational Collusion Topology")
    
    # Initialize a clean, local Graph for this tenant
    G = nx.DiGraph()
    
    for _, row in df.iterrows():
        # Build relationship: Employee -> Bank Routing Account
        G.add_edge(
            row['employee_id'], 
            row['bank_routing_account'], 
            amount=row['amount'], 
            vendor=row['vendor_name']
        )
        
    # Analyze Graph properties for this specific tenant's network
    islands = list(nx.weakly_connected_components(G))
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        st.write(f"**Total Network Nodes (Entities):** {G.number_of_nodes()}")
        st.write(f"**Total Direct Edges (Relationships):** {G.number_of_edges()}")
    with col_g2:
        st.write(f"**Identified Relational Clusters (Islands):** {len(islands)}")
        
    # Draw simple textual topological tree
    st.markdown("#### Entity Relationship Tree")
    for idx, component in enumerate(islands):
        st.code(f"Cluster {idx+1}: {list(component)}")

    # =====================================================================
    # 📤 BOARDROOM-READY DUAL EXPORTER
    # =====================================================================
    st.markdown("---")
    st.markdown("### 📥 Compliance Packet Exporters")
    
    # Build clean JSON download payload representing this tenant's isolated state
    json_data = df.to_json(orient="records", indent=4)
    st.download_button(
        label="Download Compliance JSON Audit Ledger",
        data=json_data,
        file_name=f"compliance_audit_{active_tenant_id}.json",
        mime="application/json"
    )