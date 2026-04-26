"""Delivery Agent model."""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class AgentStatus(str, enum.Enum):
    """Agent status enumeration."""
    active = "active"
    inactive = "inactive"
    on_route = "on_route"
    on_break = "on_break"


class Agent(Base):
    """Delivery agent model."""
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    agent_code = Column(String(50), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(AgentStatus), default=AgentStatus.active, nullable=False, index=True)
    assigned_area = Column(String(100), nullable=True)
    vehicle_number = Column(String(20), nullable=True)
    current_latitude = Column(Float, nullable=True)
    current_longitude = Column(Float, nullable=True)
    total_deliveries = Column(Integer, default=0)
    total_earnings = Column(Float, default=0.0)
    available_for_delivery = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Agent(id={self.id}, user_id={self.user_id}, agent_code={self.agent_code}, status={self.status})>"
