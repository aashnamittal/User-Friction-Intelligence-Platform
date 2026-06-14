import React from 'react';

function EngineControl() {
  return (
    <div>
      <div className="header-banner">
        <h1 className="header-title">Engine Control Room</h1>
        <p className="header-subtitle">Pipeline Orchestration & System Configurations</p>
      </div>

      <div className="section-secondary" style={{ display: 'flex', gap: '24px' }}>
        <div className="glass-card" style={{ flex: 1, marginBottom: 0 }}>
            <div className="glass-card-header">⚙️ Active Environment Configuration</div>
            <p><strong>Database:</strong> <code>ufip</code> on <code>localhost:3307</code></p>
            <p><strong>Backend:</strong> <code>Java Spring Boot (Port 8080)</code></p>
            <p><strong>Pipeline:</strong> <code>Python Prefect</code></p>
        </div>
        <div className="glass-card" style={{ flex: 1, marginBottom: 0 }}>
            <div className="glass-card-header">🏥 System Health Monitors</div>
            <div className="empathy-indicator empathy-green" style={{marginBottom: '12px'}}>MySQL: Connected</div>
            <div className="empathy-indicator empathy-amber" style={{marginBottom: 0}}>Python ETL: Standby</div>
        </div>
      </div>

      <div className="glass-card">
        <h4>Prefect Pipeline Orchestrator</h4>
        <p style={{marginBottom: '24px'}}>Triggering the main flow executes schema updates, user telemetry simulation, score generation, and cohort recalculations via the Java API executing a Python ProcessBuilder.</p>
        <button className="btn-primary">🏃 Run Main ETL Processing Pipeline Now</button>
      </div>
    </div>
  );
}

export default EngineControl;
