"""Payment CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from app.crud.base import CRUDBase
from app.models.payment import Payment, PaymentStatus, PaymentMethod
from app.schemas.payment import UPIPaymentRequest as PaymentCreate
class CRUDPayment(CRUDBase[Payment, PaymentCreate, PaymentCreate]):
    """CRUD operations for Payment model."""

    def get_by_payment_number(self, db: Session, payment_number: str) -> Optional[Payment]:
        """Get payment by payment number."""
        return db.query(Payment).filter(Payment.payment_number == payment_number).first()

    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get payments by customer."""
        return db.query(Payment).filter(Payment.customer_id == customer_id).offset(skip).limit(limit).all()

    def get_by_order(self, db: Session, order_id: int) -> List[Payment]:
        """Get payments for order."""
        return db.query(Payment).filter(Payment.order_id == order_id).all()

    def get_by_status(self, db: Session, status: str, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get payments by status."""
        return db.query(Payment).filter(Payment.status == status).offset(skip).limit(limit).all()

    def get_pending_payments(self, db: Session, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get pending payments."""
        return db.query(Payment).filter(Payment.status == PaymentStatus.pending).offset(skip).limit(limit).all()

    def get_by_method(self, db: Session, method: str, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get payments by method."""
        return db.query(Payment).filter(Payment.payment_method == method).offset(skip).limit(limit).all()

    def update_status(self, db: Session, payment: Payment, status: str) -> Payment:
        """Update payment status."""
        payment.status = status
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def mark_completed(self, db: Session, payment: Payment, transaction_id: Optional[str] = None) -> Payment:
        """Mark payment as completed."""
        payment.status = PaymentStatus.completed
        if transaction_id:
            payment.gateway_transaction_id = transaction_id
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def mark_failed(self, db: Session, payment: Payment) -> Payment:
        """Mark payment as failed."""
        payment.status = PaymentStatus.failed
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def refund_payment(self, db: Session, payment: Payment, amount: float, reason: str) -> Payment:
        """Refund payment."""
        payment.status = PaymentStatus.refunded
        payment.refund_amount = amount
        payment.refund_reason = reason
        db.add(payment)
        db.commit()
        db.refresh(payment)
        return payment

    def get_cash_payments_for_agent(self, db: Session, agent_id: int, skip: int = 0, limit: int = 100) -> List[Payment]:
        """Get cash payments collected by agent."""
        return db.query(Payment).filter(
            Payment.collected_by_agent_id == agent_id,
            Payment.payment_method == PaymentMethod.cash,
            Payment.status != PaymentStatus.pending
        ).offset(skip).limit(limit).all()

    def generate_payment_number(self, db: Session) -> str:
        """Generate unique payment number."""
        import uuid
        payment_number = f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        while db.query(Payment).filter(Payment.payment_number == payment_number).first():
            payment_number = f"PAY-{datetime.utcnow().strftime('%Y%m%d')}-{uuid.uuid4().hex[:8].upper()}"
        return payment_number


crud_payment = CRUDPayment(Payment)
