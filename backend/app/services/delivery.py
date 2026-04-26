"""Delivery service."""
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
import logging
import random
import string

from app.crud.delivery import crud_delivery
from app.crud.order import crud_order
from app.crud.agent import crud_agent
from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import OrderStatus

logger = logging.getLogger(__name__)


class DeliveryService:
    """Delivery management service."""

    @staticmethod
    def assign_agent_to_delivery(db: Session, delivery_id: int, agent_id: int) -> Delivery:
        """Assign delivery agent."""
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")

        agent = crud_agent.get(db, agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")

        if delivery.agent_id:
            logger.warning(f"Delivery already assigned to agent {delivery.agent_id}")

        # Assign agent
        delivery = crud_delivery.assign_agent(db, delivery, agent_id)
        
        # Generate OTP for delivery
        otp = DeliveryService.generate_delivery_otp()
        delivery.delivery_otp = otp
        db.add(delivery)
        db.commit()
        db.refresh(delivery)

        logger.info(f"Agent {agent_id} assigned to delivery {delivery_id}")
        return delivery

    @staticmethod
    def start_delivery(db: Session, delivery_id: int) -> Delivery:
        """Mark delivery as in progress."""
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")

        if delivery.status not in [DeliveryStatus.pending]:
            raise ValueError(f"Cannot start delivery with status: {delivery.status}")

        delivery = crud_delivery.update_status(db, delivery, DeliveryStatus.in_progress)
        logger.info(f"Delivery {delivery_id} started")
        return delivery

    @staticmethod
    def complete_delivery(
        db: Session, delivery_id: int, latitude: Optional[float] = None, longitude: Optional[float] = None
    ) -> Delivery:
        """Mark delivery as completed."""
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")

        if delivery.status != DeliveryStatus.in_progress:
            raise ValueError(f"Cannot complete delivery with status: {delivery.status}")

        delivery = crud_delivery.mark_delivered(db, delivery, latitude, longitude)
        
        # Update order status
        order = crud_order.get(db, delivery.order_id)
        if order:
            order.status = OrderStatus.delivered
            db.add(order)
            db.commit()

        # Update agent earnings
        if delivery.agent_id:
            agent = crud_agent.get(db, delivery.agent_id)
            if agent and order:
                commission = order.total_amount * 0.05  # 5% commission
                crud_agent.update_earnings(db, agent, commission)
                crud_agent.increment_deliveries(db, agent)

        logger.info(f"Delivery {delivery_id} completed")
        return delivery

    @staticmethod
    def fail_delivery(db: Session, delivery_id: int, reason: str) -> Delivery:
        """Mark delivery as failed."""
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")

        delivery = crud_delivery.mark_failed(db, delivery, reason)
        logger.info(f"Delivery {delivery_id} marked as failed: {reason}")
        return delivery

    @staticmethod
    def verify_delivery_otp(db: Session, delivery_id: int, otp: str) -> bool:
        """Verify delivery OTP."""
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")

        if not delivery.delivery_otp:
            raise ValueError("No OTP set for this delivery")

        if not otp or len(str(otp).strip()) != 6:
            raise ValueError("OTP must be 6 digits")

        verified = crud_delivery.verify_otp(db, delivery, otp)
        if verified:
            logger.info(f"OTP verified for delivery {delivery_id}")
        else:
            logger.warning(f"OTP verification failed for delivery {delivery_id}. Stored: {delivery.delivery_otp}, Provided: {otp}")
        
        return verified

    @staticmethod
    def generate_delivery_otp() -> str:
        """Generate OTP for delivery verification."""
        return ''.join(random.choices(string.digits, k=6))
    
    @staticmethod
    def get_agent_pending_deliveries(db: Session, agent_id: int) -> List[Delivery]:
        """Get pending deliveries assigned to agent."""
        from app.models.delivery import Delivery, DeliveryStatus
        
        deliveries = db.query(Delivery).filter(
            Delivery.agent_id == agent_id,
            Delivery.status.in_([DeliveryStatus.pending, DeliveryStatus.in_progress])
        ).all()
        
        print(f"DEBUG: Found {len(deliveries)} deliveries for agent {agent_id}")  # Debug line
        return deliveries

    # @staticmethod
    # def get_agent_pending_deliveries(db: Session, agent_id: int) -> List[Delivery]:
    #     """Get pending deliveries for agent."""
    #     return crud_delivery.get_agent_pending_deliveries(db, agent_id)

    @staticmethod
    def update_agent_location(db: Session, delivery_id: int, agent_id: int, latitude: float, longitude: float) -> Delivery:
        """Update agent location for delivery."""
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise ValueError(f"Delivery {delivery_id} not found")

        if delivery.agent_id != agent_id:
            raise ValueError("Agent not assigned to this delivery")

        agent = crud_agent.get(db, agent_id)
        if agent:
            crud_agent.update_location(db, agent, latitude, longitude)

        logger.info(f"Agent {agent_id} location updated")
        return delivery


delivery_service = DeliveryService()
