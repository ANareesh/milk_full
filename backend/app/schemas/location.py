"""Location tracking schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class LocationUpdate(BaseModel):
    """Agent location update."""
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    accuracy: Optional[float] = Field(None, description="GPS accuracy in meters")
    speed: Optional[float] = Field(None, ge=0, description="Speed in km/h")
    bearing: Optional[float] = Field(None, ge=0, le=360, description="Direction in degrees")
    address: Optional[str] = Field(None, max_length=500, description="Address string")


class LocationResponse(BaseModel):
    """Location response model."""
    id: int
    agent_id: int
    latitude: float
    longitude: float
    accuracy: Optional[float]
    speed: Optional[float]
    bearing: Optional[float]
    address: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True


class AgentLocationResponse(BaseModel):
    """Agent current location."""
    agent_id: int
    latitude: float
    longitude: float
    accuracy: Optional[float]
    speed: Optional[float]
    bearing: Optional[float]
    last_updated: datetime
    
    class Config:
        from_attributes = True


class LocationHistoryResponse(BaseModel):
    """Location history."""
    locations: list[LocationResponse]
    total_distance: float  # in km
    average_speed: float  # in km/h
    start_time: datetime
    end_time: datetime


class AgentMapResponse(BaseModel):
    """Agent data for map display."""
    agent_id: int
    agent_name: str
    latitude: float
    longitude: float
    status: str
    assigned_area: Optional[str]
    current_delivery_id: Optional[int]
    last_updated: datetime
    
    class Config:
        from_attributes = True