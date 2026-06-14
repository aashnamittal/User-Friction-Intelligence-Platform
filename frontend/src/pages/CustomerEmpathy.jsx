import React from 'react';

function CustomerEmpathy() {
  return (
    <div>
      <div className="header-banner">
        <h1 className="header-title">Customer Empathy Workspace</h1>
        <p className="header-subtitle">Chronological storylines, emotional meters, and active recovery draft campaigns.</p>
      </div>

      <div className="section-secondary">
        <p>This section is connected to the Java API via <code>/api/empathy/users</code>.</p>
        <div className="empathy-indicator empathy-red">
            <span>🔴</span> <strong>Friction Score: 85.0/100 - Severe Roadblock (Critical)</strong>
        </div>
        <div className="speech-bubble bubble-rage">
            <small style={{color: 'var(--text-muted)', fontWeight: 600}}>[14:32:01]</small><br/>
            🔴 <strong>Rage Clicks:</strong> Repeatedly smashed click on <code>submit_btn</code> on page <strong>/checkout</strong> out of frustration.
        </div>
      </div>
    </div>
  );
}

export default CustomerEmpathy;
