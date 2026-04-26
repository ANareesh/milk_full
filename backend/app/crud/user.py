"""User CRUD operations."""
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional

from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import PasswordUtils


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD operations for User model."""

    def get_by_username(self, db: Session, username: str) -> Optional[User]:
        """Get user by username."""
        return db.query(User).filter(User.username == username).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_by_username_or_email(self, db: Session, username: str) -> Optional[User]:
        """Get user by username or email."""
        return db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()

    def create(self, db: Session, obj_in: UserCreate) -> User:
        """Create new user with hashed password."""
        db_obj = User(
            username=obj_in.username,
            email=obj_in.email,
            full_name=obj_in.full_name,
            phone_number=obj_in.phone_number,
            role=obj_in.role,
            hashed_password=PasswordUtils.hash_password(obj_in.password),
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def authenticate(self, db: Session, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password."""
        user = self.get_by_username_or_email(db, username)
        if not user:
            return None
        if not PasswordUtils.verify_password(password, user.hashed_password):
            return None
        return user

    def is_active(self, user: User) -> bool:
        """Check if user is active."""
        return user.is_active

    def is_verified(self, user: User) -> bool:
        """Check if user is verified."""
        return user.is_verified

    def get_by_role(self, db: Session, role: str, skip: int = 0, limit: int = 100):
        """Get users by role."""
        return db.query(User).filter(User.role == role).offset(skip).limit(limit).all()


crud_user = CRUDUser(User)
