from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey, String
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class MilkCollection(Base):
    __tablename__ = "milk_collections"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quantity_liters = Column(Float, nullable=False)
    fat_percentage = Column(Float, nullable=True)
    snf_percentage = Column(Float, nullable=True)
    collection_time = Column(DateTime, default=datetime.utcnow)
    notes = Column(String(255), nullable=True)
    batch_id = Column(Integer, ForeignKey("batches.id"), nullable=True)
    farmer = relationship("User", back_populates="milk_collections")
    batch = relationship("Batch")
