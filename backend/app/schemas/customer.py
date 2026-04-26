"""Customer schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CustomerBase(BaseModel):
    """Base customer schema."""
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=50)
    postal_code: str = Field(..., max_length=10)
    preferred_delivery_time: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class CustomerCreate(BaseModel):
    """Customer creation schema."""
    user_id: int
    address: str = Field(..., max_length=255)
    city: str = Field(..., max_length=50)
    postal_code: str = Field(..., max_length=10)
    preferred_delivery_time: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class CustomerUpdate(BaseModel):
    """Customer update schema."""
    address: Optional[str] = Field(None, max_length=255)
    city: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str] = Field(None, max_length=10)
    preferred_delivery_time: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = Field(None, max_length=500)


class CustomerResponse(CustomerBase):
    """Customer response schema."""
    id: int
    user_id: int
    total_amount_due: float
    latitude: Optional[float]
    longitude: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    """Detailed customer response schema."""
    user: Optional[dict] = None
