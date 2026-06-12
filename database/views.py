from sqlalchemy import text

CREATE_VIEW_SQL = """
CREATE VIEW v_user_features AS
SELECT 
    u.id AS user_id,
    u.username AS username,
    COUNT(DISTINCT s.id) AS total_sessions,
    COUNT(e.id) AS total_events,
    SUM(CASE WHEN e.event_type = 'rage_click' THEN 1 ELSE 0 END) AS rage_clicks,
    SUM(CASE WHEN e.event_type = 'error' THEN 1 ELSE 0 END) AS error_count,
    COALESCE(AVG(CASE WHEN e.event_type = 'network_latency' THEN e.latency_ms ELSE NULL END), 0.0) AS avg_latency,
    MAX(CASE WHEN e.event_type = 'checkout_abandoned' THEN 1 ELSE 0 END) AS checkout_abandoned
FROM users u
LEFT JOIN sessions s ON u.id = s.user_id
LEFT JOIN events e ON s.id = e.session_id
GROUP BY u.id, u.username;
"""

def create_feature_view(engine):
    with engine.begin() as conn:
        conn.execute(text("DROP VIEW IF EXISTS v_user_features;"))
        conn.execute(text(CREATE_VIEW_SQL))
