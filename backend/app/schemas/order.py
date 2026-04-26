"""Order schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Order status enumeration."""
    pending = "pending"
    confirmed = "confirmed"
    out_for_delivery = "out_for_delivery"
    delivered = "delivered"
    cancelled = "cancelled"
    returned = "returned"


class OrderType(str, Enum):
    """Order type enumeration."""
    subscription = "subscription"
    one_time = "one_time"


class OrderBase(BaseModel):
    """Base order schema."""
    product_id: int
    quantity: float = Field(..., gt=0)
    special_instructions: Optional[str] = None


class OrderCreate(OrderBase):
    """Order creation schema."""
    delivery_date: datetime


class OrderCreateOneTime(BaseModel):
    """One-time order creation schema."""
    product_id: int
    quantity: float = Field(..., gt=0)
    delivery_date: datetime
    special_instructions: Optional[str] = None
    delivery_address: str = Field(..., min_length=3, max_length=255)



class OrderResponse(BaseModel):
    """Order response schema."""
    id: int
    order_number: str
    customer_id: int
    product_id: int
    order_type: OrderType
    quantity: float
    unit_price: float
    total_amount: float
    status: OrderStatus
    delivery_date: datetime
    special_instructions: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class OrderDetailResponse(OrderResponse):
    """Detailed order response schema."""
    product: Optional[dict] = None
    delivery: Optional[dict] = None
