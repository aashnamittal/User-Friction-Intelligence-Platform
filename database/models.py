from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
import datetime
from database.connection import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")
    friction_scores = relationship("FrictionScore", back_populates="user", cascade="all, delete-orphan")
    cohorts = relationship("UserCohort", back_populates="user", cascade="all, delete-orphan")
    recommendations = relationship("RecoveryRecommendation", back_populates="user", cascade="all, delete-orphan")

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(String(50), primary_key=True, index=True) # UUID string
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    ended_at = Column(DateTime, nullable=True)
    device = Column(String(100), nullable=True)
    location = Column(String(100), nullable=True)
    
    user = relationship("User", back_populates="sessions")
    events = relationship("Event", back_populates="session", cascade="all, delete-orphan")

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(50), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    event_type = Column(String(50), index=True, nullable=False) # e.g. click, error, network_latency, rage_click, checkout_abandoned
    page = Column(String(100), nullable=False)
    element = Column(String(100), nullable=True)
    latency_ms = Column(Integer, default=0, nullable=False)
    metadata_text = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    session = relationship("Session", back_populates="events")

class FrictionScore(Base):
    __tablename__ = "friction_scores"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    score = Column(Float, nullable=False)
    rage_clicks = Column(Integer, default=0, nullable=False)
    error_count = Column(Integer, default=0, nullable=False)
    avg_latency = Column(Float, default=0.0, nullable=False)
    checkout_abandoned = Column(Boolean, default=False, nullable=False)
    calculated_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="friction_scores")

class UserCohort(Base):
    __tablename__ = "user_cohorts"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cohort_label = Column(String(100), nullable=False) # e.g. 'Frustrated Checkout Users', 'Active Happy Users'
    cluster_id = Column(Integer, nullable=False)
    assigned_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="cohorts")

class RecoveryRecommendation(Base):
    __tablename__ = "recovery_recommendations"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    cohort_id = Column(Integer, ForeignKey("user_cohorts.id", ondelete="SET NULL"), nullable=True)
    recommendation = Column(Text, nullable=False)
    status = Column(String(50), default="Pending", nullable=False) # e.g. Pending, Sent, Resolved
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    user = relationship("User", back_populates="recommendations")
