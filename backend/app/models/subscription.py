"""Subscription model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Boolean, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class SubscriptionFrequency(str, enum.Enum):
    """Subscription frequency enumeration."""
    daily = "daily"
    weekly = "weekly"
    bi_weekly = "bi_weekly"
    monthly = "monthly"


class SubscriptionStatus(str, enum.Enum):
    """Subscription status enumeration."""
    active = "active"
    paused = "paused"
    cancelled = "cancelled"
    expired = "expired"


class Subscription(Base):
    """Subscription model for recurring orders."""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    
    frequency = Column(SQLEnum(SubscriptionFrequency), nullable=False)
    status = Column(String(50), default="active", index=True)  # Store as string, not enum
    
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=True)
    next_delivery_date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    payment_method = Column(String(50), nullable=False)
    auto_renew = Column(Boolean, default=True)
    
    pause_reason = Column(Text, nullable=True)
    resume_date = Column(DateTime(timezone=True), nullable=True)
    
    total_orders_created = Column(Integer, default=0)
    last_order_date = Column(DateTime(timezone=True), nullable=True)
    failed_attempts = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Subscription(id={self.id}, customer_id={self.customer_id}, status={self.status})>"