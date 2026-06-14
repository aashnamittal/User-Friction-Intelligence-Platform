import os
import pytest
from streamlit.testing.v1 import AppTest

# Set mock testing configuration before loading components
os.environ["TESTING"] = "True"


def test_dashboard_navigation():
    """
    Autonomous verification of UFIP Dashboard interactive navigation tabs.
    Simulates clicks on Stage 1-4 buttons and asserts two-way session state sync.
    """
    # 1. Initialize AppTest from app/dashboard.py
    at = AppTest.from_file("app/dashboard.py")

    # Set default size for consistent rendering checks
    at.run(timeout=10)

    # 2. Assert no exceptions occurred during startup
    assert not at.exception, f"Dashboard startup failed with exception: {at.exception}"

    # 3. Assert default stage is Live Telemetry Ingestion
    assert at.session_state.sidebar_stage_radio == "📡 Ingestion & Telemetry Feed"

    # 4. Simulate clicking Button 2: Customer Empathy Workspace
    btn_stage_2 = at.button(key="btn_stage_2")
    assert btn_stage_2 is not None, "Button key 'btn_stage_2' not found on the page."
    btn_stage_2.click().run(timeout=10)

    # Assert state updated and no exceptions
    assert at.session_state.sidebar_stage_radio == "👤 Customer Empathy Space"
    assert not at.exception, f"Stage 2 failed: {at.exception}"

    # 5. Simulate clicking Button 3: Cohort & Metrics Analytics
    btn_stage_3 = at.button(key="btn_stage_3")
    assert btn_stage_3 is not None, "Button key 'btn_stage_3' not found on the page."
    btn_stage_3.click().run(timeout=10)

    # Assert state updated and no exceptions
    assert at.session_state.sidebar_stage_radio == "📊 Cohort & Metrics Analytics"
    assert not at.exception, f"Stage 3 failed: {at.exception}"

    # 6. Simulate clicking Button 4: Engine Control Room
    btn_stage_4 = at.button(key="btn_stage_4")
    assert btn_stage_4 is not None, "Button key 'btn_stage_4' not found on the page."
    btn_stage_4.click().run(timeout=10)

    # Assert state updated and no exceptions
    assert at.session_state.sidebar_stage_radio == "🎛️ Engine Control Room"
    assert not at.exception, f"Stage 4 failed: {at.exception}"

    # 7. Check 2-way sync: Simulate updating the radio selection from the sidebar instead
    radio = at.sidebar.radio(key="sidebar_stage_radio")
    assert radio is not None, "Sidebar stage selector radio button not found."

    # Select index 0 (Ingestion Feed)
    radio.set_value("📡 Ingestion & Telemetry Feed").run(timeout=10)

    # Assert that session state synced back to stage 1
    assert at.session_state.sidebar_stage_radio == "📡 Ingestion & Telemetry Feed"
    assert not at.exception
