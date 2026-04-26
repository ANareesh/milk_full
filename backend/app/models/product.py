"""Product (Milk) model."""
from sqlalchemy import Column, Integer, String, Float, Text, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class ProductType(str, enum.Enum):
    """Product type enumeration."""
    full_cream = "full_cream"
    toned = "toned"
    double_toned = "double_toned"
    skimmed = "skimmed"
    cow_milk = "cow_milk"
    buffalo_milk = "buffalo_milk"
    goat_milk = "goat_milk"


class Product(Base):
    """Milk product model."""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    product_type = Column(SQLEnum(ProductType), nullable=False)
    unit = Column(String(20), default="liter")  # liter, half-liter, etc.
    unit_price = Column(Float, nullable=False)  # Price per unit
    available_quantity = Column(Float, default=0.0)
    image_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    fat_percentage = Column(Float, nullable=True)
    nutritional_info = Column(Text, nullable=True)
    discount_percentage = Column(Float, default=0)  # e.g., 10 for 10% off
    offer_price = Column(Float, nullable=True)  # If set, overrides discount calculation
    offer_description = Column(String(255), nullable=True)  # e.g., "Buy 2 get 1 Free"
    min_quantity_for_offer = Column(Float, default=1)  # Minimum quantity to get offer
    max_quantity_per_order = Column(Float, nullable=True)  # Limit per order (optional)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Product(id={self.id}, name={self.name}, type={self.product_type})>"
