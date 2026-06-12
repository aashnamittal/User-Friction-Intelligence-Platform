import pytest
from models.friction_scorer import calculate_user_friction

def test_happy_user_score():
    # Happy user with zero clicks, errors, latency, and no abandonment
    score = calculate_user_friction(
        rage_clicks=0,
        error_count=0,
        avg_latency=120.0,
        checkout_abandoned=False
    )
    assert score == 0.0

def test_slow_network_user_score():
    # Slow network user with high latency (e.g. 2500ms)
    # latency score = (2500 - 500) / 100 = 20 (max 20)
    score = calculate_user_friction(
        rage_clicks=0,
        error_count=0,
        avg_latency=2500.0,
        checkout_abandoned=False
    )
    assert score == 20.0

def test_checkout_frustrated_score():
    # Frustrated checkout user: 5 rage clicks, 2 errors, 120ms latency, checkout abandoned
    # rage_clicks: 5 * 10 = 50 (capped at 40)
    # error_count: 2 * 8 = 16
    # avg_latency: 120 < 500 = 0
    # checkout_abandoned: 30
    # total = 40 + 16 + 0 + 30 = 86
    score = calculate_user_friction(
        rage_clicks=5,
        error_count=2,
        avg_latency=120.0,
        checkout_abandoned=True
    )
    assert score == 86.0

def test_score_capping():
    # Extreme inputs: scores should cap at 100
    score = calculate_user_friction(
        rage_clicks=50, # 500 -> capped at 40
        error_count=40, # 320 -> capped at 30
        avg_latency=5000.0, # 45 -> capped at 20
        checkout_abandoned=True # 30
    )
    # 40 + 30 + 20 + 30 = 120 -> capped at 100
    assert score == 100.0
