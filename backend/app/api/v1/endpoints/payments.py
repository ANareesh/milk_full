"""Payment endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_customer_user, get_current_admin_user, get_current_user
from app.crud.payment import crud_payment
from app.crud.customer import crud_customer
from app.schemas.payment import PaymentResponse, PaymentDetailResponse, UPIPaymentRequest, CardPaymentRequest, CashPaymentRequest
from app.models.user import User, UserRole
from app.services.payment import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/upi", response_model=PaymentResponse)
async def create_upi_payment(
    payment_data: UPIPaymentRequest,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Process UPI payment (customer)."""
    try:
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
        
        payment = payment_service.process_upi_payment(
            db, customer.id, payment_data.amount, payment_data.upi_id, payment_data.order_id
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/card", response_model=PaymentResponse)
async def create_card_payment(
    payment_data: CardPaymentRequest,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Process card payment (customer)."""
    try:
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
        
        payment = payment_service.process_card_payment(
            db, customer.id, payment_data.amount, payment_data.card_token, payment_data.order_id
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/cash", response_model=PaymentResponse)
async def create_cash_payment(
    payment_data: CashPaymentRequest,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Process cash payment - cash on delivery (customer)."""
    try:
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
        
        # For customer COD payments, no agent_id needed, pass None
        payment = payment_service.process_cash_payment(
            db, customer.id, payment_data.amount, None, payment_data.order_id
        )
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my-payments", response_model=List[PaymentDetailResponse])
async def get_my_payments(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get my payment history (customer)."""
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    
    payments = crud_payment.get_by_customer(db, customer.id, skip=skip, limit=limit)
    return payments


@router.get("/{payment_id}", response_model=PaymentDetailResponse)
async def get_payment(
    payment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get payment details."""
    payment = crud_payment.get(db, payment_id)
    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    
    # Check permission
    if current_user.role == UserRole.customer:
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer or payment.customer_id != customer.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentDetailResponse)
async def refund_payment(
    payment_id: int,
    refund_data: dict,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Refund payment (admin only)."""
    try:
        reason = refund_data.get("reason", "Admin initiated refund")
        payment = payment_service.refund_payment(db, payment_id, reason)
        return payment
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/admin/all", response_model=List[PaymentDetailResponse])
async def get_all_payments(
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all payments (admin only)."""
    if status:
        payments = crud_payment.get_by_status(db, status, skip=skip, limit=limit)
    else:
        payments = crud_payment.get_multi(db, skip=skip, limit=limit)
    return payments

