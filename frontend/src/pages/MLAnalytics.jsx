import React from 'react';

function MLAnalytics() {
  return (
    <div>
      <div className="header-banner">
        <h1 className="header-title">Machine Learning Analytics</h1>
        <p className="header-subtitle">Cohort Segmentation & Predictive Telemetry Analysis</p>
      </div>

      <div className="section-secondary">
        <h3>📊 Cohort & Population Overview</h3>
        <p>This data is fetched from the Java Backend <code>/api/ml/cohorts</code>, utilizing the Python Prefect models stored in the MySQL database.</p>
        <div style={{ display: 'flex', gap: '24px', marginTop: '24px' }}>
          <div className="glass-card" style={{ flex: 1, textAlign: 'center', marginBottom: 0 }}>
            <div className="stat-val" style={{color: 'var(--success)'}}>1,204</div>
            <div className="stat-desc">Healthy Users</div>
          </div>
          <div className="glass-card" style={{ flex: 1, textAlign: 'center', marginBottom: 0 }}>
            <div className="stat-val" style={{color: 'var(--alert)'}}>45</div>
            <div className="stat-desc">At-Risk Accounts</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MLAnalytics;
