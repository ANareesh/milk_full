"""Map visualization schemas."""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class MapMarkerType(str, Enum):
    """Map marker types."""
    AGENT = "agent"
    CUSTOMER = "customer"
    DELIVERY = "delivery"
    WAREHOUSE = "warehouse"


class MapCoordinate(BaseModel):
    """Map coordinate."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class AgentMapMarker(BaseModel):
    """Agent marker for admin map."""
    agent_id: int
    agent_name: str
    user_id: int
    phone: str
    email: str
    latitude: float
    longitude: float
    accuracy: Optional[float]
    speed: Optional[float]
    bearing: Optional[float]
    address: Optional[str]
    status: str  # active, inactive, on_break
    assigned_area: Optional[str]
    current_deliveries_count: int
    total_earnings: float
    last_updated: datetime
    is_active: bool

    class Config:
        from_attributes = True


class DeliveryMapMarker(BaseModel):
    """Delivery marker for customer map."""
    delivery_id: int
    agent_id: int
    agent_name: str
    agent_phone: str
    order_id: int
    customer_id: int
    customer_name: str
    latitude: float  # Agent current location
    longitude: float
    customer_latitude: float  # Customer delivery address
    customer_longitude: float
    status: str  # pending, in_progress, delivered
    estimated_arrival: Optional[datetime]
    actual_delivery_time: Optional[datetime]
    distance_remaining_km: float
    last_updated: datetime

    class Config:
        from_attributes = True


class RoutePoint(BaseModel):
    """A point on a delivery route."""
    sequence: int
    latitude: float
    longitude: float
    timestamp: datetime
    speed: Optional[float]
    accuracy: Optional[float]


class DeliveryRouteResponse(BaseModel):
    """Complete delivery route."""
    delivery_id: int
    agent_id: int
    agent_name: str
    order_id: int
    start_point: RoutePoint
    end_point: RoutePoint
    total_route_points: int
    total_distance_km: float
    average_speed_kmh: float
    estimated_duration_minutes: int
    actual_duration_minutes: Optional[int]
    route_points: List[RoutePoint]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class AdminMapResponseData(BaseModel):
    """Admin map view response."""
    agents_online: int
    agents_busy: int
    agents_on_break: int
    total_deliveries_in_progress: int
    agent_markers: List[AgentMapMarker]
    center_latitude: float = 28.7041  # Default to Delhi
    center_longitude: float = 77.1025
    zoom_level: int = 12
    timestamp: datetime

    class Config:
        from_attributes = True


class CustomerDeliveryTrackingResponse(BaseModel):
    """Customer delivery tracking response."""
    has_active_delivery: bool
    delivery_marker: Optional[DeliveryMapMarker]
    estimated_delivery_time: Optional[datetime]
    status_message: str
    timestamp: datetime

    class Config:
        from_attributes = True


class MapStatsResponse(BaseModel):
    """Map statistics."""
    total_agents: int
    agents_online: int
    agents_in_delivery: int
    total_deliveries_in_progress: int
    total_distance_covered_today_km: float
    average_delivery_time_minutes: float
    on_time_delivery_percentage: float
    successful_deliveries_today: int