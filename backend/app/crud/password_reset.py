"""CRUD operations for password reset tokens."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.models.password_reset import PasswordReset


class CRUDPasswordReset:
    """CRUD operations for password reset."""

    @staticmethod
    def create_reset_token(db: Session, user_id: int) -> PasswordReset:
        """Create password reset token."""
        token = PasswordReset.generate_token()
        expires_at = datetime.now(timezone.utc) + timedelta(minutes=30)
        
        reset = PasswordReset(
            user_id=user_id,
            token=token,
            expires_at=expires_at
        )
        db.add(reset)
        db.commit()
        db.refresh(reset)
        return reset

    @staticmethod
    def get_by_token(db: Session, token: str) -> PasswordReset | None:
        """Get reset token by token string."""
        return db.query(PasswordReset).filter(PasswordReset.token == token).first()

    @staticmethod
    def mark_as_used(db: Session, reset: PasswordReset):
        """Mark token as used."""
        reset.is_used = True
        db.commit()

    @staticmethod
    def cleanup_expired_tokens(db: Session):
        """Delete expired tokens."""
        db.query(PasswordReset).filter(
            PasswordReset.expires_at < datetime.now(timezone.utc),
            PasswordReset.is_used == False
        ).delete()
        db.commit()


crud_password_reset = CRUDPasswordReset()