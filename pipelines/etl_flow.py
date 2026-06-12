import os
from prefect import task, flow
from database.connection import engine, SessionLocal, Base
from database.views import create_feature_view
from database.seed import seed_data
from models.friction_scorer import compute_and_save_scores
from models.clustering import train_and_log_clustering
from models.recovery_generator import pregenerate_user_recommendations
from dotenv import load_dotenv

# Load env file
dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.development')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    load_dotenv()

@task(name="Initialize Schema & Views")
def initialize_db_schema():
    print("Initializing SQLAlchemy database tables...")
    Base.metadata.create_all(bind=engine)
    print("Creating MySQL/SQLite Feature Aggregation view...")
    create_feature_view(engine)

@task(name="Seed User Behavior logs")
def seed_behavioral_data():
    db = SessionLocal()
    try:
        seed_data(db, num_users=60)
    finally:
        db.close()

@task(name="Calculate Friction Scores")
def run_friction_scoring():
    db = SessionLocal()
    try:
        compute_and_save_scores(db)
    finally:
        db.close()

@task(name="Cluster Behavioral Cohorts")
def run_cohort_clustering():
    db = SessionLocal()
    try:
        train_and_log_clustering(db, n_clusters=4)
    finally:
        db.close()

@task(name="Generate Recovery Recommendations")
def run_recommendations_generation():
    db = SessionLocal()
    try:
        pregenerate_user_recommendations(db, high_friction_threshold=30.0)
    finally:
        db.close()

@flow(name="UFIP Main ETL Pipeline")
def ufip_etl_pipeline():
    initialize_db_schema()
    seed_behavioral_data()
    run_friction_scoring()
    run_cohort_clustering()
    run_recommendations_generation()

if __name__ == "__main__":
    ufip_etl_pipeline()
