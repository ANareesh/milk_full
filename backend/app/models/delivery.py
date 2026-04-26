"""Delivery model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class DeliveryStatus(str, enum.Enum):
    """Delivery status enumeration."""
    pending = "pending"
    in_progress = "in_progress"
    delivered = "delivered"
    failed = "failed"
    returning = "returning"


class Delivery(Base):
    """Delivery tracking model."""
    __tablename__ = "deliveries"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, unique=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True, index=True)
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.pending, index=True)
    scheduled_date = Column(DateTime(timezone=True), nullable=False)
    actual_delivery_date = Column(DateTime(timezone=True), nullable=True)
    pickup_time = Column(DateTime(timezone=True), nullable=True)
    delivery_time = Column(DateTime(timezone=True), nullable=True)
    customer_signature = Column(String(255), nullable=True)
    delivery_notes = Column(Text, nullable=True)
    delivery_photo_url = Column(String(255), nullable=True)
    failed_reason = Column(String(255), nullable=True)
    delivery_otp = Column(String(6), nullable=True)
    otp_verified = Column(Boolean, default=False)
    latitude_delivered = Column(Float, nullable=True)
    longitude_delivered = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Delivery(id={self.id}, order_id={self.order_id}, status={self.status})>"
