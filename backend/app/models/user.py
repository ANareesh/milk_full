"""User model."""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from datetime import datetime
import enum
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.milk_collection import MilkCollection


class UserRole(str, enum.Enum):
    """User role enumeration."""
    admin = "admin"
    agent = "agent"
    customer = "customer"


class User(Base):
    """User base model for all user types."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone_number = Column(String(20), nullable=True)
    role = Column(SQLEnum(UserRole), nullable=False, index=True)
    is_active = Column(Boolean, default=True, index=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    milk_collections = relationship("MilkCollection", back_populates="farmer")
    # Relationships to Document and Feedback kept as foreign keys only to avoid initialization issues
    documents = relationship("Document", back_populates="user")
    feedbacks = relationship("Feedback", back_populates="user")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username={self.username}, email={self.email}, role={self.role})>"
