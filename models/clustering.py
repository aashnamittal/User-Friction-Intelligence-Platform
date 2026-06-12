import os
import pandas as pd
import numpy as np
import datetime
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
import mlflow
import mlflow.sklearn
from sqlalchemy import text
from sqlalchemy.orm import Session
from database.models import UserCohort

def train_and_log_clustering(db: Session, n_clusters=4):
    """
    Trains a KMeans clustering model on user behavior features, logs experiments with MLflow, 
    labels the resulting cohorts dynamically, and saves classifications to the database.
    """
    print("Extracting features for clustering...")
    # 1. Fetch features
    query = text("SELECT user_id, rage_clicks, error_count, avg_latency, checkout_abandoned FROM v_user_features")
    df = pd.read_sql_query(query, db.bind)
    
    if len(df) < n_clusters:
        print(f"Not enough users ({len(df)}) to train KMeans with {n_clusters} clusters. Skipping clustering.")
        return
        
    user_ids = df['user_id'].values
    features_df = df[['rage_clicks', 'error_count', 'avg_latency', 'checkout_abandoned']].copy()
    
    # 2. Scale features
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(features_df)
    
    # 3. MLflow Tracking
    if os.getenv("MLFLOW_TRACKING_URI"):
        # Ensure the directory for sqlite file exists if it's a sqlite path
        tracking_uri = os.getenv("MLFLOW_TRACKING_URI")
        if tracking_uri.startswith("sqlite:///"):
            sqlite_path = tracking_uri.replace("sqlite:///", "")
            sqlite_dir = os.path.dirname(sqlite_path)
            if sqlite_dir and not os.path.exists(sqlite_dir):
                os.makedirs(sqlite_dir, exist_ok=True)
        mlflow.set_tracking_uri(tracking_uri)
        
    mlflow.set_experiment("ufip_user_segmentation")
    
    with mlflow.start_run() as run:
        print("Training KMeans model...")
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init='auto')
        kmeans.fit(scaled_features)
        labels = kmeans.labels_
        
        # Calculate metrics
        inertia = kmeans.inertia_
        sil_score = silhouette_score(scaled_features, labels)
        
        # Log to MLflow
        mlflow.log_param("n_clusters", n_clusters)
        mlflow.log_param("random_state", 42)
        mlflow.log_metric("inertia", inertia)
        mlflow.log_metric("silhouette_score", sil_score)
        
        # Log model
        mlflow.sklearn.log_model(kmeans, "kmeans_model")
        
        print(f"KMeans model logged to MLflow. Run ID: {run.info.run_id}")
        
    # 4. Map cluster IDs to human-readable names
    # Group raw features by cluster label to compute averages and identify profiles
    features_df['cluster'] = labels
    cluster_means = features_df.groupby('cluster').mean()
    
    # Generate labels dynamically
    cluster_names = {}
    for cluster_id, row in cluster_means.iterrows():
        # High rage clicks or checkout abandonment
        if row['rage_clicks'] > 1.5 or row['checkout_abandoned'] > 0.3:
            cluster_names[cluster_id] = "Frustrated Checkout Users"
        # High latency
        elif row['avg_latency'] > 1000.0:
            cluster_names[cluster_id] = "Slow Network Users"
        # High error rate but not checkout-blocked
        elif row['error_count'] > 1.0:
            cluster_names[cluster_id] = "Error Prone Users"
        else:
            cluster_names[cluster_id] = "Happy Active Users"
            
    # 5. Save/Update in database
    print("Saving cohort classifications to database...")
    for idx, user_id in enumerate(user_ids):
        cluster_id = int(labels[idx])
        cohort_label = cluster_names.get(cluster_id, "Unknown Cohort")
        
        db_cohort = db.query(UserCohort).filter(UserCohort.user_id == int(user_id)).first()
        if db_cohort:
            db_cohort.cluster_id = cluster_id
            db_cohort.cohort_label = cohort_label
            db_cohort.assigned_at = datetime.datetime.utcnow()
        else:
            db_cohort = UserCohort(
                user_id=int(user_id),
                cluster_id=cluster_id,
                cohort_label=cohort_label,
                assigned_at=datetime.datetime.utcnow()
            )
            db.add(db_cohort)
            
    db.commit()
    print("Cohort mapping completed successfully.")
