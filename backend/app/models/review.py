"""Review and Rating model."""
from sqlalchemy import Column, Integer, Float, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class Review(Base):
    """Customer review and rating model."""
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    
    rating = Column(Float, nullable=False)  # 1-5
    quality_rating = Column(Float, nullable=True)  # Product quality
    delivery_rating = Column(Float, nullable=True)  # Delivery service
    agent_rating = Column(Float, nullable=True)  # Agent rating
    
    comment = Column(Text, nullable=True)
    is_recommended = Column(Boolean, default=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Review(id={self.id}, customer_id={self.customer_id}, rating={self.rating})>"
