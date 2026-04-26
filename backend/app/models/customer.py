"""Customer model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class Customer(Base):
    """Customer model."""
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    address = Column(String(255), nullable=False)
    city = Column(String(50), nullable=False)
    postal_code = Column(String(10), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    preferred_delivery_time = Column(String(50), nullable=True)  # e.g., "morning" or "06:00-08:00"
    total_amount_due = Column(Float, default=0.0)
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Customer(id={self.id}, user_id={self.user_id}, city={self.city})>"
