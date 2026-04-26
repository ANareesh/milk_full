"""Agent schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class AgentStatus(str, Enum):
    """Agent status enumeration."""
    active = "active"
    inactive = "inactive"
    on_route = "on_route"
    on_break = "on_break"


class AgentBase(BaseModel):
    """Base agent schema."""
    agent_code: str = Field(..., max_length=50)
    assigned_area: Optional[str] = Field(None, max_length=100)
    vehicle_number: Optional[str] = Field(None, max_length=20)


class AgentCreate(BaseModel):
    """Agent creation schema."""
    user_id: int
    agent_code: str = Field(..., max_length=50)
    assigned_area: Optional[str] = Field(None, max_length=100)
    vehicle_number: Optional[str] = Field(None, max_length=20)


class AgentUpdate(BaseModel):
    """Agent update schema."""
    assigned_area: Optional[str] = Field(None, max_length=100)
    vehicle_number: Optional[str] = Field(None, max_length=20)
    status: Optional[AgentStatus] = None


class AgentLocationUpdate(BaseModel):
    """Agent location update schema."""
    latitude: float
    longitude: float


class AgentResponse(AgentBase):
    """Agent response schema."""
    id: int
    user_id: int
    status: AgentStatus
    current_latitude: Optional[float]
    current_longitude: Optional[float]
    total_deliveries: int
    total_earnings: float
    available_for_delivery: bool
    rating: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
