"""Delivery schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DeliveryStatus(str, Enum):
    """Delivery status enumeration."""
    pending = "pending"
    in_progress = "in_progress"
    delivered = "delivered"
    failed = "failed"
    returning = "returning"


class DeliveryBase(BaseModel):
    """Base delivery schema."""
    order_id: int
    scheduled_date: datetime


class DeliveryCreate(DeliveryBase):
    """Delivery creation schema."""
    pass


class DeliveryAssignAgent(BaseModel):
    """Assign agent to delivery schema."""
    agent_id: int


class DeliveryUpdateStatus(BaseModel):
    """Update delivery status schema."""
    status: DeliveryStatus
    delivery_notes: Optional[str] = None
    failed_reason: Optional[str] = None


class DeliveryOTPVerify(BaseModel):
    """OTP verification schema."""
    otp: str = Field(..., min_length=6, max_length=6)


class DeliveryCompleteRequest(BaseModel):
    """Complete delivery request schema."""
    delivery_notes: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class DeliveryResponse(BaseModel):
    """Delivery response schema."""
    id: int
    order_id: int
    agent_id: Optional[int] = None
    status: DeliveryStatus
    scheduled_date: datetime
    actual_delivery_date: Optional[datetime] = None
    delivery_notes: Optional[str] = None
    delivery_otp: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    
    # Nested order details
    order_number: Optional[str] = None
    customer_id: Optional[int] = None
    total_amount: Optional[float] = None
    
    # Nested agent details
    agent_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        
class DeliveryFailRequest(BaseModel):
    """Fail delivery request schema."""
    reason: Optional[str] = "Unknown"