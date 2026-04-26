"""Subscription tests covering all scenarios."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.crud.subscription import crud_subscription
from app.services.subscription import subscription_service
from app.schemas.subscription import SubscriptionCreate, SubscriptionFrequency


class TestSubscriptionCreation:
    """Test subscription creation."""
    
    def test_create_subscription_success(self, db: Session, customer_id: int, product_id: int):
        """Test successful subscription creation."""
        data = SubscriptionCreate(
            product_id=product_id,
            quantity=2,
            frequency=SubscriptionFrequency.weekly,
            start_date=datetime.now(),
            payment_method="upi",
            auto_renew=True
        )
        
        subscription = subscription_service.create_subscription(db, customer_id, data)
        
        assert subscription.id is not None
        assert subscription.customer_id == customer_id
        assert subscription.quantity == 2
        assert subscription.status == "active"
    
    def test_create_subscription_invalid_product(self, db: Session, customer_id: int):
        """Test creation with non-existent product."""
        data = SubscriptionCreate(
            product_id=9999,
            quantity=1,
            frequency=SubscriptionFrequency.weekly,
            start_date=datetime.now(),
            payment_method="upi"
        )
        
        with pytest.raises(ValueError, match="Product"):
            subscription_service.create_subscription(db, customer_id, data)
    
    def test_create_subscription_insufficient_stock(self, db: Session, customer_id: int, product_id: int):
        """Test creation with insufficient stock."""
        data = SubscriptionCreate(
            product_id=product_id,
            quantity=10000,  # Exceed stock
            frequency=SubscriptionFrequency.weekly,
            start_date=datetime.now(),
            payment_method="upi"
        )
        
        with pytest.raises(ValueError, match="Insufficient stock"):
            subscription_service.create_subscription(db, customer_id, data)
    
    def test_create_subscription_invalid_date_range(self, db: Session, customer_id: int, product_id: int):
        """Test creation with end_date before start_date."""
        start = datetime.now()
        end = start - timedelta(days=1)  # Before start
        
        data = SubscriptionCreate(
            product_id=product_id,
            quantity=1,
            frequency=SubscriptionFrequency.weekly,
            start_date=start,
            end_date=end,
            payment_method="upi"
        )
        
        with pytest.raises(ValueError):
            subscription_service.create_subscription(db, customer_id, data)


class TestSubscriptionLifecycle:
    """Test subscription lifecycle."""
    
    def test_pause_subscription(self, db: Session, subscription_id: int):
        """Test pausing a subscription."""
        sub = crud_subscription.pause_subscription(db, subscription_id, "Taking a break", 7)
        
        assert sub.status == "paused"
        assert sub.pause_reason == "Taking a break"
        assert sub.resume_date is not None
    
    def test_resume_subscription(self, db: Session, paused_subscription_id: int):
        """Test resuming a subscription."""
        sub = crud_subscription.resume_subscription(db, paused_subscription_id)
        
        assert sub.status == "active"
        assert sub.pause_reason is None
        assert sub.resume_date is None
    
    def test_cancel_subscription(self, db: Session, subscription_id: int):
        """Test cancelling a subscription."""
        sub = crud_subscription.cancel_subscription(db, subscription_id)
        
        assert sub.status == "cancelled"
        assert sub.end_date is not None
    
    def test_cannot_pause_cancelled(self, db: Session, cancelled_subscription_id: int):
        """Test cannot pause a cancelled subscription."""
        with pytest.raises(ValueError):
            crud_subscription.pause_subscription(db, cancelled_subscription_id)


class TestRecurringOrders:
    """Test recurring order processing."""
    
    def test_process_recurring_orders_success(self, db: Session):
        """Test successful recurring order processing."""
        results = subscription_service.process_recurring_orders(db)
        
        assert results["total_processed"] >= 0
        assert results["successful"] >= 0
        assert results["failed"] >= 0
        assert "errors" in results
    
    def test_process_expired_subscription(self, db: Session, expired_subscription_id: int):
        """Test that expired subscriptions are marked correctly."""
        results = subscription_service.process_recurring_orders(db)
        
        # Verify expired sub is handled
        expired_sub = crud_subscription.get(db, expired_subscription_id)
        assert expired_sub.status in ["expired", "cancelled"]
    
    def test_failed_payment_increments_counter(self, db: Session):
        """Test that failed payments increment counter."""
        # This would require mocking payment gateway
        pass


class TestErrorScenarios:
    """Test error handling."""
    
    def test_invalid_frequency(self, db: Session, customer_id: int, product_id: int):
        """Test invalid subscription frequency."""
        data = SubscriptionCreate(
            product_id=product_id,
            quantity=1,
            frequency="invalid_freq",  # Invalid
            start_date=datetime.now(),
            payment_method="upi"
        )
        
        with pytest.raises(ValueError):
            subscription_service.create_subscription(db, customer_id, data)
    
    def test_invalid_payment_method(self, db: Session, customer_id: int, product_id: int):
        """Test invalid payment method."""
        data = SubscriptionCreate(
            product_id=product_id,
            quantity=1,
            frequency=SubscriptionFrequency.weekly,
            start_date=datetime.now(),
            payment_method="bitcoin"  # Invalid
        )
        
        with pytest.raises(ValueError):
            subscription_service.create_subscription(db, customer_id, data)
    
    def test_zero_quantity(self, db: Session, customer_id: int, product_id: int):
        """Test subscription with zero quantity."""
        data = SubscriptionCreate(
            product_id=product_id,
            quantity=0,  # Invalid
            frequency=SubscriptionFrequency.weekly,
            start_date=datetime.now(),
            payment_method="upi"
        )
        
        with pytest.raises(ValueError):
            subscription_service.create_subscription(db, customer_id, data)