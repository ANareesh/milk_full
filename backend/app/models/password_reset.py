"""Password reset token model."""
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import secrets

from app.core.database import Base


class PasswordReset(Base):
    """Password reset token model."""
    __tablename__ = "password_resets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    is_used = Column(Boolean, default=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    @staticmethod
    def generate_token():
        """Generate secure random token."""
        return secrets.token_urlsafe(32)

    def is_valid(self) -> bool:
        """Check if token is still valid."""
        return not self.is_used and datetime.now(self.expires_at.tzinfo) < self.expires_at