"""Payment schemas."""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    upi = "upi"
    card = "card"
    cash = "cash"
    net_banking = "net_banking"
    wallet = "wallet"


class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    pending = "pending"
    processing = "processing"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"


class PaymentCreateRequest(BaseModel):
    """Payment creation request schema."""
    order_id: Optional[int] = None
    subscription_id: Optional[int] = None
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod


class UPIPaymentRequest(PaymentCreateRequest):
    """UPI payment request schema."""
    upi_id: str = Field(..., max_length=100)
    payment_method: PaymentMethod = PaymentMethod.upi


class CardPaymentRequest(PaymentCreateRequest):
    """Card payment request schema."""
    card_token: str
    payment_method: PaymentMethod = PaymentMethod.card


class CashPaymentRequest(PaymentCreateRequest):
    """Cash payment request schema."""
    payment_method: PaymentMethod = PaymentMethod.cash


class PaymentResponse(BaseModel):
    """Payment response schema."""
    id: int
    payment_number: str
    customer_id: int
    amount: float
    payment_method: PaymentMethod
    status: PaymentStatus
    gateway_transaction_id: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PaymentDetailResponse(PaymentResponse):
    """Detailed payment response schema."""
    order_id: Optional[int]
    subscription_id: Optional[int]
    refund_amount: float
    refund_reason: Optional[str]



# This file defines the Pydantic schemas for payment-related operations in the ASN Dairy Farm API. These schemas are used for validating and serializing payment data in API requests and responses. The schemas include payment creation requests, payment method-specific requests, and payment response models.



# """Payment schemas."""
# from pydantic import BaseModel, Field, validator
# from typing import Optional
# from datetime import datetime
# from enum import Enum


# class PaymentMethod(str, Enum):
#     upi = "upi"
#     card = "card"
#     cash = "cash"
#     net_banking = "net_banking"


# class PaymentStatus(str, Enum):
#     pending = "pending"
#     initiated = "initiated"
#     processing = "processing"
#     completed = "completed"
#     failed = "failed"
#     refunded = "refunded"
#     cancelled = "cancelled"


# # ========== UPI PAYMENT ==========
# class UPIPaymentRequest(BaseModel):
#     """UPI payment request."""
#     order_id: int
#     amount: float = Field(..., gt=0)
#     upi_id: str = Field(..., min_length=3, max_length=100)
#     idempotency_key: str = Field(..., min_length=20)  # UUID or unique identifier
    
#     @validator('upi_id')
#     def validate_upi_id(cls, v):
#         """Validate UPI ID format: name@upi"""
#         if '@' not in v:
#             raise ValueError('Invalid UPI ID format. Must be like: username@bankname')
#         return v.lower()
    
#     @validator('amount')
#     def validate_amount(cls, v):
#         """Validate amount is not too large"""
#         if v > 100000:  # Max ₹100,000 per transaction
#             raise ValueError('Amount exceeds maximum limit of ₹100,000')
#         return v


# class UPIPaymentResponse(BaseModel):
#     """UPI payment response."""
#     id: int
#     payment_number: str
#     order_id: int
#     amount: float
#     upi_id: str
#     status: PaymentStatus
#     gateway_transaction_id: Optional[str]
#     created_at: datetime

#     class Config:
#         from_attributes = True


# # ========== CASH ON DELIVERY ==========
# class CashPaymentRequest(BaseModel):
#     """COD payment request."""
#     order_id: int
#     amount: float = Field(..., gt=0)
#     idempotency_key: str = Field(..., min_length=20)
    
#     @validator('amount')
#     def validate_amount(cls, v):
#         if v <= 0:
#             raise ValueError('Amount must be greater than 0')
#         return v


# class CashOTPVerifyRequest(BaseModel):
#     """OTP verification for cash payment."""
#     payment_id: int
#     otp: str = Field(..., min_length=6, max_length=6)
    
#     @validator('otp')
#     def validate_otp(cls, v):
#         if not v.isdigit():
#             raise ValueError('OTP must be numeric')
#         return v


# class CashPaymentResponse(BaseModel):
#     """Cash payment response."""
#     id: int
#     payment_number: str
#     order_id: int
#     amount: float
#     status: str  # pending, verified_otp, collected, settled
#     cash_otp_verified: bool
#     collected_by_agent_id: Optional[int]
#     created_at: datetime

#     class Config:
#         from_attributes = True


# # ========== PAYMENT RESPONSES ==========
# class PaymentDetailResponse(BaseModel):
#     """Detailed payment response."""
#     id: int
#     payment_number: str
#     customer_id: int
#     order_id: Optional[int]
#     amount: float
#     payment_method: PaymentMethod
#     status: PaymentStatus
#     gateway_transaction_id: Optional[str]
#     refund_amount: float
#     refund_reason: Optional[str]
#     created_at: datetime
#     updated_at: datetime

#     class Config:
#         from_attributes = True

