import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.connection import Base
from database.views import create_feature_view
from database.models import User, Session as DBSession, Event, UserCohort
from models.clustering import train_and_log_clustering

@pytest.fixture(scope="function")
def test_db():
    # Set environment variables for testing
    os.environ["TESTING"] = "True"
    os.environ["MLFLOW_TRACKING_URI"] = "sqlite:///:memory:"
    
    engine = create_engine("sqlite:///:memory:")
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    create_feature_view(engine)
    
    db = TestingSessionLocal()
    
    # Insert at least 4 users to test 4 clusters
    for i in range(12):
        user = User(username=f"test_user_{i}")
        db.add(user)
        db.flush()
        
        # Add a session and events
        session = DBSession(id=f"session_{i}", user_id=user.id)
        db.add(session)
        db.flush()
        
        # Mix features to make centroids distinct
        if i % 4 == 0:
            # Happy path
            db.add(Event(session_id=session.id, event_type="page_view", page="/home"))
        elif i % 4 == 1:
            # Frustrated (Rage click)
            for rc in range(5):
                db.add(Event(session_id=session.id, event_type="rage_click", page="/checkout"))
            db.add(Event(session_id=session.id, event_type="checkout_abandoned", page="/checkout"))
        elif i % 4 == 2:
            # Slow network
            db.add(Event(session_id=session.id, event_type="network_latency", page="/home", latency_ms=3000))
        else:
            # Error prone
            for ec in range(3):
                db.add(Event(session_id=session.id, event_type="error", page="/cart"))
            
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_clustering_runs(test_db):
    # Run the clustering algorithm on our mock test database
    train_and_log_clustering(test_db, n_clusters=4)
    
    # Query database and verify that user cohorts were assigned
    cohorts = test_db.query(UserCohort).all()
    assert len(cohorts) == 12
    
    # Verify we mapped clusters correctly to labels
    labels = [c.cohort_label for c in cohorts]
    # Check that the categories exist
    assert "Happy Active Users" in labels
    assert "Frustrated Checkout Users" in labels
    assert "Slow Network Users" in labels
    assert "Error Prone Users" in labels
