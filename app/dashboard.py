import os
import sys
import streamlit as st
import pandas as pd
from sqlalchemy import text
import requests
from dotenv import load_dotenv

# Add project root directory to path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.development')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

from database.connection import engine, SessionLocal
from database.models import User, UserCohort, FrictionScore, RecoveryRecommendation
from models.recovery_generator import generate_llm_recommendation

st.set_page_config(
    page_title="UFIP | User Friction Intelligence",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Global styles */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Custom Banner */
    .header-banner {
        background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 50%, #2563eb 100%);
        padding: 35px 30px;
        border-radius: 16px;
        color: white;
        margin-bottom: 30px;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.25);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .header-title {
        font-size: 36px;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .header-subtitle {
        font-size: 16px;
        opacity: 0.85;
        margin-top: 8px;
    }
    
    /* Styled KPI Cards */
    .kpi-card {
        background: linear-gradient(135deg, #16171d 0%, #1e2029 100%);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
        margin-bottom: 20px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .kpi-card:hover {
        transform: translateY(-4px);
        border-color: rgba(124, 58, 237, 0.5);
    }
    .kpi-val {
        font-size: 38px;
        font-weight: 700;
        color: #ef4444;
        margin-bottom: 8px;
        line-height: 1;
    }
    .kpi-val-green {
        color: #10b981;
    }
    .kpi-val-purple {
        color: #8b5cf6;
    }
    .kpi-title {
        font-size: 12px;
        text-transform: uppercase;
        color: #94a3b8;
        letter-spacing: 1.2px;
        font-weight: 600;
    }
    
    /* Recommendations Box */
    .rec-box {
        background: linear-gradient(135deg, #1b1c24 0%, #111217 100%);
        border: 1px solid rgba(139, 92, 246, 0.25);
        border-left: 6px solid #8b5cf6;
        border-radius: 12px;
        padding: 22px;
        color: #f1f5f9;
        margin-bottom: 25px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.25);
    }

    /* Timeline Item Cards */
    .timeline-card {
        background-color: #181920;
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.15);
        border-left: 4px solid #2563eb;
    }
    .timeline-card-rage {
        border-left-color: #ef4444;
        background: linear-gradient(90deg, #1c1517 0%, #181920 100%);
    }
    .timeline-card-error {
        border-left-color: #f59e0b;
        background: linear-gradient(90deg, #1c1815 0%, #181920 100%);
    }
    .timeline-card-abandon {
        border-left-color: #ec4899;
        background: linear-gradient(90deg, #1c151a 0%, #181920 100%);
    }
    .timeline-card-slow {
        border-left-color: #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

# Helper function to check service status
def check_ollama_status():
    ollama_url = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
    try:
        res = requests.get(f"{ollama_url}/api/tags", timeout=1.0)
        if res.status_code == 200:
            return True, "Active"
    except Exception:
        pass
    return False, "Inactive"

def check_db_status():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True, "Connected"
    except Exception as e:
        return False, f"Disconnected ({type(e).__name__})"

# Database data load
def load_data():
    db = SessionLocal()
    try:
        # Check if v_user_features view exists
        features = pd.read_sql_query(text("SELECT * FROM v_user_features"), db.bind)
        scores = pd.read_sql_query(text("SELECT * FROM friction_scores"), db.bind)
        cohorts = pd.read_sql_query(text("SELECT * FROM user_cohorts"), db.bind)
        recs = pd.read_sql_query(text("SELECT * FROM recovery_recommendations"), db.bind)
        return features, scores, cohorts, recs
    except Exception as e:
        st.error(f"Error loading database details: {e}")
        return None, None, None, None
    finally:
        db.close()

# Sidebar Setup
st.sidebar.image("https://img.icons8.com/nolan/96/lightning-bolt.png", width=60)
st.sidebar.markdown("### **UFIP CONTROL CENTER**")
st.sidebar.markdown("---")

db_ok, db_msg = check_db_status()
ollama_ok, ollama_msg = check_ollama_status()

st.sidebar.markdown("#### **Services Status**")
if db_ok:
    st.sidebar.success(f"MySQL DB: {db_msg}")
else:
    st.sidebar.error(f"MySQL DB: {db_msg}")

if ollama_ok:
    st.sidebar.success(f"Ollama AI: {ollama_msg}")
else:
    st.sidebar.warning(f"Ollama AI: {ollama_msg} (Fallback Active)")

st.sidebar.markdown("---")
st.sidebar.markdown("#### **Parameters Configuration**")
friction_threshold = st.sidebar.slider(
    "Friction Alert Threshold:",
    min_value=10.0,
    max_value=90.0,
    value=40.0,
    step=5.0,
    help="Friction scores above this value will classify a user as At-Risk, requiring immediate recovery."
)

st.sidebar.markdown("---")
st.sidebar.markdown("`v0.1.0` | local mode")

# Header banner
st.markdown("""
<div class="header-banner">
    <div class="header-title">User Friction Intelligence Platform (UFIP)</div>
    <div class="header-subtitle">AI-powered customer behavior telemetry & automated revenue recovery console</div>
</div>
""", unsafe_allow_html=True)

# Main Dashboard Content
features_df, scores_df, cohorts_df, recs_df = load_data()

if features_df is None or len(features_df) == 0:
    st.info("👋 Welcome! The database is empty or schemas have not been initialized.")
    st.warning("Please run the Prefect pipeline first to seed simulated data, calculate scores, and generate cohorts.")
    
    if st.button("🚀 Initialize and Seed Database Now"):
        with st.spinner("Executing pipeline initialization (this runs schema initialization & seeds mock clickstreams)..."):
            from pipelines.etl_flow import ufip_etl_pipeline
            try:
                ufip_etl_pipeline()
                st.success("Pipeline executed successfully! Please reload the page.")
                st.rerun()
            except Exception as ex:
                st.error(f"Pipeline execution failed: {ex}")
else:
    # We have data! Let's build the tabs.
    tab1, tab2, tab3 = st.tabs(["📊 Cohort Analysis", "🔍 User Friction lookup", "⚙️ Control Panel"])
    
    # Pre-merge tables for easier analysis
    full_df = pd.merge(features_df, scores_df[['user_id', 'score']], on='user_id')
    full_df = pd.merge(full_df, cohorts_df[['user_id', 'cohort_label', 'cluster_id']], on='user_id')
    
    with tab1:
        st.markdown("### **User Cohorts & Friction Profiles**")
        
        # Row 1: KPI metrics cards
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val-purple kpi-val">{len(full_df)}</div>
                <div class="kpi-title">Total Monitored Users</div>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            avg_f = full_df['score'].mean()
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{avg_f:.1f}</div>
                <div class="kpi-title">Average Friction Score</div>
            </div>
            """, unsafe_allow_html=True)
        with col3:
            at_risk_count = len(full_df[full_df['score'] >= friction_threshold])
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val">{at_risk_count}</div>
                <div class="kpi-title">At-Risk Users (>= Threshold)</div>
            </div>
            """, unsafe_allow_html=True)
        with col4:
            happy_count = len(full_df[full_df['cohort_label'] == 'Happy Active Users'])
            st.markdown(f"""
            <div class="kpi-card">
                <div class="kpi-val-green kpi-val">{happy_count}</div>
                <div class="kpi-title">Happy Active Users</div>
            </div>
            """, unsafe_allow_html=True)
            
        # Row 2: Charts
        col_c1, col_c2 = st.columns([1, 1])
        with col_c1:
            st.markdown("#### Cohort Segment Sizes")
            cohort_counts = full_df['cohort_label'].value_counts().reset_index()
            cohort_counts.columns = ['Cohort', 'Users']
            st.bar_chart(data=cohort_counts, x='Cohort', y='Users', color='#a855f7')
            
        with col_c2:
            st.markdown("#### Friction Score Distribution by Cohort")
            cohort_scores = full_df.groupby('cohort_label')['score'].mean().reset_index()
            st.bar_chart(data=cohort_scores, x='cohort_label', y='score', color='#ff4b4b')
            
        # Table of Cohort Means
        st.markdown("#### **Cohort Average Feature Metrics**")
        cohort_summary = full_df.groupby('cohort_label')[['score', 'rage_clicks', 'error_count', 'avg_latency', 'checkout_abandoned']].mean()
        cohort_summary.rename(columns={
            'score': 'Avg Friction',
            'rage_clicks': 'Avg Rage Clicks',
            'error_count': 'Avg Errors',
            'avg_latency': 'Avg Latency (ms)',
            'checkout_abandoned': 'Checkout Abandon rate'
        }, inplace=True)
        st.dataframe(cohort_summary.style.format("{:.2f}").background_gradient(cmap="BuPu"), use_container_width=True)

    with tab2:
        st.markdown("### **User Search & Telemetry Analysis**")
        
        # User dropdown
        user_list = full_df['username'].tolist()
        selected_user = st.selectbox("Select User to Inspect:", user_list)
        
        user_row = full_df[full_df['username'] == selected_user].iloc[0]
        u_id = int(user_row['user_id'])
        
        # User details card
        col_u1, col_u2, col_u3, col_u4 = st.columns(4)
        with col_u1:
            st.metric("Friction Score", f"{user_row['score']}/100")
        with col_u2:
            st.metric("Behavior Cohort", user_row['cohort_label'])
        with col_u3:
            st.metric("Rage Clicks", int(user_row['rage_clicks']))
        with col_u4:
            st.metric("System Errors", int(user_row['error_count']))
            
        st.markdown("---")
        
        # Left column: Timeline; Right column: AI Recommendation
        col_lay1, col_lay2 = st.columns([1, 1])
        
        with col_lay1:
            st.markdown("#### **User Clickstream Timeline**")
            # Query session events
            db = SessionLocal()
            try:
                events_query = text("""
                    SELECT e.created_at, e.event_type, e.page, e.element, e.latency_ms, e.metadata_text 
                    FROM events e
                    JOIN sessions s ON e.session_id = s.id
                    WHERE s.user_id = :u_id
                    ORDER BY e.created_at ASC
                """)
                events_df = pd.read_sql_query(events_query, db.bind, params={"u_id": u_id})
                
                if len(events_df) == 0:
                    st.write("No events recorded for this user.")
                else:
                    for idx, row in events_df.iterrows():
                        time_str = pd.to_datetime(row['created_at']).strftime('%H:%M:%S')
                        etype = row['event_type']
                        
                        # Style event type
                        card_class = "timeline-card"
                        if etype == "rage_click":
                            card_class += " timeline-card-rage"
                            icon = "🔴 RAGE CLICK"
                        elif etype == "error":
                            card_class += " timeline-card-error"
                            icon = "⚠️ SYSTEM ERROR"
                        elif etype == "checkout_abandoned":
                            card_class += " timeline-card-abandon"
                            icon = "💸 CHECKOUT ABANDONED"
                        elif etype == "network_latency" and row['latency_ms'] > 1000:
                            card_class += " timeline-card-slow"
                            icon = "⏳ LATENCY ALERT"
                        else:
                            icon = "🔹 VIEW"
                            
                        element_part = f" on <code>{row['element']}</code>" if row['element'] else ""
                        latency_part = f" (<strong>{row['latency_ms']}ms</strong>)" if row['latency_ms'] > 0 else ""
                        meta_part = f"<br/><small style='color:#94a3b8;'>Details: {row['metadata_text']}</small>" if row['metadata_text'] else ""
                        
                        st.markdown(f"""
                        <div class="{card_class}">
                            <span style="color:#8b5cf6; font-weight:600;">[{time_str}]</span> 
                            <span style="font-weight:600;">{icon}</span> - {row['page']}{element_part}{latency_part}
                            {meta_part}
                        </div>
                        """, unsafe_allow_html=True)
            finally:
                db.close()
                
        with col_lay2:
            st.markdown("#### **AI Recovery Recommendation**")
            
            # Fetch recommendation from DB
            db = SessionLocal()
            try:
                rec_record = db.query(RecoveryRecommendation).filter(RecoveryRecommendation.user_id == u_id).first()
                
                if rec_record:
                    st.markdown(f"""
                    <div class="rec-box">
                        <strong>Status: {rec_record.status}</strong><br/><br/>
                        {rec_record.recommendation.replace(chr(10), '<br/>')}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.info("No pre-generated recovery recommendation found for this user (Friction Score is below threshold).")
                    
                # Option to regenerate on demand
                st.markdown("##### **On-Demand AI Recovery Action**")
                if st.button("⚡ Generate/Regenerate Recommendation"):
                    with st.spinner("Invoking local LLM server via Ollama..."):
                        # Query details
                        c_label = user_row['cohort_label']
                        score_val = float(user_row['score'])
                        rc = int(user_row['rage_clicks'])
                        ec = int(user_row['error_count'])
                        al = float(user_row['avg_latency'])
                        
                        new_rec = generate_llm_recommendation(c_label, score_val, rc, ec, al)
                        
                        # Save/update database
                        cohort_record = db.query(UserCohort).filter(UserCohort.user_id == u_id).first()
                        c_id = cohort_record.id if cohort_record else None
                        
                        if rec_record:
                            rec_record.recommendation = new_rec
                            rec_record.status = "Pending"
                        else:
                            rec_record = RecoveryRecommendation(
                                user_id=u_id,
                                cohort_id=c_id,
                                recommendation=new_rec,
                                status="Pending"
                            )
                            db.add(rec_record)
                        db.commit()
                        st.success("Recovery action generated by local AI!")
                        st.rerun()
            finally:
                db.close()
                
    with tab3:
        st.markdown("### **System Orchestration & Control Panel**")
        st.write("Trigger pipeline runs, configure thresholds, and view MLflow logging directories.")
        
        st.markdown("#### **Orchestration Runner**")
        if st.button("🏃 Run End-to-End Prefect ETL Flow"):
            with st.spinner("Orchestrating pipeline running database analysis, scoring, ML KMeans, and Ollama..."):
                from pipelines.etl_flow import ufip_etl_pipeline
                try:
                    ufip_etl_pipeline()
                    st.success("ETL Pipeline completed successfully! Relogged to MLflow.")
                    st.rerun()
                except Exception as ex:
                    st.error(f"Pipeline error: {ex}")
                    
        st.markdown("---")
        st.markdown("#### **MLflow Tracking Location**")
        st.code(f"MLflow Tracking URI: {os.getenv('MLFLOW_TRACKING_URI')}")
        st.write("To view model runs, run this command in your terminal:")
        st.code("mlflow server --host 127.0.0.1 --port 5001")
        st.write("Then open: `http://localhost:5001`")
