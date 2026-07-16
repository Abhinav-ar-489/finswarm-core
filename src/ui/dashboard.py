import streamlit as st
import duckdb
import pandas as pd
import os
import json
import io
from datetime import datetime
from src.database.graph_core import HeterogeneousFraudCore
from src.agents.compliance_swarm import ComplianceSwarm

# Import ReportLab modules for professional enterprise document layout
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

st.set_page_config(
    page_title="FinSwarm Intelligence | Enterprise Production Suite",
    page_icon="🛡️",
    layout="wide"
)

# Render professional corporate theme style grids
st.markdown("""
    <style>
    .metric-card { background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #3b82f6; }
    .metric-card-risk { background-color: #1e293b; padding: 20px; border-radius: 10px; border-left: 5px solid #ef4444; }
    </style>
""", unsafe_allow_html=True)

st.title("🛡️ FinSwarm Analytics Matrix")
st.subheader("Enterprise Multi-Entity Collusion & Forensic Risk Auditing Engine")
st.markdown("---")

DB_PATH = "data/processed/audit.db"

# =====================================================================
# 🛠️ HELPER ENGINE: GENERATE CERTIFIED PDF REPORT
# =====================================================================
def generate_compliance_pdf(report_data, cluster_id):
    """Compiles financial forensics cleanly into an official corporate PDF ledger."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40
    )
    
    styles = getSampleStyleSheet()
    
    # Custom Palette Typography
    title_style = ParagraphStyle(
        'DocTitle', parent=styles['Heading1'],
        fontSize=24, leading=28, textColor=colors.HexColor("#0f172a"), spaceAfter=12
    )
    section_style = ParagraphStyle(
        'SectionHeader', parent=styles['Heading2'],
        fontSize=14, leading=18, textColor=colors.HexColor("#1e3a8a"), spaceBefore=15, spaceAfter=8
    )
    body_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'],
        fontSize=10, leading=15, textColor=colors.HexColor("#334155")
    )
    alert_style = ParagraphStyle(
        'AlertText', parent=styles['Normal'],
        fontSize=11, leading=16, textColor=colors.HexColor("#991b1b"), fontName="Helvetica-Bold"
    )

    story = []
    
    # Document Header Band
    story.append(Paragraph("🛡️ FINSWARM CERTIFIED COMPLIANCE AUDIT", title_style))
    story.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC", body_style))
    story.append(Spacer(1, 15))
    
    # Metadata Segment Table
    metadata_data = [
        [Paragraph("<b>Target Entity / Cluster:</b>", body_style), Paragraph(report_data["vendor_investigated"], body_style)],
        [Paragraph("<b>Threat Vector Profile:</b>", body_style), Paragraph("MULTI_ENTITY_COLLUSION_RING", body_style)],
        [Paragraph("<b>Total Exposure Footprint:</b>", body_style), Paragraph(f"${report_data['total_capital_at_risk']:,.2f}", body_style)],
    ]
    t = Table(metadata_data, colWidths=[160, 360])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f8fafc")),
        ('PADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    story.append(t)
    story.append(Spacer(1, 15))
    
    # Watchlist Status Warning Bar
    story.append(Paragraph("🚨 REGULATORY COMPLIANCE WATCHLIST VERIFICATION", section_style))
    if report_data["regulatory_watchlist_breach"]:
        status_text = "⚠️ CRITICAL BREACH SHIELD TRIGGERED: Target parameters closely match global AML sanction tables."
        story.append(Paragraph(status_text, alert_style))
    else:
        story.append(Paragraph("✅ PASS: No immediate sanction markers identified.", body_style))
        
    story.append(Spacer(1, 15))
    
    # Executive Narrative Section
    story.append(Paragraph("📝 FORENSIC ANALYSIS SUMMARY NARRATIVE", section_style))
    story.append(Paragraph(report_data["forensic_summary_narrative"], body_style))
    story.append(Spacer(1, 15))
    
    # System Provenance Log Stack
    story.append(Paragraph("⛓️ ORCHESTRATION PROCESS PROVENANCE TRACE", section_style))
    for log in report_data["system_provenance_trail"]:
        story.append(Paragraph(f"• {log}", body_style))
        story.append(Spacer(1, 4))
        
    # Build Document
    doc.build(story)
    buffer.seek(0)
    return buffer

# =====================================================================
# 📥 DATA INGESTION GATEWAY TERMINAL
# =====================================================================
st.sidebar.header("📥 Data Management Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Corporate Ledger (CSV)", type=["csv"])

if uploaded_file is not None:
    with st.spinner("Ingesting corporate stream securely into cache..."):
        raw_save_path = os.path.join("data/raw", uploaded_file.name)
        os.makedirs(os.path.dirname(raw_save_path), exist_ok=True)
        with open(raw_save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        conn = duckdb.connect(DB_PATH)
        conn.execute(f"CREATE OR REPLACE TABLE ledger AS SELECT * FROM read_csv_auto('{raw_save_path}');")
        conn.close()
        st.sidebar.success("Data stream ingestion successful.")

# =====================================================================
# ⚙️ GOVERNANCE RISK POLICY CONFIGURATORS
# =====================================================================
st.sidebar.markdown("---")
st.sidebar.header("🛡️ Governance Risk Boundaries")
corporate_threshold = st.sidebar.slider("Aggregation Limit ($)", min_value=1000, max_value=25000, value=10000, step=500)
temporal_window = st.sidebar.slider("Temporal Scan Window (Mins)", min_value=5, max_value=120, value=30, step=5)

db_exists = os.path.exists(DB_PATH) and len(duckdb.connect(DB_PATH, read_only=True).execute("SHOW TABLES").fetchall()) > 0

if not db_exists:
    st.info("👋 FinSwarm Platform Ready. Please upload an enterprise CSV transactional ledger in the sidebar to engage live detection processing.")
else:
    conn = duckdb.connect(DB_PATH, read_only=True)
    total_transactions = conn.execute("SELECT COUNT(*) FROM ledger").fetchone()[0]
    total_volume = conn.execute("SELECT SUM(amount) FROM ledger").fetchone()[0] or 0.0
    conn.close()

    detector = HeterogeneousFraudCore(db_path=DB_PATH)
    detector.build_multi_entity_network()
    network_anomalies = detector.detect_collusion_rings(
        threshold=float(corporate_threshold), 
        time_window_mins=int(temporal_window)
    )

    unique_threats = len(network_anomalies)
    total_risk_capital = sum(a['amount'] for a in network_anomalies)

    # KPI Layout Cards
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"<div class='metric-card'><p style='color:#94a3b8; font-size:14px; margin:0;'>TOTAL RECORD STREAM</p><h2 style='color:#ffffff; margin:0;'>{total_transactions:,} rows</h2></div>", unsafe_allow_html=True)
    with col2:
        st.markdown(f"<div class='metric-card'><p style='color:#94a3b8; font-size:14px; margin:0;'>TOTAL CAPITAL MONITORED</p><h2 style='color:#ffffff; margin:0;'>${total_volume:,.2f}</h2></div>", unsafe_allow_html=True)
    with col3:
        st.markdown(f"<div class='metric-card-risk'><p style='color:#f87171; font-size:14px; margin:0;'>FLAGGED CAPITAL AT RISK</p><h2 style='color:#ef4444; margin:0;'>${total_risk_capital:,.2f}</h2></div>", unsafe_allow_html=True)
    with col4:
        st.markdown(f"<div class='metric-card-risk'><p style='color:#f87171; font-size:14px; margin:0;'>ACTIVE COLLUSION CLUSTERS</p><h2 style='color:#ef4444; margin:0;'>{unique_threats} clusters</h2></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.header("🔍 Topological Anomaly Control Console")

    if not network_anomalies:
        st.success("Network relational graph topology is fully stable. Zero cross-entity collusion networks identified.")
    else:
        df_anomalies = pd.DataFrame(network_anomalies)
        st.dataframe(df_anomalies[["anomaly_type", "vendor_name", "amount", "severity", "description"]].drop_duplicates(), use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.header("🤖 Multi-Agent Telemetry Synthesis Workspace")
        
        selected_index = st.selectbox(
            "Select active threat targets to route to Compliance Swarm:", 
            options=df_anomalies.index, 
            format_func=lambda x: f"Cluster #{x} - Risk Volume: ${df_anomalies.loc[x, 'amount']:,.2f}"
        )
        
        if st.button("🚀 Dispatch Compliance Swarm to Investigate Target"):
            match_data = df_anomalies.loc[selected_index].to_dict()
            
            try:
                swarm = ComplianceSwarm()
                with st.spinner("Orchestrating multi-agent compliance validation pipelines..."):
                    report = swarm.process_anomaly_packet(match_data)
                    
                    if report:
                        st.success("Cognitive analysis cleanly compiled.")
                        rep_col1, rep_col2 = st.columns([3, 2])
                        with rep_col1:
                            st.subheader("📝 Executive Summary Narrative")
                            st.info(report.executive_narrative)
                        with rep_col2:
                            st.subheader("🛡️ Regulatory Risk Markers")
                            st.error(f"AML Watchlist Verification: {'🚨 BREACH SHIELD TRIGGERED' if report.aml_sanction_match else 'PASS'}")
                            st.metric("Total Exposure Footprint", f"${report.total_amount_at_risk:,.2f}")
                            
                        st.markdown("<br>", unsafe_allow_html=True)
                        st.subheader("⛓️ Orchestrated Process Provenance Trace")
                        for trace in report.provenance_chain:
                            st.code(trace)
                            
                        # =====================================================================
                        # 📥 DUAL EXPORTER CONTROL MATRIX (JSON + PDF)
                        # =====================================================================
                        st.markdown("---")
                        st.subheader("📥 Export Certified Regulatory Compliance Packets")
                        
                        compliance_json = {
                            "vendor_investigated": report.vendor_name,
                            "threat_profile": "MULTI_ENTITY_COLLUSION_RING",
                            "total_capital_at_risk": report.total_amount_at_risk,
                            "regulatory_watchlist_breach": report.aml_sanction_match,
                            "forensic_summary_narrative": report.executive_narrative,
                            "system_provenance_trail": report.provenance_chain
                        }
                        
                        # Generate data formats
                        json_string = json.dumps(compliance_json, indent=4)
                        pdf_buffer = generate_compliance_pdf(compliance_json, selected_index)
                        
                        # Split UI layout elements into two clean side-by-side action points
                        exp_col1, exp_col2 = st.columns(2)
                        
                        with exp_col1:
                            st.download_button(
                                label="📄 Download Official Executive PDF",
                                data=pdf_buffer,
                                file_name=f"FINSWARM_AUDIT_REPORT_{selected_index}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                            
                        with exp_col2:
                            st.download_button(
                                label="⚙️ Download Raw Machine-Readable JSON",
                                data=json_string,
                                file_name=f"FINSWARM_AUDIT_DATA_{selected_index}.json",
                                mime="application/json",
                                use_container_width=True
                            )
            except ValueError as ve:
                st.error(f"Configuration Missing: {str(ve)}")