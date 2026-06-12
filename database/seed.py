import uuid
import random
import datetime
from sqlalchemy.orm import Session
from database.connection import SessionLocal, engine, Base
from database.models import User, Session as DBSession, Event
from database.views import create_feature_view

# Generate a list of cohort groups for seeding
def seed_data(db: Session, num_users=50):
    # Check if database already has users
    if db.query(User).count() > 0:
        print("Database already has data. Skipping seeding.")
        return
        
    print(f"Seeding {num_users} users with simulated behavioral data...")
    
    # Define user types
    cohorts_distribution = ["happy", "frustrated_checkout", "slow_network", "error_prone"]
    
    devices = ["macOS Chrome", "iOS Safari", "Windows Edge", "Android Chrome"]
    locations = ["New York, USA", "San Francisco, USA", "London, UK", "Berlin, Germany", "Tokyo, Japan"]
    
    for i in range(num_users):
        username = f"user_{i+1:03d}_{random.choice(['alpha', 'beta', 'gamma', 'delta'])}"
        user_type = cohorts_distribution[i % len(cohorts_distribution)]
        
        user = User(username=username)
        db.add(user)
        db.flush() # Populate user.id
        
        # Determine number of sessions
        num_sessions = random.randint(2, 6) if user_type == "happy" else random.randint(1, 3)
        
        for s_idx in range(num_sessions):
            session_id = str(uuid.uuid4())
            device = random.choice(devices)
            location = random.choice(locations)
            
            # Sessions spaced out in the last 7 days
            start_offset = random.randint(0, 168) # hours
            started_at = datetime.datetime.utcnow() - datetime.timedelta(hours=start_offset)
            ended_at = started_at + datetime.timedelta(minutes=random.randint(5, 30))
            
            session = DBSession(
                id=session_id,
                user_id=user.id,
                started_at=started_at,
                ended_at=ended_at,
                device=device,
                location=location
            )
            db.add(session)
            db.flush()
            
            # Events in the session
            current_time = started_at
            
            # All users start at home and search
            for page in ["/home", "/search"]:
                current_time += datetime.timedelta(seconds=random.randint(10, 40))
                db.add(Event(
                    session_id=session_id,
                    event_type="page_view",
                    page=page,
                    created_at=current_time
                ))
                
                # Network latency event
                latency = random.randint(50, 250)
                if user_type == "slow_network":
                    latency = random.randint(1500, 4500)
                
                db.add(Event(
                    session_id=session_id,
                    event_type="network_latency",
                    page=page,
                    latency_ms=latency,
                    created_at=current_time
                ))
            
            if user_type == "happy":
                # Happy path: product, cart, checkout, confirmation
                for page in ["/product/123", "/cart", "/checkout", "/confirmation"]:
                    current_time += datetime.timedelta(seconds=random.randint(15, 60))
                    db.add(Event(
                        session_id=session_id,
                        event_type="page_view",
                        page=page,
                        created_at=current_time
                    ))
                    
                    db.add(Event(
                        session_id=session_id,
                        event_type="click",
                        page=page,
                        element="button_next",
                        created_at=current_time
                    ))
                    
            elif user_type == "frustrated_checkout":
                # Product, cart, checkout... then rage click and abandon
                for page in ["/product/123", "/cart", "/checkout"]:
                    current_time += datetime.timedelta(seconds=random.randint(15, 60))
                    db.add(Event(
                        session_id=session_id,
                        event_type="page_view",
                        page=page,
                        created_at=current_time
                    ))
                    
                # On checkout page, user encounters a bug
                current_time += datetime.timedelta(seconds=20)
                # Rage click on payment button
                for rc in range(random.randint(5, 12)):
                    current_time += datetime.timedelta(milliseconds=200)
                    db.add(Event(
                        session_id=session_id,
                        event_type="rage_click",
                        page="/checkout",
                        element="payment_submit_btn",
                        created_at=current_time
                    ))
                
                # System error event
                current_time += datetime.timedelta(seconds=1)
                db.add(Event(
                    session_id=session_id,
                    event_type="error",
                    page="/checkout",
                    element="payment_submit_btn",
                    metadata_text="500 Internal Server Error - Payment Gateway Timeout",
                    created_at=current_time
                ))
                
                # Abandon event
                current_time += datetime.timedelta(seconds=5)
                db.add(Event(
                    session_id=session_id,
                    event_type="checkout_abandoned",
                    page="/checkout",
                    created_at=current_time
                ))
                
            elif user_type == "slow_network":
                # Product, cart, slow page load, abandon
                for page in ["/product/123", "/cart"]:
                    current_time += datetime.timedelta(seconds=random.randint(15, 60))
                    db.add(Event(
                        session_id=session_id,
                        event_type="page_view",
                        page=page,
                        created_at=current_time
                    ))
                    # Extremely high latency
                    db.add(Event(
                        session_id=session_id,
                        event_type="network_latency",
                        page=page,
                        latency_ms=random.randint(4000, 8000),
                        created_at=current_time
                    ))
                    
            elif user_type == "error_prone":
                # Try to navigate but hit validation/script errors
                for page in ["/product/123", "/cart"]:
                    current_time += datetime.timedelta(seconds=random.randint(10, 30))
                    db.add(Event(
                        session_id=session_id,
                        event_type="page_view",
                        page=page,
                        created_at=current_time
                    ))
                    
                    if random.random() > 0.3:
                        db.add(Event(
                            session_id=session_id,
                            event_type="error",
                            page=page,
                            element="form_input",
                            metadata_text="Validation Error: Invalid format zip code",
                            created_at=current_time
                        ))
                        
    db.commit()
    print("Database seeding completed.")

def init_and_seed_db(num_users=60):
    Base.metadata.create_all(bind=engine)
    create_feature_view(engine)
    db = SessionLocal()
    try:
        seed_data(db, num_users=num_users)
    finally:
        db.close()

if __name__ == "__main__":
    init_and_seed_db()
