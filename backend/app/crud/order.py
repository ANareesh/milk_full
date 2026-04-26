"""Order CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from app.crud.base import CRUDBase
from app.models.order import Order, OrderStatus, OrderType
from app.schemas.order import OrderCreate, OrderCreate as OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    """CRUD operations for Order model."""

    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by customer."""
        return db.query(Order).filter(Order.customer_id == customer_id).offset(skip).limit(limit).all()

    def get_by_order_number(self, db: Session, order_number: str) -> Optional[Order]:
        """Get order by order number."""
        return db.query(Order).filter(Order.order_number == order_number).first()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders by status."""
        return db.query(Order).filter(Order.status == status).offset(skip).limit(limit).all()

    def get_pending_orders(self, db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get pending orders."""
        return db.query(Order).filter(Order.status == OrderStatus.pending).offset(skip).limit(limit).all()

    def get_orders_for_delivery(self, db: Session, date: datetime, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders scheduled for delivery on specific date."""
        start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=1)
        return db.query(Order).filter(
            Order.delivery_date >= start_date,
            Order.delivery_date < end_date,
            Order.status != OrderStatus.cancelled
        ).offset(skip).limit(limit).all()

    def update_status(self, db: Session, order: Order, status: str) -> Order:
        """Update order status."""
        order.status = status
        db.add(order)
        db.commit()
        db.refresh(order)
        return order

    def get_subscription_orders(self, db: Session, subscription_id: int, skip: int = 0, limit: int = 100) -> List[Order]:
        """Get orders from subscription."""
        return db.query(Order).filter(
            Order.subscription_id == subscription_id
        ).offset(skip).limit(limit).all()

    def get_customer_orders_by_status(self, db: Session, customer_id: int, status: str) -> List[Order]:
        """Get customer orders by status."""
        return db.query(Order).filter(
            Order.customer_id == customer_id,
            Order.status == status
        ).all()

    def generate_order_number(self, db: Session) -> str:
        """Generate unique order number."""
        import uuid
        order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        while db.query(Order).filter(Order.order_number == order_number).first():
            order_number = f"ORD-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        return order_number


crud_order = CRUDOrder(Order)
