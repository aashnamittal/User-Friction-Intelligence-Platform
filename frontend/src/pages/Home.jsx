import React, { useEffect, useState } from 'react';
import axios from 'axios';

function Home() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    axios.get('http://localhost:8080/api/telemetry/logs')
      .then(response => {
        setLogs(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching logs:", error);
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <div className="header-banner">
        <h1 className="header-title">Live Telemetry Ingestion</h1>
        <p className="header-subtitle">Real-time user event tracking and system monitoring feed.</p>
      </div>

      <div className="section-secondary">
        <h3>📡 Top-Level Metrics</h3>
        <div style={{ display: 'flex', gap: '24px', marginTop: '24px' }}>
          <div className="glass-card" style={{ flex: 1, textAlign: 'center', marginBottom: 0 }}>
            <div className="stat-val">{logs.length > 0 ? "50+" : "0"}</div>
            <div className="stat-desc">Recent Events</div>
          </div>
        </div>
      </div>

      <h4>Real-time Event Log (Latest 50 Telemetry Signals)</h4>
      {loading ? (
        <p>Loading events from Java API...</p>
      ) : logs.length === 0 ? (
        <p>No matching telemetry events found in the database.</p>
      ) : (
        <div style={{ background: 'var(--bg-primary)', border: '1px solid var(--border-color)', borderRadius: 'var(--radius)', overflow: 'hidden', marginTop: '16px' }}>
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Session ID</th>
                <th>Event Type</th>
                <th>Page Route</th>
                <th>UI Element</th>
                <th>Latency</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.createdAt).toLocaleTimeString()}</td>
                  <td>{log.sessionId.substring(0, 8)}...</td>
                  <td><span style={{fontWeight: 600, color: 'var(--primary)'}}>{log.eventType}</span></td>
                  <td>{log.page}</td>
                  <td>{log.element || '-'}</td>
                  <td>{log.latencyMs > 0 ? `${log.latencyMs}ms` : '-'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Home;
