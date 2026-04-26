"""Delivery CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.delivery import Delivery, DeliveryStatus
from app.schemas.delivery import DeliveryCreate, DeliveryUpdateStatus


class CRUDDelivery(CRUDBase[Delivery, DeliveryCreate, DeliveryUpdateStatus]):
    """CRUD operations for Delivery model."""

    def get_by_order(self, db: Session, order_id: int) -> Optional[Delivery]:
        """Get delivery by order."""
        return db.query(Delivery).filter(Delivery.order_id == order_id).first()

    def get_by_agent(self, db: Session, agent_id: int, skip: int = 0, limit: int = 100) -> List[Delivery]:
        """Get deliveries assigned to agent."""
        return db.query(Delivery).filter(Delivery.agent_id == agent_id).offset(skip).limit(limit).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Delivery]:
        """Get deliveries by status."""
        return db.query(Delivery).filter(Delivery.status == status).offset(skip).limit(limit).all()

    def get_pending_deliveries(self, db: Session, skip: int = 0, limit: int = 100) -> List[Delivery]:
        """Get pending deliveries."""
        return db.query(Delivery).filter(Delivery.status == DeliveryStatus.pending).offset(skip).limit(limit).all()

    def get_agent_pending_deliveries(self, db: Session, agent_id: int) -> List[Delivery]:
        """Get pending deliveries for agent."""
        return db.query(Delivery).filter(
            Delivery.agent_id == agent_id,
            Delivery.status.in_([DeliveryStatus.pending, DeliveryStatus.in_progress])
        ).all()

    def get_agent_delivered(self, db: Session, agent_id: int, skip: int = 0, limit: int = 100) -> List[Delivery]:
        """Get delivered orders by agent."""
        return db.query(Delivery).filter(
            Delivery.agent_id == agent_id,
            Delivery.status == DeliveryStatus.delivered
        ).offset(skip).limit(limit).all()

    def assign_agent(self, db: Session, delivery: Delivery, agent_id: int) -> Delivery:
        """Assign agent to delivery."""
        delivery.agent_id = agent_id
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery

    def update_status(self, db: Session, delivery: Delivery, status: str) -> Delivery:
        """Update delivery status."""
        delivery.status = status
        if status == DeliveryStatus.delivered:
            delivery.actual_delivery_date = datetime.utcnow()
            delivery.delivery_time = datetime.utcnow()
        elif status == DeliveryStatus.in_progress:
            delivery.pickup_time = datetime.utcnow()
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery

    def mark_delivered(self, db: Session, delivery: Delivery, latitude: Optional[float] = None, longitude: Optional[float] = None) -> Delivery:
        """Mark delivery as completed."""
        delivery.status = DeliveryStatus.delivered
        delivery.actual_delivery_date = datetime.utcnow()
        delivery.delivery_time = datetime.utcnow()
        if latitude and longitude:
            delivery.latitude_delivered = latitude
            delivery.longitude_delivered = longitude
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery

    def mark_failed(self, db: Session, delivery: Delivery, reason: str) -> Delivery:
        """Mark delivery as failed."""
        delivery.status = DeliveryStatus.failed
        delivery.failed_reason = reason
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        return delivery

    def verify_otp(self, db: Session, delivery: Delivery, otp: str) -> bool:
        """Verify delivery OTP."""
        # Convert both to strings for comparison to avoid type mismatch
        stored_otp = str(delivery.delivery_otp).strip()
        provided_otp = str(otp).strip()
        
        if stored_otp == provided_otp:
            delivery.otp_verified = True
            delivery.status = DeliveryStatus.delivered
            db.add(delivery)
            db.commit()
            db.refresh(delivery)
            return True
        return False


crud_delivery = CRUDDelivery(Delivery)
