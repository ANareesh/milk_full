"""Subscription service with recurring order automation."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.crud.subscription import crud_subscription
from app.crud.order import crud_order
from app.crud.customer import crud_customer
from app.crud.product import crud_product
from app.crud.payment import crud_payment
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionFrequency
from app.models.order import Order, OrderStatus
from app.models.payment import Payment, PaymentStatus
from app.schemas.subscription import SubscriptionCreate

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Subscription management and automation service."""

    @staticmethod
    def create_subscription(db: Session, customer_id: int, subscription_data: SubscriptionCreate) -> Subscription:
        """Create new subscription."""
        # Validate customer exists
        customer = crud_customer.get(db, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Validate product exists and has stock
        product = crud_product.get(db, subscription_data.product_id)
        if not product:
            raise ValueError(f"Product {subscription_data.product_id} not found")
        
        if product.available_quantity < subscription_data.quantity:
            raise ValueError(f"Insufficient stock. Available: {product.available_quantity}")
        
        # Validate end_date is after start_date
        if subscription_data.end_date and subscription_data.end_date <= subscription_data.start_date:
            raise ValueError("end_date must be after start_date")
        
        # Calculate total amount
        total_amount = product.unit_price * subscription_data.quantity
        
        # Create subscription
        subscription = Subscription(
            customer_id=customer_id,
            product_id=subscription_data.product_id,
            quantity=subscription_data.quantity,
            unit_price=product.unit_price,
            total_amount=total_amount,
            frequency=subscription_data.frequency,
            start_date=subscription_data.start_date,
            end_date=subscription_data.end_date,
            next_delivery_date=subscription_data.start_date,
            payment_method=subscription_data.payment_method,
            auto_renew=subscription_data.auto_renew,
            status=SubscriptionStatus.active,
        )
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"Subscription created: {subscription.id} for customer {customer_id}")
        return subscription

    @staticmethod
    def process_recurring_orders(db: Session) -> dict:
        """
        Process all due subscriptions and create recurring orders.
        This should be run by a scheduled job (e.g., Celery, APScheduler).
        """
        results = {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }
        
        try:
            # Get all subscriptions due for delivery
            due_subscriptions = crud_subscription.get_subscriptions_due_today(db)
            results["total_processed"] = len(due_subscriptions)
            
            for subscription in due_subscriptions:
                try:
                    # Check if subscription has expired
                    if subscription.end_date and subscription.end_date <= datetime.utcnow():
                        subscription.status = SubscriptionStatus.expired
                        db.add(subscription)
                        db.commit()
                        logger.info(f"Subscription {subscription.id} expired")
                        continue
                    
                    # Create recurring order
                    order = SubscriptionService._create_order_from_subscription(db, subscription)
                    
                    # Process payment
                    payment_success = SubscriptionService._process_payment(db, order, subscription)
                    
                    if payment_success:
                        # Update subscription tracking
                        crud_subscription.update_next_delivery_date(db, subscription.id, subscription.frequency)
                        crud_subscription.reset_failed_attempts(db, subscription.id)
                        results["successful"] += 1
                        logger.info(f"Recurring order created for subscription {subscription.id}, order: {order.order_number}")
                    else:
                        # Increment failed attempts
                        failed_attempts = crud_subscription.increment_failed_attempts(db, subscription.id)
                        
                        # Pause after 3 failed attempts
                        if failed_attempts >= 3:
                            crud_subscription.pause_subscription(
                                db, 
                                subscription.id, 
                                pause_reason="Payment failed 3 times",
                                pause_days=7
                            )
                            logger.warning(f"Subscription {subscription.id} paused due to payment failures")
                        
                        results["failed"] += 1
                        results["errors"].append(f"Subscription {subscription.id}: Payment failed")
                
                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"Subscription {subscription.id}: {str(e)}")
                    logger.error(f"Error processing subscription {subscription.id}: {str(e)}")
            
            logger.info(f"Recurring orders processed: {results['successful']} successful, {results['failed']} failed")
            return results
        
        except Exception as e:
            logger.error(f"Error in process_recurring_orders: {str(e)}")
            results["errors"].append(f"Critical error: {str(e)}")
            return results

    @staticmethod
    def _create_order_from_subscription(db: Session, subscription: Subscription) -> Order:
        """Create order from subscription."""
        from app.crud.order import crud_order
        
        # Generate order number
        order_number = crud_order.generate_order_number(db)
        
        # Create order
        order = Order(
            order_number=order_number,
            customer_id=subscription.customer_id,
            product_id=subscription.product_id,
            order_type="subscription",
            quantity=subscription.quantity,
            unit_price=subscription.unit_price,
            total_amount=subscription.total_amount,
            delivery_date=subscription.next_delivery_date,
            special_instructions=f"Recurring order from subscription {subscription.id}",
            status=OrderStatus.pending,
        )
        
        db.add(order)
        db.commit()
        db.refresh(order)
        
        return order

    @staticmethod
    def _process_payment(db: Session, order: Order, subscription: Subscription) -> bool:
        """Process payment for recurring order."""
        try:
            payment = Payment(
                order_id=order.id,
                customer_id=order.customer_id,
                amount=order.total_amount,
                payment_method=subscription.payment_method,
                transaction_id=f"AUTO-{datetime.utcnow().timestamp()}",
                status=PaymentStatus.pending,
            )
            
            db.add(payment)
            db.commit()
            db.refresh(payment)
            
            # Simulate payment processing
            # In production, integrate with payment gateway
            payment.status = PaymentStatus.completed
            db.add(payment)
            db.commit()
            
            # Update order status
            order.status = OrderStatus.confirmed
            db.add(order)
            db.commit()
            
            logger.info(f"Payment processed for order {order.order_number}")
            return True
        
        except Exception as e:
            logger.error(f"Payment processing failed for order {order.order_number}: {str(e)}")
            return False

    @staticmethod
    def update_subscription(db: Session, subscription_id: int, update_data: dict) -> Subscription:
        """Update subscription details."""
        subscription = crud_subscription.get(db, subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        if subscription.status == SubscriptionStatus.cancelled:
            raise ValueError("Cannot update cancelled subscription")
        
        # Validate if any restricted fields are being changed
        if "status" in update_data and update_data["status"] != subscription.status:
            raise ValueError("Use pause/resume/cancel methods to change status")
        
        # Update fields
        for field, value in update_data.items():
            if value is not None and hasattr(subscription, field):
                setattr(subscription, field, value)
        
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
        
        logger.info(f"Subscription {subscription_id} updated")
        return subscription

    @staticmethod
    def get_subscription_stats(db: Session, customer_id: int) -> dict:
        """Get subscription statistics for customer."""
        try:
            subscriptions = crud_subscription.get_by_customer(db, customer_id)
            
            # Use string comparison instead of enum
            active = sum(1 for s in subscriptions if s.status == "active")
            paused = sum(1 for s in subscriptions if s.status == "paused")
            cancelled = sum(1 for s in subscriptions if s.status == "cancelled")
            
            # Handle None total_amount
            total_value = sum(s.total_amount for s in subscriptions if s.status == "active" and s.total_amount)
            
            return {
                "total": len(subscriptions),
                "active": active,
                "paused": paused,
                "cancelled": cancelled,
                "total_monthly_value": total_value * 4 if total_value else 0,
            }
        except Exception as e:
            logger.error(f"Error in get_subscription_stats: {str(e)}")
            return {
                "total": 0,
                "active": 0,
                "paused": 0,
                "cancelled": 0,
                "total_monthly_value": 0,
            }


subscription_service = SubscriptionService()