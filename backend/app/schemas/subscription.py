# """Subscription schemas."""
# from pydantic import BaseModel, Field
# from typing import Optional
# from datetime import datetime
# from enum import Enum


# class SubscriptionFrequency(str, Enum):
#     """Subscription frequency enumeration."""
#     daily = "daily"
#     weekly = "weekly"
#     monthly = "monthly"


# class SubscriptionStatus(str, Enum):
#     """Subscription status enumeration."""
#     active = "active"
#     paused = "paused"
#     cancelled = "cancelled"
#     expired = "expired"


# class SubscriptionBase(BaseModel):
#     """Base subscription schema."""
#     customer_id: int
#     product_id: int
#     frequency: SubscriptionFrequency
#     quantity: float = Field(..., gt=0)
#     auto_renewal: bool = Field(default=True)
#     notes: Optional[str] = Field(None, max_length=255)


# class SubscriptionCreate(BaseModel):
#     """Subscription creation schema."""
#     product_id: int
#     frequency: SubscriptionFrequency
#     quantity: float = Field(..., gt=0)
#     start_date: datetime
#     end_date: Optional[datetime] = None
#     auto_renewal: bool = Field(default=True)
#     notes: Optional[str] = Field(None, max_length=255)


# class SubscriptionUpdate(BaseModel):
#     """Subscription update schema."""
#     quantity: Optional[float] = Field(None, gt=0)
#     frequency: Optional[SubscriptionFrequency] = None
#     status: Optional[SubscriptionStatus] = None
#     auto_renewal: Optional[bool] = None
#     notes: Optional[str] = Field(None, max_length=255)


# class SubscriptionResponse(SubscriptionBase):
#     """Subscription response schema."""
#     id: int
#     status: SubscriptionStatus
#     price_per_unit: float
#     total_price: float
#     start_date: datetime
#     end_date: Optional[datetime]
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True


"""Subscription schemas."""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
from enum import Enum


class SubscriptionFrequency(str, Enum):
    """Subscription frequency."""
    daily = "daily"
    weekly = "weekly"
    bi_weekly = "bi_weekly"
    monthly = "monthly"


class SubscriptionStatus(str, Enum):
    """Subscription status."""
    active = "active"
    paused = "paused"
    cancelled = "cancelled"
    expired = "expired"


class SubscriptionCreate(BaseModel):
    """Create subscription schema."""
    product_id: int = Field(..., gt=0)
    quantity: int = Field(..., gt=0, le=1000)
    frequency: SubscriptionFrequency
    start_date: datetime
    end_date: Optional[datetime] = None
    payment_method: str = Field(..., min_length=3)
    auto_renew: bool = True

    @validator('end_date')
    def end_date_after_start(cls, v, values):
        if v and 'start_date' in values and v <= values['start_date']:
            raise ValueError('end_date must be after start_date')
        return v

    @validator('payment_method')
    def validate_payment_method(cls, v):
        valid = ['upi', 'card', 'cash']
        if v.lower() not in valid:
            raise ValueError(f'payment_method must be one of {valid}')
        return v.lower()


class SubscriptionUpdate(BaseModel):
    """Update subscription schema."""
    quantity: Optional[int] = Field(None, gt=0, le=1000)
    frequency: Optional[SubscriptionFrequency] = None
    end_date: Optional[datetime] = None
    auto_renew: Optional[bool] = None


class SubscriptionPause(BaseModel):
    """Pause subscription schema."""
    pause_reason: Optional[str] = None
    pause_days: int = Field(..., gt=0, le=365)  # Pause for N days


class SubscriptionResponse(BaseModel):
    """Subscription response schema."""
    id: int
    customer_id: int
    product_id: int
    quantity: int
    unit_price: float
    total_amount: float
    frequency: SubscriptionFrequency
    status: SubscriptionStatus
    start_date: datetime
    end_date: Optional[datetime]
    next_delivery_date: datetime
    payment_method: str
    auto_renew: bool
    total_orders_created: int
    last_order_date: Optional[datetime]
    failed_attempts: int
    created_at: datetime
    updated_at: datetime
    
    # Nested product details
    product_name: Optional[str] = None
    product_unit_price: Optional[float] = None
    
    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Subscription list response."""
    subscriptions: list[SubscriptionResponse]
    total: int
    active: int
    paused: int
    cancelled: int