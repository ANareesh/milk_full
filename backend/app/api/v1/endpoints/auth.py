# """Authentication endpoints."""
from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.user import UserCreate, TokenRequest, TokenResponse, UserResponse
from app.services.auth import auth_service
from app.crud.customer import crud_customer
from app.crud.agent import crud_agent
from app.models.user import UserRole
from app.schemas.customer import CustomerCreate
from app.schemas.agent import AgentCreate
from app.services.email import EmailService
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
import logging

from app.crud.user import crud_user
from app.crud.password_reset import crud_password_reset
from app.services.email import EmailService
from app.core.security import PasswordUtils, JWTUtils
from app.schemas.user import UserCreate, TokenResponse
from app.models.user import User
from app.models.password_reset import PasswordReset

router = APIRouter(tags=["authentication"])


@router.post("/auth/register/customer", response_model=UserResponse)
async def register_customer(
    user_data: UserCreate, db: Session = Depends(get_db)
):
    """Register new customer."""
    try:
        # Ensure role is customer
        user_data.role = UserRole.customer
        user = auth_service.register_user(db, user_data)
        
        # Create customer profile
        customer = CustomerCreate(
            user_id=user.id,
            address="",
            city="",
            postal_code="",
        )
        crud_customer.create(db, customer)
        
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/auth/register/agent", response_model=UserResponse)
async def register_agent(
    user_data: UserCreate, agent_code: str, db: Session = Depends(get_db)
):
    """Register new delivery agent."""
    try:
        user_data.role = UserRole.agent
        user = auth_service.register_user(db, user_data)
        
        # Create agent profile
        agent = AgentCreate(
            user_id=user.id,
            agent_code=agent_code,
        )
        crud_agent.create(db, agent)
        
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/auth/login", response_model=TokenResponse)
async def login(
    credentials: TokenRequest, db: Session = Depends(get_db)
):
    """Login user and get access token."""
    token_response = auth_service.login(db, credentials.username, credentials.password)
    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    return token_response


@router.post("/auth/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: dict, db: Session = Depends(get_db)
):
    """Refresh access token."""
    refresh_token = refresh_request.get("refresh_token")
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Refresh token is required",
        )
    
    token_response = auth_service.refresh_access_token(db, refresh_token)
    if not token_response:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    return token_response



from pydantic import BaseModel, EmailStr

class ForgotPasswordRequest(BaseModel):
    """Forgot password request."""
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    """Reset password request."""
    token: str
    new_password: str
    confirm_password: str

class TokenVerificationResponse(BaseModel):
    """Token verification response."""
    valid: bool
    message: str


@router.post("/auth/forgot-password", response_model=dict)
async def forgot_password(
    request: ForgotPasswordRequest, db: Session = Depends(get_db)
):
    """Request password reset."""
    success = auth_service.request_password_reset(db, request.email)
    return {
        "message": "If email exists, password reset link has been sent",
        "success": success
    }


@router.get("/auth/verify-reset-token/{token}")
async def verify_reset_token(token: str, db: Session = Depends(get_db)):
    """Verify reset token is valid."""
    valid = auth_service.verify_reset_token(db, token)
    return {
        "valid": valid,
        "message": "Token is valid" if valid else "Token is invalid or expired"
    }


@router.post("/auth/reset-password", response_model=dict)
async def reset_password(
    request: ResetPasswordRequest, db: Session = Depends(get_db)
):
    """Reset password with token."""
    if request.new_password != request.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Passwords do not match"
        )
    
    success = auth_service.reset_password(db, request.token, request.new_password)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    return {
        "message": "Password has been reset successfully",
        "success": True
    }
@router.post("/auth/register/admin", response_model=UserResponse)
async def register_admin(
    user_data: UserCreate, db: Session = Depends(get_db)
):
    """Register new admin user (admin creation endpoint)."""
    try:
        # Ensure role is admin
        user_data.role = UserRole.admin
        user = auth_service.register_user(db, user_data)
        
        return user
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
