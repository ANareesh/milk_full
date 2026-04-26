"""Payment service."""
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
import logging
import uuid

from app.crud.payment import crud_payment
from app.crud.order import crud_order
from app.crud.customer import crud_customer
from app.crud.agent import crud_agent
from app.models.payment import Payment, PaymentStatus, PaymentMethod

logger = logging.getLogger(__name__)


class PaymentService:
    """Payment management service."""

    @staticmethod
    def create_payment(
        db: Session,
        customer_id: int,
        amount: float,
        payment_method: str,
        order_id: Optional[int] = None,
    ) -> Payment:
        """Create payment record."""
        customer = crud_customer.get(db, customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        payment_number = crud_payment.generate_payment_number(db)
        
        payment = Payment(
            payment_number=payment_number,
            customer_id=customer_id,
            order_id=order_id,
            amount=amount,
            payment_method=payment_method,
            status=PaymentStatus.pending,
        )
        db.add(payment)
        db.commit()
        db.refresh(payment)

        logger.info(f"Payment created: {payment.payment_number}")
        return payment

    @staticmethod
    def process_upi_payment(
        db: Session,
        customer_id: int,
        amount: float,
        upi_id: str,
        order_id: Optional[int] = None,
    ) -> Payment:
        """Process UPI payment."""
        payment = PaymentService.create_payment(
            db, customer_id, amount, PaymentMethod.upi, order_id
        )
        payment.upi_id = upi_id
        
        # Simulate UPI payment processing
        payment.status = PaymentStatus.processing
        payment.gateway_transaction_id = str(uuid.uuid4())
        
        # Mark as completed (in real scenario, wait for webhook)
        payment.status = PaymentStatus.completed
        payment.upi_transaction_id = str(uuid.uuid4())
        
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Update customer balance
        customer = crud_customer.get(db, customer_id)
        if customer and order_id:
            order = crud_order.get(db, order_id)
            if order:
                customer.total_amount_due -= order.total_amount
                db.add(customer)
                db.commit()

        logger.info(f"UPI payment processed: {payment.payment_number}")
        return payment

    @staticmethod
    def process_card_payment(
        db: Session,
        customer_id: int,
        amount: float,
        card_token: str,
        order_id: Optional[int] = None,
    ) -> Payment:
        """Process card payment."""
        payment = PaymentService.create_payment(
            db, customer_id, amount, PaymentMethod.card, order_id
        )
        
        # Simulate card payment processing with Stripe
        payment.status = PaymentStatus.processing
        payment.gateway_transaction_id = str(uuid.uuid4())
        payment.card_brand = "VISA"  # In reality, from Stripe
        payment.card_last_four = "1234"  # In reality, from Stripe
        
        # Mark as completed
        payment.status = PaymentStatus.completed
        
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Update customer balance
        customer = crud_customer.get(db, customer_id)
        if customer and order_id:
            order = crud_order.get(db, order_id)
            if order:
                customer.total_amount_due -= order.total_amount
                db.add(customer)
                db.commit()

        logger.info(f"Card payment processed: {payment.payment_number}")
        return payment

    @staticmethod
    def process_cash_payment(
        db: Session,
        customer_id: int,
        amount: float,
        agent_id: Optional[int] = None,
        order_id: Optional[int] = None,
    ) -> Payment:
        """Process cash payment (collected by agent or customer COD)."""
        payment = PaymentService.create_payment(
            db, customer_id, amount, PaymentMethod.cash, order_id
        )
        if agent_id:
            payment.collected_by_agent_id = agent_id
        payment.cash_collected_date = datetime.utcnow()
        payment.status = PaymentStatus.completed
        
        db.add(payment)
        db.commit()
        db.refresh(payment)

        # Update customer balance
        customer = crud_customer.get(db, customer_id)
        if customer and order_id:
            order = crud_order.get(db, order_id)
            if order:
                customer.total_amount_due -= order.total_amount
                db.add(customer)
                db.commit()

        logger.info(f"Cash payment processed: {payment.payment_number}")
        return payment

    @staticmethod
    def refund_payment(db: Session, payment_id: int, reason: str) -> Payment:
        """Refund payment."""
        payment = crud_payment.get(db, payment_id)
        if not payment:
            raise ValueError(f"Payment {payment_id} not found")

        if payment.status != PaymentStatus.completed:
            raise ValueError(f"Cannot refund payment with status: {payment.status}")

        payment = crud_payment.refund_payment(db, payment, payment.amount, reason)
        
        # Update customer balance
        customer = crud_customer.get(db, payment.customer_id)
        if customer:
            customer.total_amount_due += payment.amount
            db.add(customer)
            db.commit()

        logger.info(f"Payment refunded: {payment.payment_number}")
        return payment

    @staticmethod
    def get_pending_cash_payments(db: Session) -> list:
        """Get all pending cash payments (for admin)."""
        return crud_payment.get_by_status(db, PaymentStatus.pending)


payment_service = PaymentService()








# """Payment service with production-ready UPI and COD handling."""
# import logging
# import random
# import string
# from datetime import datetime, timedelta
# from typing import Optional
# from sqlalchemy.orm import Session
# from sqlalchemy.exc import IntegrityError

# from app.crud.payment import crud_payment
# from app.crud.order import crud_order
# from app.crud.customer import crud_customer
# from app.crud.agent import crud_agent
# from app.models.payment import Payment, PaymentStatus, PaymentMethod, CashPaymentStatus
# from app.models.order import Order
# from app.models.delivery import Delivery, DeliveryStatus
# from app.core.config import get_settings

# logger = logging.getLogger(__name__)
# settings = get_settings()


# class PaymentService:
#     """Production-grade payment service."""

#     @staticmethod
#     def validate_payment_request(
#         db: Session, customer_id: int, order_id: int, amount: float, idempotency_key: str
#     ) -> tuple[bool, str]:
#         """
#         Validate payment request.
        
#         Returns: (is_valid, error_message)
#         """
#         # Check for duplicate payment (idempotency)
#         existing = db.query(Payment).filter(
#             Payment.idempotency_key == idempotency_key
#         ).first()
#         if existing:
#             if existing.status == PaymentStatus.completed:
#                 logger.warning(f"Duplicate successful payment: {idempotency_key}")
#                 return False, "Payment already processed"
#             elif existing.status in [PaymentStatus.initiated, PaymentStatus.processing]:
#                 return False, "Payment processing, please wait"
        
#         # Validate order exists and belongs to customer
#         order = crud_order.get(db, order_id)
#         if not order:
#             return False, f"Order {order_id} not found"
        
#         customer = crud_customer.get(db, customer_id)
#         if not customer or order.customer_id != customer.id:
#             return False, "Order doesn't belong to this customer"
        
#         # Validate amount matches order total (with ±5 INR tolerance for charges)
#         if abs(order.total_amount - amount) > 5:
#             logger.error(f"Amount mismatch: Expected {order.total_amount}, got {amount}")
#             return False, f"Amount mismatch. Expected ₹{order.total_amount}"
        
#         # Check if payment already exists for this order
#         existing_payment = crud_payment.get_by_order(db, order_id)
#         if existing_payment:
#             completed = [p for p in existing_payment if p.status == PaymentStatus.completed]
#             if completed:
#                 return False, "Order already paid"
        
#         return True, ""

#     # ========== UPI PAYMENT ==========
#     @staticmethod
#     def process_upi_payment(
#         db: Session,
#         customer_id: int,
#         order_id: int,
#         amount: float,
#         upi_id: str,
#         idempotency_key: str,
#     ) -> Payment:
#         """
#         Process UPI payment with production-grade error handling.
        
#         Flow:
#         1. Validate request
#         2. Create payment record with idempotency key
#         3. Call UPI gateway (Razorpay/NPCI)
#         4. Wait for webhook confirmation
#         5. Update order delivery status
#         """
#         # Step 1: Validate
#         is_valid, error_msg = PaymentService.validate_payment_request(
#             db, customer_id, order_id, amount, idempotency_key
#         )
#         if not is_valid:
#             raise ValueError(error_msg)
        
#         # Step 2: Create payment record
#         try:
#             payment_number = f"UPI-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
            
#             payment = Payment(
#                 payment_number=payment_number,
#                 idempotency_key=idempotency_key,
#                 customer_id=customer_id,
#                 order_id=order_id,
#                 amount=amount,
#                 payment_method=PaymentMethod.upi,
#                 upi_id=upi_id,
#                 status=PaymentStatus.initiated,  # Not pending - initiated by user
#                 retry_count=0,
#             )
#             db.add(payment)
#             db.commit()
#             db.refresh(payment)
#         except IntegrityError as e:
#             db.rollback()
#             logger.error(f"Duplicate payment attempt: {idempotency_key}")
#             raise ValueError("Payment already in progress")
        
#         # Step 3: Call UPI gateway
#         try:
#             # THIS IS WHERE YOU INTEGRATE RAZORPAY/NPCI
#             gateway_response = PaymentService._call_razorpay_upi(
#                 amount=amount,
#                 upi_id=upi_id,
#                 payment_id=payment.id,
#                 order_id=order_id,
#             )
            
#             # Step 4: Update payment with gateway response
#             payment.gateway_transaction_id = gateway_response.get('request_id')
#             payment.status = PaymentStatus.processing  # Waiting for webhook
#             payment.upi_ref_id = gateway_response.get('upi_req_id')
            
#             db.add(payment)
#             db.commit()
#             db.refresh(payment)
            
#             logger.info(f"UPI payment initiated: {payment.payment_number} -> {payment.gateway_transaction_id}")
            
#         except Exception as e:
#             payment.status = PaymentStatus.failed
#             payment.notes = str(e)
#             payment.retry_count = 1
#             db.add(payment)
#             db.commit()
#             logger.error(f"UPI gateway error for payment {payment.id}: {str(e)}")
#             raise ValueError(f"Payment gateway error: {str(e)}")
        
#         return payment

#     @staticmethod
#     def _call_razorpay_upi(
#         amount: float, upi_id: str, payment_id: int, order_id: int
#     ) -> dict:
#         """
#         Call Razorpay UPI gateway.
        
#         NOTE: This requires Razorpay API key configuration
#         """
#         # PRODUCTION: Implement actual Razorpay integration
#         # import razorpay
#         # client = razorpay.Client(auth=(settings.razorpay_key_id, settings.razorpay_key_secret))
#         # response = client.payment_link.create({...})
        
#         # FOR NOW: Simulate with structure
#         return {
#             'request_id': f'REQ_{payment_id}_{order_id}',
#             'upi_req_id': f'UPI{random.randint(1000000, 9999999)}',
#             'status': 'created'
#         }

#     @staticmethod
#     def handle_upi_webhook(db: Session, webhook_data: dict) -> Payment:
#         """
#         Handle UPI payment webhook from Razorpay.
        
#         This is called when payment gateway confirms UPI transaction.
#         """
#         request_id = webhook_data.get('request_id')
#         status = webhook_data.get('status')
#         transaction_id = webhook_data.get('transaction_id')
        
#         if not request_id:
#             raise ValueError("Invalid webhook: missing request_id")
        
#         # Find payment by gateway transaction ID
#         payment = db.query(Payment).filter(
#             Payment.gateway_transaction_id == request_id
#         ).first()
        
#         if not payment:
#             logger.error(f"Webhook: Payment not found for request {request_id}")
#             raise ValueError("Payment record not found")
        
#         if status == 'success':
#             payment.status = PaymentStatus.completed
#             payment.upi_transaction_id = transaction_id
            
#             # Update customer balance
#             order = crud_order.get(db, payment.order_id)
#             if order:
#                 customer = crud_customer.get(db, payment.customer_id)
#                 customer.total_amount_due = max(0, customer.total_amount_due - order.total_amount)
#                 db.add(customer)
            
#             logger.info(f"UPI payment completed: {payment.payment_number}")
            
#         elif status == 'failed':
#             payment.status = PaymentStatus.failed
#             payment.notes = webhook_data.get('error_message', 'UPI payment failed')
#             logger.warning(f"UPI payment failed: {payment.payment_number}")
            
#         db.add(payment)
#         db.commit()
#         db.refresh(payment)
        
#         return payment

#     # ========== CASH ON DELIVERY ==========
#     @staticmethod
#     def process_cod_payment(
#         db: Session,
#         customer_id: int,
#         order_id: int,
#         amount: float,
#         idempotency_key: str,
#     ) -> Payment:
#         """
#         Process Cash on Delivery payment.
        
#         Flow:
#         1. Validate request
#         2. Create payment record (status: pending)
#         3. Generate OTP for agent verification
#         4. Link to delivery (wait for delivery agent to collect)
#         5. Mark as completed only after agent OTP verification
#         """
#         # Validate
#         is_valid, error_msg = PaymentService.validate_payment_request(
#             db, customer_id, order_id, amount, idempotency_key
#         )
#         if not is_valid:
#             raise ValueError(error_msg)
        
#         # Create payment record
#         try:
#             payment_number = f"COD-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}-{random.randint(1000, 9999)}"
#             otp = ''.join(random.choices(string.digits, k=6))
            
#             payment = Payment(
#                 payment_number=payment_number,
#                 idempotency_key=idempotency_key,
#                 customer_id=customer_id,
#                 order_id=order_id,
#                 amount=amount,
#                 payment_method=PaymentMethod.cash,
#                 status=PaymentStatus.pending,
#                 cash_status=CashPaymentStatus.pending,
#                 cash_otp=otp,
#                 cash_otp_verified=False,
#             )
#             db.add(payment)
#             db.commit()
#             db.refresh(payment)
            
#             logger.info(f"COD payment initiated: {payment.payment_number} (OTP: {otp})")
            
#         except IntegrityError:
#             db.rollback()
#             raise ValueError("Payment already in progress")
        
#         return payment

#     @staticmethod
#     def verify_cod_otp(
#         db: Session, payment_id: int, otp: str
#     ) -> Payment:
#         """
#         Verify OTP for COD payment.
        
#         Called by delivery agent when arriving at customer location.
#         """
#         payment = crud_payment.get(db, payment_id)
#         if not payment:
#             raise ValueError(f"Payment {payment_id} not found")
        
#         if payment.payment_method != PaymentMethod.cash:
#             raise ValueError("OTP verification only for COD payments")
        
#         if payment.status != PaymentStatus.pending:
#             raise ValueError(f"Cannot verify OTP for payment with status {payment.status}")
        
#         if otp != payment.cash_otp:
#             logger.warning(f"Invalid OTP for payment {payment_id}")
#             raise ValueError("Invalid OTP")
        
#         # Mark OTP as verified
#         payment.cash_otp_verified = True
#         payment.cash_status = CashPaymentStatus.verified_otp
#         payment.status = PaymentStatus.processing  # Waiting for actual collection
        
#         db.add(payment)
#         db.commit()
#         db.refresh(payment)
        
#         logger.info(f"COD OTP verified: {payment.payment_number}")
#         return payment

#     @staticmethod
#     def mark_cod_collected(
#         db: Session, payment_id: int, agent_id: int, delivery_id: int
#     ) -> Payment:
#         """
#         Mark COD payment as collected by agent.
        
#         Called when agent confirms payment collection during delivery.
#         """
#         payment = crud_payment.get(db, payment_id)
#         if not payment:
#             raise ValueError(f"Payment {payment_id} not found")
        
#         # Verify agent exists
#         agent = crud_agent.get(db, agent_id)
#         if not agent:
#             raise ValueError(f"Agent {agent_id} not found")
        
#         # Verify delivery matches
#         delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
#         if not delivery or delivery.agent_id != agent_id:
#             raise ValueError("Delivery doesn't match agent")
        
#         if payment.cash_status != CashPaymentStatus.verified_otp:
#             raise ValueError(f"Cannot collect payment with status {payment.cash_status}")
        
#         # Update payment
#         payment.collected_by_agent_id = agent_id
#         payment.cash_collected_date = datetime.utcnow()
#         payment.cash_status = CashPaymentStatus.collected
#         payment.status = PaymentStatus.completed
        
#         # Update customer balance
#         order = crud_order.get(db, payment.order_id)
#         if order:
#             customer = crud_customer.get(db, payment.customer_id)
#             customer.total_amount_due = max(0, customer.total_amount_due - order.total_amount)
#             db.add(customer)
        
#         db.add(payment)
#         db.commit()
#         db.refresh(payment)
        
#         logger.info(f"COD payment collected: {payment.payment_number} by Agent {agent_id}")
#         return payment


# # Singleton instance
# payment_service = PaymentService()
