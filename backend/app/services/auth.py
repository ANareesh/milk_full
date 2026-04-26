"""Authentication service."""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.crud.user import crud_user
from app.core.security import PasswordUtils, JWTUtils
from app.schemas.user import UserCreate, TokenResponse
from app.models.user import User
from app.crud.password_reset import crud_password_reset
from app.models.password_reset import PasswordReset
logger = logging.getLogger(__name__)


class AuthService:
    """Authentication service."""

    @staticmethod
    def register_user(db: Session, user_data: UserCreate) -> User:
        """Register new user."""
        # Check if username already exists
        existing_user = crud_user.get_by_username(db, user_data.username)
        if existing_user:
            raise ValueError(f"Username '{user_data.username}' already exists")

        # Check if email already exists
        existing_email = crud_user.get_by_email(db, user_data.email)
        if existing_email:
            raise ValueError(f"Email '{user_data.email}' already exists")

        # Create new user
        user = crud_user.create(db, user_data)
        logger.info(f"User registered successfully: {user.username}")
        return user

    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with credentials."""
        user = crud_user.authenticate(db, username, password)
        if not user:
            logger.warning(f"Authentication failed for username: {username}")
            return None

        if not user.is_active:
            logger.warning(f"Login attempt by inactive user: {username}")
            return None

        logger.info(f"User authenticated successfully: {username}")
        return user

    @staticmethod
    def login(db: Session, username: str, password: str) -> Optional[TokenResponse]:
        """Login user and return tokens."""
        user = AuthService.authenticate_user(db, username, password)
        if not user:
            return None

        # Generate tokens
        access_token_data = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": getattr(user.role, "value", str(user.role)),
            }
        access_token = JWTUtils.create_access_token(access_token_data)
        refresh_token = JWTUtils.create_refresh_token(access_token_data)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    @staticmethod
    def refresh_access_token(db: Session, refresh_token: str) -> Optional[TokenResponse]:
        """Generate new access token from refresh token."""
        payload = JWTUtils.decode_token(refresh_token)
        if payload is None:
            return None

        if not JWTUtils.verify_token_type(payload, "refresh"):
            return None

        user_id = payload.get("sub")
        user = crud_user.get(db, user_id)
        if not user or not user.is_active:
            return None

        # Generate new tokens
        access_token_data = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "role": getattr(user.role, "value", str(user.role)),
        }
        new_access_token = JWTUtils.create_access_token(access_token_data)
        new_refresh_token = JWTUtils.create_refresh_token(access_token_data)

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode token."""
        return JWTUtils.decode_token(token)

    @staticmethod
    def request_password_reset(db: Session, email: str) -> bool:
        """Request password reset by email."""
        from app.services.email import EmailService
        from app.crud.password_reset import crud_password_reset
        
        user = crud_user.get_by_email(db, email)
        if not user:
            # Don't reveal if email exists (security best practice)
            return True  # Return success anyway
        
        # Invalidate old tokens
        old_tokens = db.query(PasswordReset).filter(
            PasswordReset.user_id == user.id,
            PasswordReset.is_used == False
        ).all()
        for token in old_tokens:
            token.is_used = True
        db.commit()
        
        # Create new token
        reset = crud_password_reset.create_reset_token(db, user.id)
        
        # Send email
        email_sent = EmailService.send_password_reset_email(
            email=user.email,
            reset_token=reset.token,
            user_name=user.full_name
        )
        
        return email_sent

    @staticmethod
    def verify_reset_token(db: Session, token: str) -> bool:
        """Verify if reset token is valid."""
        from app.crud.password_reset import crud_password_reset
        
        reset = crud_password_reset.get_by_token(db, token)
        if not reset:
            return False
        return reset.is_valid()

    @staticmethod
    def reset_password(db: Session, token: str, new_password: str) -> bool:
        """Reset password with valid token."""
        from app.crud.password_reset import crud_password_reset
        
        reset = crud_password_reset.get_by_token(db, token)
        if not reset or not reset.is_valid():
            return False
        
        user = crud_user.get(db, reset.user_id)
        if not user:
            return False
        
        # Update password
        user.hashed_password = PasswordUtils.hash_password(new_password)
        db.commit()
        
        # Mark token as used
        crud_password_reset.mark_as_used(db, reset)
        
        return True


auth_service = AuthService()
