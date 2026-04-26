"""Subscription endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
import logging

from app.core.database import get_db
from app.core.dependencies import get_current_customer_user, get_current_admin_user
from app.models.user import User
from app.crud.subscription import crud_subscription
from app.crud.product import crud_product
from app.crud.customer import crud_customer
from app.schemas.subscription import (
    SubscriptionCreate, SubscriptionResponse, SubscriptionUpdate,
    SubscriptionPause, SubscriptionListResponse
)
from app.services.subscription import subscription_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


# Helper function to get customer from user
def get_customer_from_user(db: Session, user_id: int):
    """Get customer from current user."""
    customer = crud_customer.get_by_user_id(db, user_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer profile not found"
        )
    return customer


@router.post("/", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription_data: SubscriptionCreate,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Create new subscription."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        
        # Validate product exists
        product = crud_product.get(db, subscription_data.product_id)
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found"
            )
        
        # Validate stock
        if product.available_quantity < subscription_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock. Available: {product.available_quantity}"
            )
        
        subscription = subscription_service.create_subscription(
            db, customer.id, subscription_data
        )
        
        logger.info(f"Subscription created: {subscription.id} by customer {customer.id}")
        return subscription
    
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )


@router.get("/stats/summary", response_model=dict)
async def get_subscription_stats(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get subscription statistics."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        stats = subscription_service.get_subscription_stats(db, customer.id)
        return stats
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch statistics"
        )


@router.get("/my-subscriptions", response_model=SubscriptionListResponse)
async def get_my_subscriptions(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    filter_status: str = Query(None),
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get customer's subscriptions."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        
        subscriptions = crud_subscription.get_by_customer(db, customer.id, skip=skip, limit=limit)
        
        # Filter by status if provided
        if filter_status:
            subscriptions = [s for s in subscriptions if s.status == filter_status]
        
        # Attach product details
        for sub in subscriptions:
            product = crud_product.get(db, sub.product_id)
            if product:
                sub.product_name = product.name
                sub.product_unit_price = product.unit_price
        
        # Count stats
        all_subs = crud_subscription.get_by_customer(db, customer.id)
        active_count = sum(1 for s in all_subs if s.status == "active")
        paused_count = sum(1 for s in all_subs if s.status == "paused")
        cancelled_count = sum(1 for s in all_subs if s.status == "cancelled")
        
        return {
            "subscriptions": subscriptions,
            "total": len(all_subs),
            "active": active_count,
            "paused": paused_count,
            "cancelled": cancelled_count,
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscriptions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscriptions"
        )


@router.get("/{subscription_id}", response_model=SubscriptionResponse)
async def get_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get subscription details."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        subscription = crud_subscription.get(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Verify ownership
        if subscription.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this subscription"
            )
        
        # Attach product details
        product = crud_product.get(db, subscription.product_id)
        if product:
            subscription.product_name = product.name
            subscription.product_unit_price = product.unit_price
        
        return subscription
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch subscription"
        )


@router.put("/{subscription_id}", response_model=SubscriptionResponse)
async def update_subscription(
    subscription_id: int,
    update_data: SubscriptionUpdate,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Update subscription."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        subscription = crud_subscription.get(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        # Verify ownership
        if subscription.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to update this subscription"
            )
        
        # Validate new quantity if provided
        if update_data.quantity:
            product = crud_product.get(db, subscription.product_id)
            if product and product.available_quantity < update_data.quantity:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Insufficient stock. Available: {product.available_quantity}"
                )
        
        # Update
        for field, value in update_data.dict(exclude_unset=True).items():
            if value is not None:
                setattr(subscription, field, value)
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"Subscription {subscription_id} updated by customer {customer.id}")
        return subscription
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update subscription"
        )


@router.post("/{subscription_id}/pause", response_model=SubscriptionResponse)
async def pause_subscription(
    subscription_id: int,
    pause_data: SubscriptionPause,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Pause subscription."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        subscription = crud_subscription.get(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        if subscription.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        if subscription.status != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot pause subscription with status: {subscription.status}"
            )
        
        subscription = crud_subscription.pause_subscription(
            db, subscription_id, pause_data.pause_reason, pause_data.pause_days
        )
        
        logger.info(f"Subscription {subscription_id} paused by customer {customer.id}")
        return subscription
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error pausing subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to pause subscription"
        )


@router.post("/{subscription_id}/resume", response_model=SubscriptionResponse)
async def resume_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Resume subscription."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        subscription = crud_subscription.get(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        if subscription.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        if subscription.status != "paused":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot resume subscription with status: {subscription.status}"
            )
        
        subscription = crud_subscription.resume_subscription(db, subscription_id)
        logger.info(f"Subscription {subscription_id} resumed by customer {customer.id}")
        return subscription
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to resume subscription"
        )


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_subscription(
    subscription_id: int,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Cancel subscription."""
    try:
        customer = get_customer_from_user(db, current_user.id)
        subscription = crud_subscription.get(db, subscription_id)
        
        if not subscription:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Subscription not found"
            )
        
        if subscription.customer_id != customer.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized"
            )
        
        crud_subscription.cancel_subscription(db, subscription_id)
        logger.info(f"Subscription {subscription_id} cancelled by customer {customer.id}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error cancelling subscription: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to cancel subscription"
        )


# Admin endpoint to process recurring orders (called by scheduler)
@router.post("/admin/process-recurring", status_code=status.HTTP_200_OK)
async def process_recurring_orders(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Process all due recurring orders. (Admin & Scheduler only)"""
    try:
        results = subscription_service.process_recurring_orders(db)
        logger.info(f"Recurring orders processed: {results['successful']} successful, {results['failed']} failed")
        return results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing recurring orders: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process recurring orders"
        )