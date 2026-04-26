from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ...core.dependencies import get_db, get_current_user
from ...services.analytics import (
    get_collection_summary,
    get_performance_analytics,
    get_payment_trends,
)

router = APIRouter()

@router.get("/summary")
def collection_summary(period: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_collection_summary(db, user.id, period)

@router.get("/performance")
def performance_analytics(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_performance_analytics(db, user.id)

@router.get("/payment-trends")
def payment_trends(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return get_payment_trends(db, user.id)