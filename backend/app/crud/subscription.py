"""Subscription CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionFrequency
from app.schemas.subscription import SubscriptionCreate, SubscriptionUpdate


class CRUDSubscription(CRUDBase[Subscription, SubscriptionCreate, SubscriptionUpdate]):
    """CRUD operations for Subscription model."""

    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get subscriptions by customer."""
        return db.query(Subscription).filter(
            Subscription.customer_id == customer_id
        ).order_by(Subscription.created_at.desc()).offset(skip).limit(limit).all()

    def get_active_subscriptions(self, db: Session, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get all active subscriptions."""
        return db.query(Subscription).filter(
            Subscription.status == "active"
        ).all()

    def get_subscriptions_due_today(self, db: Session) -> List[Subscription]:
        """Get subscriptions due for delivery today."""
        today = datetime.utcnow().date()
        return db.query(Subscription).filter(
            Subscription.status == "active",
            Subscription.next_delivery_date <= datetime.combine(today, datetime.min.time()),
            Subscription.auto_renew == True
        ).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Subscription]:
        """Get subscriptions by status."""
        return db.query(Subscription).filter(
            Subscription.status == status
        ).offset(skip).limit(limit).all()

    def pause_subscription(self, db: Session, subscription_id: int, pause_reason: Optional[str] = None, pause_days: int = 7) -> Subscription:
        """Pause subscription."""
        subscription = self.get(db, subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status != "active":
            raise ValueError(f"Cannot pause subscription with status: {subscription.status}")
        
        subscription.status = "paused"
        subscription.pause_reason = pause_reason
        subscription.resume_date = datetime.utcnow() + timedelta(days=pause_days)
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    def resume_subscription(self, db: Session, subscription_id: int) -> Subscription:
        """Resume subscription."""
        subscription = self.get(db, subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status != "paused":
            raise ValueError(f"Cannot resume subscription with status: {subscription.status}")
        
        subscription.status = "active"
        subscription.pause_reason = None
        subscription.resume_date = None
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    def cancel_subscription(self, db: Session, subscription_id: int, reason: Optional[str] = None) -> Subscription:
        """Cancel subscription."""
        subscription = self.get(db, subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status == "cancelled":
            raise ValueError("Subscription is already cancelled")
        
        subscription.status = SubscriptionStatus.cancelled
        subscription.end_date = datetime.utcnow()
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription

    def increment_failed_attempts(self, db: Session, subscription_id: int) -> int:
        """Increment failed delivery attempts."""
        subscription = self.get(db, subscription_id)
        subscription.failed_attempts = (subscription.failed_attempts or 0) + 1
        db.add(subscription)
        db.commit()
        return subscription.failed_attempts

    def reset_failed_attempts(self, db: Session, subscription_id: int):
        """Reset failed attempts after successful order."""
        subscription = self.get(db, subscription_id)
        subscription.failed_attempts = 0
        db.add(subscription)
        db.commit()

    def update_next_delivery_date(self, db: Session, subscription_id: int, frequency: SubscriptionFrequency):
        """Calculate and update next delivery date."""
        subscription = self.get(db, subscription_id)
        
        # Calculate days to add
        days_to_add = {
            SubscriptionFrequency.daily: 1,
            SubscriptionFrequency.weekly: 7,
            SubscriptionFrequency.bi_weekly: 14,
            SubscriptionFrequency.monthly: 30,
        }
        
        subscription.next_delivery_date = datetime.utcnow() + timedelta(days=days_to_add[frequency])
        subscription.last_order_date = datetime.utcnow()
        subscription.total_orders_created = (subscription.total_orders_created or 0) + 1
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        return subscription


crud_subscription = CRUDSubscription(Subscription)
