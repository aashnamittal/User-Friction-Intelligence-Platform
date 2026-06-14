import os
import sys
import streamlit as st
import pandas as pd
from sqlalchemy import text
import requests
from dotenv import load_dotenv

# Add project root directory to path for module resolution
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Load env file
dotenv_path = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), ".env.development"
)
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

from database.connection import engine, SessionLocal
from database.models import User, UserCohort, FrictionScore, RecoveryRecommendation
from models.recovery_generator import generate_llm_recommendation

st.set_page_config(
    page_title="UFIP | User Experience Hub",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Premium CSS with CSS Theme Variables (supports Light & Dark Modes)
st.markdown(
    """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap');
    
    /* Global Overrides */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Theme-Adaptive Cards */
    .glass-card {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        color: var(--text-color) !important;
    }
    
    .glass-card-header {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 15px;
        color: var(--text-color) !important;
        border-bottom: 1px solid rgba(128, 128, 128, 0.15) !important;
        padding-bottom: 10px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    /* Header Banner with animated gradient */
    .header-banner {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 50%, #ec4899 100%);
        background-size: 200% 200%;
        animation: gradientShift 10s ease infinite;
        padding: 30px;
        border-radius: 20px;
        color: white !important;
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(168, 85, 247, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.15);
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    .header-title {
        font-size: 32px;
        font-weight: 800;
        margin: 0;
        letter-spacing: -0.5px;
        color: white !important;
    }
    .header-subtitle {
        font-size: 15px;
        opacity: 0.9;
        margin-top: 6px;
        font-weight: 300;
        color: white !important;
    }
    
    /* Secondary (Inactive) Tabs styling */
    div[data-testid="stBaseButton-secondary"] button {
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        color: var(--text-color) !important;
        opacity: 0.85;
        padding: 12px 20px !important;
        font-weight: 600 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05) !important;
        transition: all 0.3s ease !important;
        height: 52px !important;
    }
    div[data-testid="stBaseButton-secondary"] button:hover {
        border-color: var(--primary-color) !important;
        color: var(--text-color) !important;
        opacity: 1 !important;
    }

    /* Primary (Active) Tabs styling */
    div[data-testid="stBaseButton-primary"] button {
        background: var(--primary-color) !important;
        border: 1px solid var(--primary-color) !important;
        border-radius: 12px !important;
        color: white !important; /* Always white for high contrast on active theme color */
        padding: 12px 20px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
        height: 52px !important;
    }
    
    /* Custom Timeline Speech Bubbles */
    .speech-bubble {
        position: relative;
        background: var(--secondary-background-color) !important;
        border: 1px solid rgba(128, 128, 128, 0.15) !important;
        border-radius: 14px;
        padding: 16px;
        margin-bottom: 12px;
        margin-left: 20px;
        border-left: 4px solid #6366f1 !important;
        color: var(--text-color) !important;
    }
    .speech-bubble::before {
        content: '';
        position: absolute;
        left: -8px;
        top: 20px;
        width: 0;
        height: 0;
        border-top: 8px solid transparent;
        border-bottom: 8px solid transparent;
        border-right: 8px solid var(--secondary-background-color) !important;
    }
    
    .bubble-rage {
        border-left-color: #ef4444 !important;
        background: rgba(239, 68, 68, 0.07) !important;
    }
    .bubble-error {
        border-left-color: #f59e0b !important;
        background: rgba(245, 158, 11, 0.07) !important;
    }
    .bubble-abandon {
        border-left-color: #ec4899 !important;
        background: rgba(236, 72, 153, 0.07) !important;
    }
    .bubble-slow {
        border-left-color: #3b82f6 !important;
        background: rgba(59, 130, 246, 0.07) !important;
    }
    
    /* Empathy Alert Box */
    .empathy-indicator {
        padding: 12px 16px;
        border-radius: 10px;
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .empathy-green {
        background: rgba(16, 185, 129, 0.1);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .empathy-amber {
        background: rgba(245, 158, 11, 0.1);
        color: #d97706;
        border: 1px solid rgba(245, 158, 11, 0.25);
    }
    .empathy-red {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }
    
    /* Email Copy block container */
    .email-container {
        background: #1e293b !important;
        border: 1px dashed rgba(168, 85, 247, 0.3);
        border-radius: 12px;
        padding: 20px;
        font-family: monospace;
        color: #f8fafc !important;
        margin-bottom: 15px;
        font-size: 14px;
        white-space: pre-wrap;
    }
    
    /* Large KPI Stat Blocks */
    .stat-val {
        font-size: 36px;
        font-weight: 800;
        letter-spacing: -1px;
        line-height: 1;
        margin-bottom: 5px;
    }
    .stat-desc {
        font-size: 12px;
        color: var(--text-color) !important;
        opacity: 0.7;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""",
    unsafe_allow_html=True,
)


# Helper functions for service checking
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


# Database data loading
def load_data():
    db = SessionLocal()
    try:
        features = pd.read_sql_query(text("SELECT * FROM v_user_features"), db.bind)
        scores = pd.read_sql_query(text("SELECT * FROM friction_scores"), db.bind)
        cohorts = pd.read_sql_query(text("SELECT * FROM user_cohorts"), db.bind)
        recs = pd.read_sql_query(
            text("SELECT * FROM recovery_recommendations"), db.bind
        )
        return features, scores, cohorts, recs
    except Exception as e:
        st.error(f"Error loading database details: {e}")
        return None, None, None, None
    finally:
        db.close()


# Sidebar Setup
st.sidebar.image("https://img.icons8.com/nolan/96/lightning-bolt.png", width=65)
st.sidebar.markdown("### **UFIP ORCHESTRATION**")
st.sidebar.markdown("---")


# Stage change callback to safely modify widget session state before rendering
def set_stage(target_stage):
    st.session_state.sidebar_stage_radio = target_stage


# Navigation representing the story funnel
if "sidebar_stage_radio" not in st.session_state:
    st.session_state.sidebar_stage_radio = "📡 Ingestion & Telemetry Feed"

stage_options = [
    "📡 Ingestion & Telemetry Feed",
    "👤 Customer Empathy Space",
    "📊 Cohort & Metrics Analytics",
    "🎛️ Engine Control Room",
]

# Ensure the state has a valid selection
if st.session_state.sidebar_stage_radio not in stage_options:
    st.session_state.sidebar_stage_radio = "📡 Ingestion & Telemetry Feed"

st.sidebar.markdown("##### **Story-Driven Funnel**")
# Bind the radio selector to st.session_state.sidebar_stage_radio
stage = st.sidebar.radio(
    "Select Stage of Investigation:",
    options=stage_options,
    key="sidebar_stage_radio",
)

st.sidebar.markdown("---")

# Alert config slider
friction_threshold = st.sidebar.slider(
    "Friction Action Threshold:",
    min_value=10.0,
    max_value=90.0,
    value=30.0,
    step=5.0,
    help="Scores at/above this value flag a user as At-Risk, generating automated recovery plans.",
)

st.sidebar.markdown("---")
db_ok, db_msg = check_db_status()
ollama_ok, ollama_msg = check_ollama_status()
st.sidebar.markdown("##### **Engine Health**")
if db_ok:
    st.sidebar.success(f"MySQL: {db_msg}")
else:
    st.sidebar.error(f"MySQL: {db_msg}")

if ollama_ok:
    st.sidebar.success(f"Ollama: {ollama_msg}")
else:
    st.sidebar.warning(f"Ollama: {ollama_msg} (Templates Active)")

# Header Banner
st.markdown(
    """
<div class="header-banner">
    <div class="header-title">User Friction Intelligence Platform (UFIP)</div>
    <div class="header-subtitle">Empathetic Telemetry Analytics & AI-Driven Customer Recovery Interface</div>
</div>
""",
    unsafe_allow_html=True,
)

# Render Visual Funnel Progress Bar as Clickable Tabs
col_tab1, col_tab2, col_tab3, col_tab4 = st.columns(4)

with col_tab1:
    st.button(
        "📡 1. Live Telemetry Ingestion",
        type="primary" if stage == "📡 Ingestion & Telemetry Feed" else "secondary",
        use_container_width=True,
        key="btn_stage_1",
        on_click=set_stage,
        args=("📡 Ingestion & Telemetry Feed",),
    )

with col_tab2:
    st.button(
        "👤 2. Experience Empathy (User Stories)",
        type="primary" if stage == "👤 Customer Empathy Space" else "secondary",
        use_container_width=True,
        key="btn_stage_2",
        on_click=set_stage,
        args=("👤 Customer Empathy Space",),
    )

with col_tab3:
    st.button(
        "📊 3. Cohort & Metrics Analytics",
        type="primary" if stage == "📊 Cohort & Metrics Analytics" else "secondary",
        use_container_width=True,
        key="btn_stage_3",
        on_click=set_stage,
        args=("📊 Cohort & Metrics Analytics",),
    )

with col_tab4:
    st.button(
        "🎛️ 4. Engine Control Room",
        type="primary" if stage == "🎛️ Engine Control Room" else "secondary",
        use_container_width=True,
        key="btn_stage_4",
        on_click=set_stage,
        args=("🎛️ Engine Control Room",),
    )

# Load data
features_df, scores_df, cohorts_df, recs_df = load_data()

if features_df is None or len(features_df) == 0:
    st.info("👋 Welcome! The database is empty or schemas have not been initialized.")
    st.warning(
        "Please run the Prefect pipeline first to seed simulated data, calculate scores, and generate cohorts."
    )

    if st.button("🚀 Initialize and Seed Database Now"):
        with st.spinner(
            "Executing pipeline initialization (this runs schema initialization & seeds mock clickstreams)..."
        ):
            from pipelines.etl_flow import ufip_etl_pipeline

            try:
                ufip_etl_pipeline()
                st.success("Pipeline executed successfully! Please reload the page.")
                st.rerun()
            except Exception as ex:
                st.error(f"Pipeline execution failed: {ex}")
else:
    # Pre-merge tables for easier use
    full_df = pd.merge(features_df, scores_df[["user_id", "score"]], on="user_id")
    full_df = pd.merge(
        full_df, cohorts_df[["user_id", "cohort_label", "cluster_id"]], on="user_id"
    )

    # ==================== STAGE 1: INGESTION & TELEMETRY FEED ====================
    if stage == "📡 Ingestion & Telemetry Feed":
        st.markdown("### **📡 Stage 1: Live Telemetry Ingestion Feed**")
        st.write(
            "This workspace represents the ingestion of raw customer event feeds. Clicks, latency events, and checkout logs stream directly into MySQL."
        )

        # Ingestion metrics
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(
                """
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color: #6366f1;">{:0,d}</div>
                <div class="stat-desc">Total Ingested Events</div>
            </div>
            """.format(int(features_df["total_events"].sum())),
                unsafe_allow_html=True,
            )
        with col_m2:
            st.markdown(
                """
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color: #a855f7;">{:0,d}</div>
                <div class="stat-desc">Monitored User Sessions</div>
            </div>
            """.format(int(features_df["total_sessions"].sum())),
                unsafe_allow_html=True,
            )
        with col_m3:
            avg_rc = features_df["rage_clicks"].mean()
            st.markdown(
                """
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color: #ef4444;">{:.1f}</div>
                <div class="stat-desc">Average Rage Clicks / User</div>
            </div>
            """.format(avg_rc),
                unsafe_allow_html=True,
            )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Real-time event log
        st.markdown("#### **Real-time Event Log (Latest 50 Telemetry Signals)**")

        # Filters for telemetry log
        filter_col1, filter_col2 = st.columns(2)
        db = SessionLocal()
        try:
            event_types_query = text("SELECT DISTINCT event_type FROM events")
            event_types = [r[0] for r in db.execute(event_types_query).fetchall()]

            with filter_col1:
                selected_event_type = st.multiselect(
                    "Filter by Event Type:", event_types, default=event_types
                )
            with filter_col2:
                search_user = st.text_input("Filter by Username:")

            # Build query
            where_clauses = []
            params = {}
            if selected_event_type:
                where_clauses.append("e.event_type IN :etypes")
                params["etypes"] = tuple(selected_event_type)
            if search_user:
                where_clauses.append("u.username LIKE :uname")
                params["uname"] = f"%{search_user}%"

            where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            logs_query = text(f"""
                SELECT e.created_at, u.username, e.event_type, e.page, e.element, e.latency_ms, e.metadata_text
                FROM events e
                JOIN sessions s ON e.session_id = s.id
                JOIN users u ON s.user_id = u.id
                {where_str}
                ORDER BY e.created_at DESC
                LIMIT 50
            """)

            logs_df = pd.read_sql_query(logs_query, db.bind, params=params)

            if len(logs_df) == 0:
                st.info("No matching telemetry events found in the database.")
            else:
                # Format latency column to look cleaner
                logs_df["latency_ms"] = logs_df["latency_ms"].apply(
                    lambda x: f"{x}ms" if x > 0 else "-"
                )
                logs_df.rename(
                    columns={
                        "created_at": "Timestamp",
                        "username": "Username",
                        "event_type": "Event Type",
                        "page": "Page Route",
                        "element": "UI Element",
                        "latency_ms": "Latency",
                        "metadata_text": "System Logs / Metadata",
                    },
                    inplace=True,
                )

                st.dataframe(logs_df, use_container_width=True)
        finally:
            db.close()

    # ==================== STAGE 2: CUSTOMER EMPATHY WORKSPACE ====================
    elif stage == "👤 Customer Empathy Space":
        st.markdown("### **👤 Stage 2: Customer Empathy Workspace (User Experiences)**")
        st.write(
            "This workspace focuses entirely on the **human customer journey**. It isolates the user experience, showing chronological storylines, emotional meters, and active recovery draft campaigns."
        )

        # Dropdown selection of user stories
        user_list = full_df["username"].tolist()

        # Highlight users above threshold in dropdown list to guide operator
        user_display_list = []
        for uname in user_list:
            u_row = full_df[full_df["username"] == uname].iloc[0]
            if u_row["score"] >= friction_threshold:
                user_display_list.append(f"🔴 {uname} (Friction: {u_row['score']:.0f})")
            else:
                user_display_list.append(f"🟢 {uname} (Friction: {u_row['score']:.0f})")

        selected_display = st.selectbox(
            "Select Customer Profile to Inspect:", user_display_list
        )
        selected_user = selected_display.split(" ")[1]  # Extract username

        user_row = full_df[full_df["username"] == selected_user].iloc[0]
        u_id = int(user_row["user_id"])
        score_val = float(user_row["score"])
        cohort_label = user_row["cohort_label"]

        st.markdown("<br/>", unsafe_allow_html=True)

        # Columns: Left (User Story & Emotional Card) | Right (AI Copywriter)
        col_emp1, col_emp2 = st.columns([1.1, 0.9])

        with col_emp1:
            st.markdown(
                f"""
            <div class="glass-card">
                <div class="glass-card-header">👤 Customer Empathy Card: {selected_user}</div>
            """,
                unsafe_allow_html=True,
            )

            # Empathy health bar / status indicator
            if score_val < 30.0:
                st.markdown(
                    """
                <div class="empathy-indicator empathy-green">
                    <span>🟢</span> <strong>Friction Score: {:.1f}/100 - Smooth Experience</strong>
                </div>
                """.format(score_val),
                    unsafe_allow_html=True,
                )
            elif score_val < 60.0:
                st.markdown(
                    """
                <div class="empathy-indicator empathy-amber">
                    <span>🟡</span> <strong>Friction Score: {:.1f}/100 - Moderate Sluggishness (At-Risk)</strong>
                </div>
                """.format(score_val),
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                <div class="empathy-indicator empathy-red">
                    <span>🔴</span> <strong>Friction Score: {:.1f}/100 - Severe Roadblock (Critical)</strong>
                </div>
                """.format(score_val),
                    unsafe_allow_html=True,
                )

            # Render user metrics metadata
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.write(f"**Cohort Profile:**\n`{cohort_label}`")
            with m_col2:
                st.write(f"**Rage Clicks:** `{int(user_row['rage_clicks'])}`")
            with m_col3:
                st.write(f"**System Errors:** `{int(user_row['error_count'])}`")

            st.markdown("</div>", unsafe_allow_html=True)

            # The Customer Story (Timeline)
            st.markdown("#### **The Customer's Experience Story**")

            db = SessionLocal()
            try:
                events_query = text("""
                    SELECT e.created_at, e.event_type, e.page, e.element, e.latency_ms, e.metadata_text 
                    FROM events e
                    JOIN sessions s ON e.session_id = s.id
                    WHERE s.user_id = :u_id
                    ORDER BY e.created_at ASC
                """)
                events_df = pd.read_sql_query(
                    events_query, db.bind, params={"u_id": u_id}
                )

                if len(events_df) == 0:
                    st.write("No session records found for this user.")
                else:
                    for idx, row in events_df.iterrows():
                        time_str = pd.to_datetime(row["created_at"]).strftime(
                            "%H:%M:%S"
                        )
                        etype = row["event_type"]
                        page = row["page"]
                        element = row["element"]
                        latency = row["latency_ms"]
                        meta = row["metadata_text"]

                        # Translate raw database events into human-centric narrative lines
                        if etype == "page_view":
                            bubble_class = "speech-bubble"
                            description = f"Opened page <strong>{page}</strong>."
                        elif etype == "click":
                            bubble_class = "speech-bubble"
                            description = f"Clicked element <code>{element}</code> on page <strong>{page}</strong>."
                        elif etype == "network_latency":
                            if latency > 1500:
                                bubble_class = "speech-bubble bubble-slow"
                                description = f"⏳ <strong>Sluggish Network Alert:</strong> Suffered major page connection delay of <strong>{latency}ms</strong> on <strong>{page}</strong>."
                            else:
                                bubble_class = "speech-bubble"
                                description = f"Normal connection delay of {latency}ms."
                        elif etype == "rage_click":
                            bubble_class = "speech-bubble bubble-rage"
                            description = f"🔴 <strong>Rage Clicks:</strong> Repeatedly smashed click on <code>{element}</code> on page <strong>{page}</strong> out of frustration."
                        elif etype == "error":
                            bubble_class = "speech-bubble bubble-error"
                            description = f"⚠️ <strong>System Error Event:</strong> Form block or script crashed on <code>{element}</code> on page <strong>{page}</strong>. Error message: <em>{meta}</em>"
                        elif etype == "checkout_abandoned":
                            bubble_class = "speech-bubble bubble-abandon"
                            description = f"💸 <strong>Checkout Abandoned:</strong> Quit the order process entirely at <strong>{page}</strong> without purchasing due to errors."
                        else:
                            bubble_class = "speech-bubble"
                            description = f"Event: {etype} on {page}."

                        st.markdown(
                            f"""
                        <div class="{bubble_class}">
                            <small style="color: #94a3b8; font-weight: 600;">[{time_str}]</small><br/>
                            {description}
                        </div>
                        """,
                            unsafe_allow_html=True,
                        )
            finally:
                db.close()

        with col_emp2:
            st.markdown(
                f"""
            <div class="glass-card">
                <div class="glass-card-header">✉️ AI Recovery Copywriter Console</div>
            """,
                unsafe_allow_html=True,
            )

            db = SessionLocal()
            try:
                rec_record = (
                    db.query(RecoveryRecommendation)
                    .filter(RecoveryRecommendation.user_id == u_id)
                    .first()
                )

                # Dynamic edit area
                if rec_record:
                    st.write("**Active Recovery Strategy Draft:**")

                    # Read only display with status indicator
                    status_color = (
                        "#3b82f6" if rec_record.status == "Pending" else "#10b981"
                    )
                    st.markdown(
                        f"""
                    <div style="margin-bottom:12px;">
                        <span>Status:</span> <strong style="color:{status_color}; text-transform:uppercase;">{rec_record.status}</strong>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Editable campaign editor
                    edited_recommendation = st.text_area(
                        "Edit draft recommendation copy:",
                        value=rec_record.recommendation,
                        height=250,
                        key="edit_rec_textarea",
                    )

                    # Action buttons: Save & Send, Regenerate
                    action_col1, action_col2 = st.columns(2)
                    with action_col1:
                        if st.button("✉️ Approve & Dispatch", use_container_width=True):
                            rec_record.recommendation = edited_recommendation
                            rec_record.status = "Sent"
                            db.commit()
                            st.success(
                                "Recovery plan dispatched to customer support pipeline!"
                            )
                            st.rerun()
                    with action_col2:
                        if st.button("🔄 Regenerate draft", use_container_width=True):
                            with st.spinner("Re-generating recovery copy via Llama..."):
                                new_rec = generate_llm_recommendation(
                                    cohort_label,
                                    score_val,
                                    int(user_row["rage_clicks"]),
                                    int(user_row["error_count"]),
                                    float(user_row["avg_latency"]),
                                )
                                rec_record.recommendation = new_rec
                                rec_record.status = "Pending"
                                db.commit()
                                st.success("New recommendations generated!")
                                st.rerun()
                else:
                    st.info(
                        "No pre-generated recovery plan exists because this user is below the friction threshold."
                    )
                    st.write(
                        "Would you like to manually generate a custom AI outreach plan for this user anyway?"
                    )

                    if st.button(
                        "⚡ Force Generate Outreach Plan", use_container_width=True
                    ):
                        with st.spinner("Generating custom recovery copy via Llama..."):
                            new_rec = generate_llm_recommendation(
                                cohort_label,
                                score_val,
                                int(user_row["rage_clicks"]),
                                int(user_row["error_count"]),
                                float(user_row["avg_latency"]),
                            )
                            # Get cohort ID
                            cohort_record = (
                                db.query(UserCohort)
                                .filter(UserCohort.user_id == u_id)
                                .first()
                            )
                            c_id = cohort_record.id if cohort_record else None

                            rec_record = RecoveryRecommendation(
                                user_id=u_id,
                                cohort_id=c_id,
                                recommendation=new_rec,
                                status="Pending",
                            )
                            db.add(rec_record)
                            db.commit()
                            st.success("Outreach plan successfully created!")
                            st.rerun()
            finally:
                db.close()
            st.markdown("</div>", unsafe_allow_html=True)

    # ==================== STAGE 3: COHORT & METRICS ANALYTICS ====================
    elif stage == "📊 Cohort & Metrics Analytics":
        st.markdown("### **📊 Stage 3: Cohort Segmentation & Mathematical Metrics**")
        st.write(
            "This workspace represents the **data science and system metrics layer**, clearly separated from individual customer timelines."
        )

        # KPI row
        col_k1, col_k2, col_k3, col_k4 = st.columns(4)
        with col_k1:
            st.markdown(
                f"""
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color:#7c3aed;">{len(full_df)}</div>
                <div class="stat-desc">Monitored Accounts</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with col_k2:
            avg_f = full_df["score"].mean()
            st.markdown(
                f"""
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color:#ef4444;">{avg_f:.1f}</div>
                <div class="stat-desc">Avg Friction Rating</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with col_k3:
            at_risk_count = len(full_df[full_df["score"] >= friction_threshold])
            st.markdown(
                f"""
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color:#f59e0b;">{at_risk_count}</div>
                <div class="stat-desc">At-Risk (>= {friction_threshold:.0f})</div>
            </div>
            """,
                unsafe_allow_html=True,
            )
        with col_k4:
            happy_count = len(full_df[full_df["cohort_label"] == "Happy Active Users"])
            st.markdown(
                f"""
            <div class="glass-card" style="text-align: center;">
                <div class="stat-val" style="color:#10b981;">{happy_count}</div>
                <div class="stat-desc">Healthy Users</div>
            </div>
            """,
                unsafe_allow_html=True,
            )

        st.markdown("<br/>", unsafe_allow_html=True)

        # Grid of charts
        col_gr1, col_gr2 = st.columns(2)
        with col_gr1:
            st.markdown("#### **KMeans Cohort Distributions**")
            cohort_counts = full_df["cohort_label"].value_counts().reset_index()
            cohort_counts.columns = ["Cohort Class", "User Count"]
            st.bar_chart(
                data=cohort_counts, x="Cohort Class", y="User Count", color="#a855f7"
            )

        with col_gr2:
            st.markdown("#### **Average Experience Friction by Cohort**")
            cohort_scores = (
                full_df.groupby("cohort_label")["score"].mean().reset_index()
            )
            cohort_scores.columns = ["Cohort Class", "Avg Friction"]
            st.bar_chart(
                data=cohort_scores, x="Cohort Class", y="Avg Friction", color="#f43f5e"
            )

        # Feature Summary Dataframe
        st.markdown("#### **Cohort Average Features Grid**")
        cohort_summary = full_df.groupby("cohort_label")[
            ["score", "rage_clicks", "error_count", "avg_latency", "checkout_abandoned"]
        ].mean()
        cohort_summary.rename(
            columns={
                "score": "Avg Friction Score",
                "rage_clicks": "Avg Rage Clicks",
                "error_count": "Avg Network Errors",
                "avg_latency": "Avg Latency (ms)",
                "checkout_abandoned": "Checkout Abandonment Rate",
            },
            inplace=True,
        )
        st.dataframe(
            cohort_summary.style.format("{:.2f}").background_gradient(cmap="Purples"),
            use_container_width=True,
        )

        # MLflow details
        st.markdown("---")
        st.markdown("#### **MLflow Experiments & Models Metadata**")
        st.write(
            "The KMeans model run parameters, inertia, and silhouette logs are pushed to MLflow."
        )
        st.code(f"MLflow Tracking URI: {os.getenv('MLFLOW_TRACKING_URI')}")
        st.write("To launch your MLflow monitoring dashboard locally, run:")
        st.code("mlflow server --host 127.0.0.1 --port 5001")

    # ==================== STAGE 4: ENGINE CONTROL ROOM ====================
    elif stage == "🎛️ Engine Control Room":
        st.markdown("### **🎛️ Stage 4: Engine Control Room & Pipeline Orchestration**")
        st.write(
            "This workspace handles database schema migrations, simulation seeds, pipeline tasks execution, and external AI service configurations."
        )

        # Configuration details card
        st.markdown(
            """
        <div class="glass-card">
            <div class="glass-card-header">⚙️ Active Environment Configuration</div>
        """,
            unsafe_allow_html=True,
        )

        st.write(
            f"**Database Host:** `{os.getenv('DB_HOST', '127.0.0.1')}:{os.getenv('DB_PORT', '3306')}`"
        )
        st.write(f"**Database Name:** `{os.getenv('DB_NAME', 'ufip')}`")
        st.write(
            f"**Ollama Local API:** `{os.getenv('OLLAMA_API_URL', 'http://127.0.0.1:11434')}`"
        )
        st.write(f"**Active Model:** `{os.getenv('OLLAMA_MODEL', 'llama3.2')}`")
        st.markdown("</div>", unsafe_allow_html=True)

        # Prefect trigger
        st.markdown("#### **Prefect Pipeline Orchestrator**")
        st.write(
            "Triggering the main flow executes schema updates, user telemetry simulation, score generation, cohort recalculations, and recommendation caching."
        )

        if st.button(
            "🏃 Run Main ETL Processing Pipeline Now", use_container_width=True
        ):
            with st.spinner(
                "Orchestrating Prefect Pipeline... (initializing tables, seeding data, fitting KMeans model, and calling Ollama)..."
            ):
                from pipelines.etl_flow import ufip_etl_pipeline

                try:
                    ufip_etl_pipeline()
                    st.success(
                        "ETL Pipeline completed successfully! Database and recommendations updated."
                    )
                    st.rerun()
                except Exception as ex:
                    st.error(f"ETL Execution failed: {ex}")
