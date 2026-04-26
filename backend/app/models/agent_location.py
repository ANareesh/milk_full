"""Agent location tracking model."""
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from datetime import datetime

from app.core.database import Base


class AgentLocation(Base):
    """Agent location history tracking."""
    __tablename__ = "agent_locations"

    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False, index=True)
    delivery_id = Column(Integer, ForeignKey("deliveries.id"), nullable=True)
    
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    accuracy = Column(Float, nullable=True)  # GPS accuracy in meters
    
    address = Column(String(500), nullable=True)
    speed = Column(Float, nullable=True)  # Speed in km/h
    bearing = Column(Float, nullable=True)  # Direction in degrees
    
    is_active = Column(Integer, default=1)  # 1 = current location, 0 = history
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<AgentLocation(agent_id={self.agent_id}, lat={self.latitude}, lng={self.longitude})>"