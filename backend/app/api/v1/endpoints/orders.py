"""Order endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_customer_user, get_current_admin_user, get_current_user
from app.crud.order import crud_order
from app.crud.delivery import crud_delivery
from app.crud.customer import crud_customer
from app.schemas.order import OrderCreateOneTime, OrderResponse, OrderDetailResponse
from app.models.user import User, UserRole
from app.services.order import order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse)
async def create_order(
    order_data: OrderCreateOneTime,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Create new order (customer)."""
    try:
        # Get customer
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
        
        order = order_service.create_one_time_order(db, customer.id, order_data)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/my-orders", response_model=List[OrderResponse])
async def get_my_orders(
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get my orders (customer)."""
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    
    orders = order_service.get_customer_orders(db, customer.id, status)
    return orders[skip : skip + limit]


@router.get("/{order_id}", response_model=OrderDetailResponse)
async def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get order details."""
    order = crud_order.get(db, order_id)
    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
    
    # Check permission
    if current_user.role == UserRole.customer:
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer or order.customer_id != customer.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    return order


@router.post("/{order_id}/confirm", response_model=OrderResponse)
async def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Confirm order (admin)."""
    try:
        order = crud_order.get(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        order = order_service.confirm_order(db, order)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Cancel order (customer)."""
    try:
        order = crud_order.get(db, order_id)
        if not order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        # Check permission
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer or order.customer_id != customer.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
        
        order = order_service.cancel_order(db, order)
        return order
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/admin/all", response_model=List[OrderResponse])
async def get_all_orders(
    status: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all orders (admin only)."""
    if status:
        orders = crud_order.get_by_status(db, status, skip=skip, limit=limit)
    else:
        orders = crud_order.get_multi(db, skip=skip, limit=limit)
    return orders
