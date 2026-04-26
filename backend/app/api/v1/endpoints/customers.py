"""Customer endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_customer_user, get_current_admin_user, get_current_user
from app.crud.customer import crud_customer
from app.crud.subscription import crud_subscription
from app.schemas.customer import CustomerResponse, CustomerUpdate
from app.schemas.subscription import SubscriptionResponse
from app.models.user import User, UserRole

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("/profile", response_model=CustomerResponse)
async def get_profile(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get my customer profile."""
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    return customer


@router.put("/profile", response_model=CustomerResponse)
async def update_profile(
    profile_data: CustomerUpdate,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Update my customer profile."""
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    
    customer = crud_customer.update(db, customer, profile_data)
    return customer


@router.get("/subscriptions/active", response_model=List[SubscriptionResponse])
async def get_active_subscriptions(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get my active subscriptions."""
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    
    subscriptions = crud_subscription.get_active_by_customer(db, customer.id)
    return subscriptions


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get customer details (admin only)."""
    customer = crud_customer.get(db, customer_id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    return customer


@router.get("/admin/all", response_model=List[CustomerResponse])
async def get_all_customers(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all customers (admin only)."""
    customers = crud_customer.get_multi(db, skip=skip, limit=limit)
    return customers


@router.get("/admin/pending-balance", response_model=List[CustomerResponse])
async def get_customers_with_pending_balance(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get customers with pending balance (admin only)."""
    customers = crud_customer.get_customers_with_pending_balance(db, skip=skip, limit=limit)
    return customers
