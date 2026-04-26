"""Payment model."""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime
import enum

from app.core.database import Base


class PaymentMethod(str, enum.Enum):
    """Payment method enumeration."""
    upi = "upi"
    card = "card"
    cash = "cash"
    net_banking = "net_banking"
    wallet = "wallet"


class PaymentStatus(str, enum.Enum):
    """Payment status enumeration."""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class Payment(Base):
    """Payment model."""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    payment_number = Column(String(50), unique=True, nullable=False, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending, index=True)
    
    # UPI specific fields
    upi_id = Column(String(100), nullable=True)
    upi_transaction_id = Column(String(100), nullable=True)
    
    # Card specific fields
    card_last_four = Column(String(4), nullable=True)
    card_brand = Column(String(50), nullable=True)
    
    # Payment gateway
    gateway_transaction_id = Column(String(100), nullable=True)
    stripe_payment_intent_id = Column(String(100), nullable=True)
    
    # Cash payment
    collected_by_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    cash_collected_date = Column(DateTime(timezone=True), nullable=True)
    
    # Refund information
    refund_amount = Column(Float, default=0.0)
    refund_reason = Column(String(255), nullable=True)
    
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, payment_number={self.payment_number}, status={self.status})>"




# #pylint: disable=too-many-columns

# """Payment model."""
# from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum as SQLEnum, Text, Boolean
# from sqlalchemy.sql import func
# from datetime import datetime
# import enum

# from app.core.database import Base


# class PaymentMethod(str, enum.Enum):
#     """Payment method enumeration."""
#     upi = "upi"
#     card = "card"
#     cash = "cash"
#     net_banking = "net_banking"
#     wallet = "wallet"


# class PaymentStatus(str, enum.Enum):
#     """Payment status enumeration."""
#     pending = "pending"
#     initiated = "initiated"  # NEW: Waiting for UPI provider
#     processing = "processing"
#     completed = "completed"
#     failed = "failed"
#     refunded = "refunded"
#     cancelled = "cancelled"


# class CashPaymentStatus(str, enum.Enum):
#     """Cash payment lifecycle states."""
#     pending = "pending"  # Awaiting delivery
#     verified_otp = "verified_otp"  # OTP confirmed
#     collected = "collected"  # Agent collected payment
#     settled = "settled"  # Settled with agent


# class Payment(Base):
#     """Payment model."""
#     __tablename__ = "payments"

#     id = Column(Integer, primary_key=True, index=True)
#     payment_number = Column(String(50), unique=True, nullable=False, index=True)
#     idempotency_key = Column(String(100), unique=True, nullable=True, index=True)  # NEW
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
#     order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
#     subscription_id = Column(Integer, ForeignKey("subscriptions.id"), nullable=True)
#     amount = Column(Float, nullable=False)
#     payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
#     status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.pending, index=True)
#     cash_status = Column(SQLEnum(CashPaymentStatus), nullable=True)  # NEW: For COD tracking
    
#     # UPI specific fields
#     upi_id = Column(String(100), nullable=True)
#     upi_transaction_id = Column(String(100), nullable=True, unique=True)
#     upi_ref_id = Column(String(100), nullable=True)
    
#     # Card specific fields
#     card_last_four = Column(String(4), nullable=True)
#     card_brand = Column(String(50), nullable=True)
    
#     # Payment gateway
#     gateway_transaction_id = Column(String(100), nullable=True, unique=True)
#     stripe_payment_intent_id = Column(String(100), nullable=True)
    
#     # Cash payment
#     collected_by_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
#     cash_collected_date = Column(DateTime(timezone=True), nullable=True)
#     cash_otp = Column(String(6), nullable=True)  # NEW: OTP for verification
#     cash_otp_verified = Column(Boolean, default=False)  # NEW
    
#     # Refund information
#     refund_amount = Column(Float, default=0.0)
#     refund_reason = Column(String(255), nullable=True)
#     refund_transaction_id = Column(String(100), nullable=True)
    
#     # Reconciliation
#     settlement_id = Column(Integer, nullable=True)  # NEW: Links to agent settlement
#     retry_count = Column(Integer, default=0)  # NEW
#     last_retry_at = Column(DateTime(timezone=True), nullable=True)  # NEW
    
#     notes = Column(Text, nullable=True)
#     created_at = Column(DateTime(timezone=True), server_default=func.now())
#     updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

#     def __repr__(self) -> str:
#         return f"<Payment(id={self.id}, payment_number={self.payment_number}, status={self.status})>"