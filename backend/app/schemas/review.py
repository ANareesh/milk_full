"""Review schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ReviewCreate(BaseModel):
    """Review creation schema."""
    order_id: int
    product_id: int
    rating: float = Field(..., ge=1, le=5)
    quality_rating: Optional[float] = Field(None, ge=1, le=5)
    delivery_rating: Optional[float] = Field(None, ge=1, le=5)
    agent_rating: Optional[float] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    is_recommended: bool = Field(default=True)


class ReviewUpdate(BaseModel):
    """Review update schema."""
    rating: Optional[float] = Field(None, ge=1, le=5)
    quality_rating: Optional[float] = Field(None, ge=1, le=5)
    delivery_rating: Optional[float] = Field(None, ge=1, le=5)
    agent_rating: Optional[float] = Field(None, ge=1, le=5)
    comment: Optional[str] = None
    is_recommended: Optional[bool] = None


class ReviewResponse(BaseModel):
    """Review response schema."""
    id: int
    customer_id: int
    order_id: int
    product_id: int
    rating: float
    quality_rating: Optional[float]
    delivery_rating: Optional[float]
    agent_rating: Optional[float]
    comment: Optional[str]
    is_recommended: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
