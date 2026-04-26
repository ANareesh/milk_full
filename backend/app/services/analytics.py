from sqlalchemy.orm import Session
from ..models.milk_collection import MilkCollection
from ..models.payment import Payment
from sqlalchemy import func
from datetime import datetime, timedelta

def get_collection_summary(db: Session, user_id: int, period: str):
    # period: "daily", "weekly", "monthly"
    now = datetime.utcnow()
    if period == "daily":
        start = now - timedelta(days=1)
    elif period == "weekly":
        start = now - timedelta(weeks=1)
    else:
        start = now - timedelta(days=30)
    total = db.query(func.sum(MilkCollection.quantity_liters)).filter(
        MilkCollection.farmer_id == user_id,
        MilkCollection.collection_time >= start
    ).scalar() or 0
    return {"period": period, "total_collected": total}

def get_performance_analytics(db: Session, user_id: int):
    # Example: average fat/SNF, total collections, etc.
    avg_fat = db.query(func.avg(MilkCollection.fat_percentage)).filter(
        MilkCollection.farmer_id == user_id
    ).scalar()
    count = db.query(func.count(MilkCollection.id)).filter(
        MilkCollection.farmer_id == user_id
    ).scalar()
    return {"avg_fat": avg_fat, "collections": count}

def get_payment_trends(db: Session, user_id: int):
    # Example: total payments, monthly trend
    total = db.query(func.sum(Payment.amount)).filter(
        Payment.customer_id == user_id
    ).scalar() or 0
    return {"total_payments": total}