"""Order model."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, Enum as SQLEnum, String, Text
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class OrderStatus(str, enum.Enum):
    """Order status enumeration."""
    pending = "pending"
    confirmed = "confirmed"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"


class OrderType(str, enum.Enum):
    """Order type enumeration."""
    subscription = "subscription"  # From subscription
    one_time = "one_time"  # One-time order


class Order(Base):
    """Order model."""
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    order_type = Column(SQLEnum(OrderType), nullable=False)
    quantity = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    total_amount = Column(Float, nullable=False)
    status = Column(SQLEnum(OrderStatus), default=OrderStatus.pending, index=True)
    delivery_date = Column(DateTime(timezone=True), nullable=False)
    special_instructions = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"
