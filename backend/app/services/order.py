"""Order service."""
from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
import logging

from app.crud.order import crud_order
from app.crud.customer import crud_customer
from app.crud.product import crud_product
from app.crud.delivery import crud_delivery
from app.crud.agent import crud_agent
from app.crud.payment import crud_payment
from app.models.order import Order, OrderStatus
from app.models.delivery import Delivery, DeliveryStatus
from app.models.agent import Agent
from app.models.payment import Payment, PaymentStatus
from app.schemas.order import OrderCreateOneTime

logger = logging.getLogger(__name__)


class OrderService:
    """Order management service."""

    @staticmethod
    def create_one_time_order(
        db: Session, customer_id: int, order_data: OrderCreateOneTime
    ) -> Order:
        """Create one-time order."""
        from app.core.config import get_settings
        # ✅ VALIDATE CITY/LOCATION
        settings = get_settings()
        if not any(city.lower() in order_data.delivery_address.lower() for city in settings.allowed_cities):
            raise ValueError(
                f"Delivery not available at this location. Allowed cities: {', '.join(settings.allowed_cities)}"
            )
        # Validate customer exists
        customer = crud_customer.get(db, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Validate product exists and has stock
        product = crud_product.get(db, order_data.product_id)
        if not product:
            raise ValueError(f"Product {order_data.product_id} not found")

        if product.available_quantity < order_data.quantity:
            raise ValueError(f"Insufficient stock. Available: {product.available_quantity}")

        # Calculate total amount
        total_amount = product.unit_price * order_data.quantity

        # Create order
        order_number = crud_order.generate_order_number(db)
        order = Order(
            order_number=order_number,
            customer_id=customer_id,
            product_id=order_data.product_id,
            order_type="one_time",
            quantity=order_data.quantity,
            unit_price=product.unit_price,
            total_amount=total_amount,
            delivery_date=order_data.delivery_date,
            special_instructions=order_data.special_instructions,
            status=OrderStatus.pending,
        )
        db.add(order)
        
        # Reduce product stock
        crud_product.reduce_quantity(db, product, order_data.quantity)
        
        # Update customer balance
        crud_customer.update_amount_due(db, customer, total_amount)
        
        db.commit()
        db.refresh(order)
        
        logger.info(f"Order created: {order.order_number}")
        return order

    @staticmethod
    def confirm_order(db: Session, order: Order) -> Order:
        """Confirm order - admin will manually assign delivery agent."""
        if order.status != OrderStatus.pending:
            raise ValueError(f"Cannot confirm order with status: {order.status}")

        order.status = OrderStatus.confirmed
        db.add(order)
        db.commit()
        db.refresh(order)

        # Create delivery record - NO AUTO-ASSIGNMENT
        import random
        import string
        
        otp = ''.join(random.choices(string.digits, k=6))
        
        delivery = Delivery(
            order_id=order.id,
            status=DeliveryStatus.pending,
            scheduled_date=order.delivery_date,
            agent_id=None,  # ✅ NO AGENT - Admin assigns manually
            delivery_otp=otp,  # ✅ OTP generated
        )
        
        db.add(delivery)
        db.commit()
        
        logger.info(f"Delivery created for order {order.order_number} (OTP: {otp}) - awaiting admin agent assignment")
        logger.info(f"Order confirmed: {order.order_number}")
        
        return order

    # @staticmethod
    # def confirm_order(db: Session, order: Order) -> Order:
    #     """Confirm order and assign delivery agent."""
    #     if order.status != OrderStatus.pending:
    #         raise ValueError(f"Cannot confirm order with status: {order.status}")

    #     order.status = OrderStatus.confirmed
    #     db.add(order)
    #     db.commit()
    #     db.refresh(order)

    #     # Create delivery record
    #     delivery = Delivery(
    #         order_id=order.id,
    #         status=DeliveryStatus.pending,
    #         scheduled_date=order.delivery_date,
            
    #     )
    #     # Try to auto-assign an available agent
    #     try:
    #         # Get available agents (those with available_for_delivery = True)
    #         available_agents = db.query(Agent).filter(
    #             Agent.available_for_delivery == True
    #         ).all()
            
    #         if available_agents:
    #             agent = available_agents[0]
    #             delivery.agent_id = agent.id
                
    #             import random
    #             import string
    #             otp = ''.join(random.choices(string.digits, k=6))
    #             delivery.delivery_otp = otp
                
    #             logger.info(f"Auto-assigned agent {agent.id} to delivery for order {order.order_number}")
    #         else:
    #             logger.warning(f"No available agents to assign for order {order.order_number}")
    #     except Exception as e:
    #         logger.error(f"Failed to auto-assign agent: {str(e)}")
        
    #     db.add(delivery)
    #     db.commit()

    #     logger.info(f"Order confirmed: {order.order_number}")
    #     return order

    @staticmethod
    def cancel_order(db: Session, order: Order, reason: str = "") -> Order:
        """Cancel order."""
        if order.status in [OrderStatus.delivered, OrderStatus.returned]:
            raise ValueError(f"Cannot cancel delivered order: {order.order_number}")

        order.status = OrderStatus.cancelled
        db.add(order)
        db.commit()

        # Restore product stock
        product = crud_product.get(db, order.product_id)
        if product:
            crud_product.increase_quantity(db, product, order.quantity)

        # Reverse customer balance
        customer = crud_customer.get(db, order.customer_id)
        if customer:
            crud_customer.update_amount_due(db, customer, -order.total_amount)

        logger.info(f"Order cancelled: {order.order_number}")
        return order

    @staticmethod
    def get_customer_orders(
        db: Session, customer_id: int, status: Optional[str] = None
    ) -> List[Order]:
        """Get customer orders."""
        if status:
            return crud_order.get_customer_orders_by_status(db, customer_id, status)
        return crud_order.get_by_customer(db, customer_id)

    @staticmethod
    def get_orders_for_delivery_today(db: Session) -> List[Order]:
        """Get orders scheduled for delivery today."""
        today = datetime.utcnow()
        return crud_order.get_orders_for_delivery(db, today)


order_service = OrderService()
