"""Admin reporting and statistics endpoints."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, Any

from app.core.database import get_db
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.crud.order import crud_order
from app.crud.payment import crud_payment
from app.crud.delivery import crud_delivery
from app.crud.customer import crud_customer
from app.crud.agent import crud_agent
from app.crud.product import crud_product
from sqlalchemy import func
from app.models.order import Order
from app.models.payment import Payment
from app.models.delivery import Delivery

router = APIRouter(prefix="/admin/reports", tags=["admin", "reports"])


@router.get("/dashboard-stats")
async def get_dashboard_stats(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get dashboard statistics."""
    
    # Total customers
    total_customers = crud_customer.count(db)
    
    # Total agents
    total_agents = crud_agent.count(db)
    
    # Total products
    total_products = crud_product.count(db)
    
    # Today's orders
    today = datetime.utcnow()
    today_orders = crud_order.get_orders_for_delivery(db, today)
    
    # Today's revenue
    today_revenue = 0.0
    completed_payments = crud_payment.get_by_status(db, "completed")
    for payment in completed_payments:
        if payment.created_at.date() == today.date():
            today_revenue += payment.amount
    
    # Pending deliveries
    pending_deliveries = crud_delivery.get_pending_deliveries(db)
    
    return {
        "total_customers": total_customers,
        "total_agents": total_agents,
        "total_products": total_products,
        "today_orders_count": len(today_orders),
        "today_revenue": today_revenue,
        "pending_deliveries": len(pending_deliveries),
    }


@router.get("/revenue-report")
async def get_revenue_report(
    days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get revenue report for specified days."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    payments_query = db.query(
        func.date(Payment.created_at).label("date"),
        func.sum(Payment.amount).label("total_amount"),
        func.count(Payment.id).label("transaction_count"),
    ).filter(
        Payment.created_at >= start_date,
        Payment.status == "completed"
    ).group_by(func.date(Payment.created_at)).all()
    
    daily_revenue = []
    total_revenue = 0.0
    for date_val, amount, count in payments_query:
        daily_revenue.append({
            "date": str(date_val),
            "amount": float(amount) if amount else 0.0,
            "transactions": count
        })
        total_revenue += float(amount) if amount else 0.0
    
    return {
        "period_days": days,
        "total_revenue": total_revenue,
        "daily_breakdown": daily_revenue,
    }


@router.get("/delivery-report")
async def get_delivery_report(
    days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get delivery report for specified days."""
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Total deliveries
    deliveries = db.query(Delivery).filter(
        Delivery.created_at >= start_date
    ).all()
    
    delivered_count = 0
    failed_count = 0
    total_earnings = 0.0
    
    agent_performance = {}
    
    for delivery in deliveries:
        if delivery.status == "delivered":
            delivered_count += 1
        elif delivery.status == "failed":
            failed_count += 1
        
        if delivery.agent_id:
            if delivery.agent_id not in agent_performance:
                agent_performance[delivery.agent_id] = {
                    "delivered": 0,
                    "failed": 0,
                    "earnings": 0.0
                }
            
            if delivery.status == "delivered":
                agent_performance[delivery.agent_id]["delivered"] += 1
                # Commission calculation
                order = crud_order.get(db, delivery.order_id)
                if order:
                    agent_performance[delivery.agent_id]["earnings"] += order.total_amount * 0.05
            elif delivery.status == "failed":
                agent_performance[delivery.agent_id]["failed"] += 1
    
    return {
        "period_days": days,
        "total_deliveries": len(deliveries),
        "delivered_count": delivered_count,
        "failed_count": failed_count,
        "delivery_success_rate": (delivered_count / len(deliveries) * 100) if deliveries else 0,
        "agent_performance": agent_performance,
    }


@router.get("/product-report")
async def get_product_report(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get product sales report."""
    
    products = crud_product.get_multi(db, limit=1000)
    
    product_stats = []
    for product in products:
        # Count orders
        orders = db.query(Order).filter(Order.product_id == product.id).all()
        total_quantity = sum(order.quantity for order in orders)
        total_sales = sum(order.total_amount for order in orders)
        
        product_stats.append({
            "product_id": product.id,
            "name": product.name,
            "type": product.product_type,
            "orders_count": len(orders),
            "total_quantity_sold": total_quantity,
            "total_sales_amount": total_sales,
        })
    
    return {
        "products": product_stats,
    }


@router.get("/customer-report")
async def get_customer_report(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Get customer report."""
    
    customers = crud_customer.get_multi(db, limit=1000)
    
    total_customers = len(customers)
    customers_with_pending = len([c for c in customers if c.total_amount_due > 0])
    total_pending_amount = sum(c.total_amount_due for c in customers)
    
    return {
        "total_customers": total_customers,
        "customers_with_pending_balance": customers_with_pending,
        "total_pending_amount": total_pending_amount,
        "average_pending_per_customer": total_pending_amount / total_customers if total_customers > 0 else 0,
    }


@router.post("/fix-unassigned-deliveries")
async def fix_unassigned_deliveries(
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """Fix deliveries without assigned agents and link reviews to agents."""
    import logging
    import random
    import string
    
    logger = logging.getLogger(__name__)
    
    try:
        # Get all unassigned deliveries
        unassigned_deliveries = db.query(Delivery).filter(Delivery.agent_id == None).all()
        logger.info(f"Found {len(unassigned_deliveries)} unassigned deliveries")
        
        # Get available agents
        from app.models.agent import Agent
        from app.models.review import Review
        
        available_agents = db.query(Agent).filter(Agent.available_for_delivery == True).all()
        
        if not available_agents:
            return {
                "status": "failed",
                "message": "No available agents to assign",
                "fixed_count": 0,
            }
        
        fixed_count = 0
        
        # Assign agents to unassigned deliveries
        for delivery in unassigned_deliveries:
            # Round-robin assignment
            agent = available_agents[fixed_count % len(available_agents)]
            delivery.agent_id = agent.id
            
            # Generate OTP if missing
            if not delivery.delivery_otp:
                otp = ''.join(random.choices(string.digits, k=6))
                delivery.delivery_otp = otp
            
            db.add(delivery)
            fixed_count += 1
            
            # Update reviews for this delivery to link to the agent
            reviews = db.query(Review).filter(
                Review.order_id == delivery.order_id,
                Review.agent_id == None
            ).all()
            
            for review in reviews:
                review.agent_id = agent.id
                db.add(review)
                logger.info(f"Linked review {review.id} to agent {agent.id}")
        
        db.commit()
        logger.info(f"Fixed {fixed_count} unassigned deliveries")
        
        return {
            "status": "success",
            "message": f"Fixed {fixed_count} deliveries and linked reviews to agents",
            "fixed_count": fixed_count,
        }
        
    except Exception as e:
        logger.error(f"Error fixing deliveries: {str(e)}", exc_info=True)
        return {
            "status": "error",
            "message": str(e),
            "fixed_count": 0,
        }
