from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MilkCollectionBase(BaseModel):
    quantity_liters: float = Field(..., gt=0)
    fat_percentage: Optional[float] = Field(None, ge=0, le=100)
    snf_percentage: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = Field(None, max_length=255)

class MilkCollectionCreate(MilkCollectionBase):
    farmer_id: int

class MilkCollectionResponse(MilkCollectionBase):
    id: int
    farmer_id: int
    collection_time: datetime

    class Config:
        orm_mode = True