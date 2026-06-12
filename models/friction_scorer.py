import datetime
from sqlalchemy import text
from sqlalchemy.orm import Session
from database.models import FrictionScore

def calculate_user_friction(rage_clicks: int, error_count: int, avg_latency: float, checkout_abandoned: bool) -> float:
    """
    Computes a friction score from 0 to 100 based on user experience telemetry.
    """
    # 1. Rage Click Friction (highly frustrated behavior)
    # Each rage click event adds 10 points. Max contribution: 40 points.
    rc_score = min(float(rage_clicks or 0) * 10.0, 40.0)
    
    # 2. Error Friction (system/validation failures)
    # Each error adds 8 points. Max contribution: 30 points.
    err_score = min(float(error_count or 0) * 8.0, 30.0)
    
    # 3. Latency Friction (slow connections)
    # Latency above 500ms adds 1 point per 100ms. Max contribution: 20 points.
    lat_score = 0.0
    if avg_latency and avg_latency > 500.0:
        lat_score = min((avg_latency - 500.0) / 100.0, 20.0)
        
    # 4. Checkout Abandonment Friction (revenue risk)
    # Abandoning checkout adds 30 points.
    abandon_score = 30.0 if checkout_abandoned else 0.0
    
    # Calculate total and cap at 100
    total_score = min(rc_score + err_score + lat_score + abandon_score, 100.0)
    return round(total_score, 2)

def compute_and_save_scores(db: Session):
    """
    Reads user behavior aggregates from the SQL view, calculates friction scores, 
    and writes them into the friction_scores table.
    """
    print("Computing user friction scores...")
    
    # Query features from database view
    result = db.execute(text("SELECT user_id, rage_clicks, error_count, avg_latency, checkout_abandoned FROM v_user_features"))
    rows = result.fetchall()
    
    for row in rows:
        user_id = row[0]
        rage_clicks = int(row[1] or 0)
        error_count = int(row[2] or 0)
        avg_latency = float(row[3] or 0.0)
        checkout_abandoned = bool(row[4] or False)
        
        score = calculate_user_friction(rage_clicks, error_count, avg_latency, checkout_abandoned)
        
        # Check if score already exists for user
        db_score = db.query(FrictionScore).filter(FrictionScore.user_id == user_id).first()
        if db_score:
            db_score.score = score
            db_score.rage_clicks = rage_clicks
            db_score.error_count = error_count
            db_score.avg_latency = avg_latency
            db_score.checkout_abandoned = checkout_abandoned
            db_score.calculated_at = datetime.datetime.utcnow()
        else:
            db_score = FrictionScore(
                user_id=user_id,
                score=score,
                rage_clicks=rage_clicks,
                error_count=error_count,
                avg_latency=avg_latency,
                checkout_abandoned=checkout_abandoned,
                calculated_at=datetime.datetime.utcnow()
            )
            db.add(db_score)
            
    db.commit()
    print(f"Friction scores successfully computed for {len(rows)} users.")
