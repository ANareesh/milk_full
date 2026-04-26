from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Batch(Base):
    __tablename__ = "batches"
    id = Column(Integer, primary_key=True)
    batch_code = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    # Add more fields as needed (e.g., source, destination, status)