import os
import requests
import datetime
from sqlalchemy.orm import Session
from database.models import RecoveryRecommendation, FrictionScore, UserCohort, User

OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

def generate_recommendation_fallback(cohort_label: str, score: float, rage_clicks: int, error_count: int, avg_latency: float) -> str:
    """
    Produces a rule-based template fallback when Ollama is unavailable.
    """
    if cohort_label == "Frustrated Checkout Users":
        return (
            f"SYSTEM FEEDBACK (Fallback Template):\n"
            f"User encountered significant friction on the checkout page (Rage Clicks: {rage_clicks}, Errors: {error_count}).\n"
            f"Recommended Recovery Actions:\n"
            f"1. Email user with a saved cart link and a 10% apology discount code.\n"
            f"2. Notify QA team to check checkout form submission logs for ID: payment_submit_btn.\n"
            f"3. Flag user for customer support outreach if checkout is attempted again."
        )
    elif cohort_label == "Slow Network Users":
        return (
            f"SYSTEM FEEDBACK (Fallback Template):\n"
            f"User suffered from poor network connection performance (Avg Latency: {avg_latency:.1f}ms).\n"
            f"Recommended Recovery Actions:\n"
            f"1. Optimistically pre-fetch checkout assets or suggest a lighter version of the interface.\n"
            f"2. Serve a friendly UI message acknowledging connection sluggishness and offer an offline email option."
        )
    elif cohort_label == "Error Prone Users":
        return (
            f"SYSTEM FEEDBACK (Fallback Template):\n"
            f"User experienced multiple application validation/system errors (Errors: {error_count}).\n"
            f"Recommended Recovery Actions:\n"
            f"1. Review input validation helpers and display clear troubleshooting tooltips.\n"
            f"2. Auto-fill previously validated details to decrease repeat inputs."
        )
    else:
        return (
            f"SYSTEM FEEDBACK (Fallback Template):\n"
            f"Active healthy user (Friction Score: {score:.1f}). No immediate recovery needed.\n"
            f"Action: Maintain standard onboarding flows."
        )

def generate_llm_recommendation(cohort_label: str, score: float, rage_clicks: int, error_count: int, avg_latency: float) -> str:
    """
    Queries local Ollama instance running Llama to generate a customized recovery suggestion.
    Falls back to a template if Ollama is offline or fails.
    """
    prompt = (
        f"You are a Customer Success AI Specialist. A user is experiencing friction on our platform. "
        f"Generate a customized, concise, and highly actionable recovery action plan (3 bullet points max) for this user.\n\n"
        f"User Details:\n"
        f"- Behavioral Cohort: {cohort_label}\n"
        f"- Friction Score: {score}/100\n"
        f"- Rage Click Count: {rage_clicks}\n"
        f"- Error Events Encountered: {error_count}\n"
        f"- Average System Latency: {avg_latency:.1f} ms\n\n"
        f"Write a friendly and professional set of recovery recommendations."
    )
    
    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.5,
            "num_predict": 150
        }
    }
    
    try:
        response = requests.post(
            f"{OLLAMA_API_URL}/api/generate",
            json=payload,
            timeout=15.0 # Keep timeout reasonable
        )
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "").strip()
        else:
            print(f"Ollama server returned error status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Ollama connection failed (using template fallback): {e}")
        
    return generate_recommendation_fallback(cohort_label, score, rage_clicks, error_count, avg_latency)

def pregenerate_user_recommendations(db: Session, high_friction_threshold=30.0):
    """
    Finds users with friction scores above the threshold and pre-generates recovery suggestions.
    """
    print(f"Pre-generating recovery recommendations for users with friction score > {high_friction_threshold}...")
    
    # Get high friction users
    targets = db.query(FrictionScore, UserCohort, User).join(
        UserCohort, FrictionScore.user_id == UserCohort.user_id
    ).join(
        User, FrictionScore.user_id == User.id
    ).filter(
        FrictionScore.score >= high_friction_threshold
    ).all()
    
    print(f"Found {len(targets)} users qualifying for recovery suggestions.")
    
    for score_record, cohort_record, user_record in targets:
        # Check if recommendation already exists
        rec = db.query(RecoveryRecommendation).filter(
            RecoveryRecommendation.user_id == user_record.id
        ).first()
        
        # Generate new suggestion
        recommendation_text = generate_llm_recommendation(
            cohort_label=cohort_record.cohort_label,
            score=score_record.score,
            rage_clicks=score_record.rage_clicks,
            error_count=score_record.error_count,
            avg_latency=score_record.avg_latency
        )
        
        if rec:
            rec.cohort_id = cohort_record.id
            rec.recommendation = recommendation_text
            rec.created_at = datetime.datetime.utcnow()
        else:
            rec = RecoveryRecommendation(
                user_id=user_record.id,
                cohort_id=cohort_record.id,
                recommendation=recommendation_text,
                status="Pending",
                created_at=datetime.datetime.utcnow()
            )
            db.add(rec)
            
    db.commit()
    print("Recommendation pre-generation completed.")
