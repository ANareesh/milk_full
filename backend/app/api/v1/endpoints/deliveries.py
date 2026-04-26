"""Delivery endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.core.dependencies import get_current_agent_user, get_current_admin_user, get_current_user
from app.crud.delivery import crud_delivery
from app.crud.order import crud_order
from app.schemas.delivery import DeliveryResponse, DeliveryAssignAgent, DeliveryUpdateStatus, DeliveryCompleteRequest, DeliveryOTPVerify
from app.models.user import User, UserRole
from app.services.delivery import delivery_service
from typing import Optional

router = APIRouter(prefix="/deliveries", tags=["deliveries"])

from app.models.delivery import Delivery, DeliveryStatus
from app.models.order import Order
from app.models.agent import Agent

# Helper function to populate delivery fields from related Order and Agent records
def populate_delivery_fields(db: Session, delivery: Delivery) -> Delivery:
    """Populate missing delivery fields from Order and Agent tables."""
    if not delivery:
        return delivery
    
    # Populate from Order
    order = db.query(Order).filter(Order.id == delivery.order_id).first()
    if order:
        delivery.order_number = order.order_number
        delivery.customer_id = order.customer_id
        delivery.total_amount = order.total_amount
        if not delivery.actual_delivery_date:
            delivery.actual_delivery_date = order.delivery_date
    
    # Populate agent name
    agent_record = db.query(Agent).filter(Agent.id == delivery.agent_id).first()
    if agent_record:
        user = db.query(User).filter(User.id == agent_record.user_id).first()
        if user:
            delivery.agent_name = user.full_name or user.username
    
    # Set default delivery_notes if null
    if not delivery.delivery_notes:
        delivery.delivery_notes = "Awaiting pickup"
    
    return delivery


@router.post("/{delivery_id}/assign-agent", response_model=DeliveryResponse)
async def assign_agent(
    delivery_id: int,
    assign_data: DeliveryAssignAgent,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Assign agent to delivery (admin)."""
    try:
        delivery = delivery_service.assign_agent_to_delivery(db, delivery_id, assign_data.agent_id)
        return delivery
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{delivery_id}/start", response_model=DeliveryResponse)
async def start_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Start delivery (agent)."""
    try:
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        
        # Find agent by user_id
        agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
        if not agent or delivery.agent_id != agent.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not assigned to this delivery")
        
        delivery = delivery_service.start_delivery(db, delivery_id)
        return populate_delivery_fields(db, delivery)  # ADD THIS LINE
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{delivery_id}/complete", response_model=DeliveryResponse)
async def complete_delivery(
    delivery_id: int,
    complete_data: DeliveryCompleteRequest,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Complete delivery (agent)."""
    try:
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        
        # Find agent by user_id
        agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
        if not agent or delivery.agent_id != agent.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not assigned")
        
        delivery = delivery_service.complete_delivery(
            db, delivery_id, complete_data.latitude, complete_data.longitude
        )
        return populate_delivery_fields(db, delivery)  # ADD THIS LINE
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/{delivery_id}/verify-otp", response_model=DeliveryResponse)
async def verify_otp(
    delivery_id: int,
    otp_data: DeliveryOTPVerify,
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Verify delivery OTP (agent)."""
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        
        # Find agent by user_id
        agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
        if not agent or delivery.agent_id != agent.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not assigned")
        
        # Log for debugging
        logger.info(f"Verifying OTP for delivery {delivery_id}. Stored: {delivery.delivery_otp}, Provided: {otp_data.otp}")
        
        # Verify OTP
        if not delivery.delivery_otp:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No OTP set for this delivery")
        
        stored_otp = str(delivery.delivery_otp).strip()
        provided_otp = str(otp_data.otp).strip()
        
        if stored_otp != provided_otp:
            logger.warning(f"OTP mismatch - Stored: '{stored_otp}' (len: {len(stored_otp)}), Provided: '{provided_otp}' (len: {len(provided_otp)})")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP")
        
        # Mark delivery as completed
        delivery.otp_verified = True
        delivery.status = DeliveryStatus.delivered
        delivery.actual_delivery_date = datetime.utcnow()
        delivery.delivery_time = datetime.utcnow()
        
        db.add(delivery)
        db.commit()
        db.refresh(delivery)
        
        # Update order status
        order = db.query(Order).filter(Order.id == delivery.order_id).first()
        if order:
            order.status = "delivered"
            db.add(order)
            db.commit()
        
        # Update agent earnings
        if delivery.agent_id:
            agent_record = db.query(Agent).filter(Agent.id == delivery.agent_id).first()
            if agent_record and order:
                commission = order.total_amount * 0.05  # 5% commission
                agent_record.total_earnings = (agent_record.total_earnings or 0) + commission
                agent_record.total_deliveries = (agent_record.total_deliveries or 0) + 1
                db.add(agent_record)
                db.commit()
        
        logger.info(f"OTP verified and delivery completed for delivery {delivery_id}")
        return populate_delivery_fields(db, delivery)
        
    except HTTPException:
        raise
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error verifying OTP: {str(e)}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

from app.schemas.delivery import DeliveryResponse, DeliveryAssignAgent, DeliveryUpdateStatus, DeliveryCompleteRequest, DeliveryOTPVerify, DeliveryFailRequest

from app.schemas.delivery import DeliveryResponse, DeliveryAssignAgent, DeliveryUpdateStatus, DeliveryCompleteRequest, DeliveryOTPVerify, DeliveryFailRequest
from fastapi import Body

@router.post("/{delivery_id}/fail", response_model=DeliveryResponse)
async def fail_delivery(
    delivery_id: int,
    fail_data: DeliveryFailRequest = Body(...),  # Use Body() to be explicit
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Mark delivery as failed (agent)."""
    try:
        delivery = crud_delivery.get(db, delivery_id)
        if not delivery:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
        
        # Find agent by user_id
        agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
        if not agent or delivery.agent_id != agent.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Agent not assigned")
        
        reason = fail_data.reason  # Access the validated schema
        delivery = delivery_service.fail_delivery(db, delivery_id, reason)
        return populate_delivery_fields(db, delivery)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


from app.models.delivery import Delivery
from app.models.order import Order
from app.models.agent import Agent

@router.get("/agent/my-deliveries", response_model=List[DeliveryResponse])
async def get_agent_deliveries(
    current_user: User = Depends(get_current_agent_user),
    db: Session = Depends(get_db),
):
    """Get my deliveries (agent)."""
    from app.models.agent import Agent
    
    # Find the agent record by user_id
    agent = db.query(Agent).filter(Agent.user_id == current_user.id).first()
    
    if not agent:
        return []  # Return empty if agent record not found
    
    # Query deliveries with ORDER JOIN to get order details
    deliveries = db.query(Delivery).join(Order).filter(
        Delivery.agent_id == agent.id,
        Delivery.status.in_(['pending', 'in_progress'])
    ).all()
    
    # Manually populate missing fields from Order
    for delivery in deliveries:
        order = db.query(Order).filter(Order.id == delivery.order_id).first()
        if order:
            delivery.order_number = order.order_number
            delivery.customer_id = order.customer_id
            delivery.total_amount = order.total_amount
            # Use order delivery_date if actual_delivery_date is null
            if not delivery.actual_delivery_date:
                delivery.actual_delivery_date = order.delivery_date
        
        # Add agent name
        agent_record = db.query(Agent).filter(Agent.id == delivery.agent_id).first()
        if agent_record:
            user = db.query(User).filter(User.id == agent_record.user_id).first()
            if user:
                delivery.agent_name = user.full_name or user.username
        
        # Set default delivery_notes if null
        if not delivery.delivery_notes:
            delivery.delivery_notes = "Awaiting pickup"
    
    return deliveries

@router.get("/{delivery_id}", response_model=DeliveryResponse)
async def get_delivery(
    delivery_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get delivery details."""
    delivery = crud_delivery.get(db, delivery_id)
    if not delivery:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Delivery not found")
    
    return delivery




# @router.get("/admin/pending", response_model=List[DeliveryResponse])
# async def get_pending_deliveries(
#     current_user: User = Depends(get_current_admin_user),
#     db: Session = Depends(get_db),
# ):
#     """Get pending deliveries without assigned agents (admin)."""
#     deliveries = crud_delivery.get_pending_deliveries(db)
#     # Filter to only those without agents
#     unassigned = [d for d in deliveries if d.agent_id is None]
#     # Populate missing fields from related records
#     for delivery in unassigned:
#         populate_delivery_fields(db, delivery)
#     return unassigned
# @router.get("/admin/pending", response_model=List[DeliveryResponse])
# async def get_pending_deliveries(
#     current_user: User = Depends(get_current_admin_user),
#     db: Session = Depends(get_db),
# ):
#     """Get pending deliveries (admin)."""
#     # Filter deliveries by pending status
#     deliveries = db.query(Delivery).filter(
#         Delivery.status == DeliveryStatus.pending
#     ).all()
    
#     # Populate missing fields from related records
#     for delivery in deliveries:
#         populate_delivery_fields(db, delivery)
    
#     return deliveries

@router.get("/admin/pending", response_model=List[DeliveryResponse])
async def get_pending_deliveries(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get pending deliveries (admin)."""
    # Show deliveries that are pending OR in_progress (not delivered/failed)
    deliveries = db.query(Delivery).filter(
        Delivery.status.in_([DeliveryStatus.pending, DeliveryStatus.in_progress])
    ).all()
    
    for delivery in deliveries:
        populate_delivery_fields(db, delivery)
    
    return deliveries

@router.get("/admin/all", response_model=List[DeliveryResponse])
async def get_all_deliveries(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Get all deliveries with optional status filter (admin)."""
    if status and status != "all":  # Handle "all" case
        deliveries = crud_delivery.get_by_status(db, status)
    else:
        deliveries = db.query(Delivery).all()
    # Populate missing fields from related records
    for delivery in deliveries:
        populate_delivery_fields(db, delivery)
    return deliveries
