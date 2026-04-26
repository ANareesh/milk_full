"""Product schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ProductType(str, Enum):
    """Product type enumeration."""
    full_cream = "full_cream"
    toned = "toned"
    double_toned = "double_toned"
    skimmed = "skimmed"
    cow_milk = "cow_milk"
    buffalo_milk = "buffalo_milk"
    goat_milk = "goat_milk"


class ProductBase(BaseModel):
    """Base product schema."""
    name: str = Field(..., min_length=2, max_length=100)
    description: Optional[str] = None
    product_type: ProductType
    unit: str = Field(default="liter", max_length=20)
    unit_price: float = Field(..., gt=0)
    available_quantity: float = Field(default=0, ge=0)
    image_url: Optional[str] = Field(None, max_length=255)
    fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    nutritional_info: Optional[str] = None
    discount_percentage: float = Field(default=0, ge=0, le=100)
    offer_price: Optional[float] = Field(None, gt=0)
    offer_description: Optional[str] = Field(None, max_length=255)
    min_quantity_for_offer: float = Field(default=1, gt=0)
    max_quantity_per_order: Optional[float] = Field(None, gt=0)


class ProductCreate(ProductBase):
    """Product creation schema."""
    pass


class ProductUpdate(BaseModel):
    """Product update schema."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None
    unit_price: Optional[float] = Field(None, gt=0)
    available_quantity: Optional[float] = Field(None, ge=0)
    image_url: Optional[str] = Field(None, max_length=255)
    fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    nutritional_info: Optional[str] = None
    is_active: Optional[bool] = None
    discount_percentage: float = Field(default=0, ge=0, le=100)
    offer_price: Optional[float] = Field(None, gt=0)
    offer_description: Optional[str] = Field(None, max_length=255)
    min_quantity_for_offer: float = Field(default=1, gt=0)
    max_quantity_per_order: Optional[float] = Field(None, gt=0)


class ProductResponse(ProductBase):
    """Product response schema."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
