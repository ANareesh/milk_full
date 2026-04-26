"""Review CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate


class CRUDReview(CRUDBase[Review, ReviewCreate, ReviewUpdate]):
    """CRUD operations for Review model."""

    def get_by_customer(self, db: Session, customer_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get reviews by customer."""
        return db.query(Review).filter(Review.customer_id == customer_id).offset(skip).limit(limit).all()

    def get_by_product(self, db: Session, product_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get reviews by product."""
        return db.query(Review).filter(Review.product_id == product_id).offset(skip).limit(limit).all()

    def get_by_order(self, db: Session, order_id: int) -> Optional[Review]:
        """Get review for order."""
        return db.query(Review).filter(Review.order_id == order_id).first()

    def get_by_agent(self, db: Session, agent_id: int, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get reviews for agent."""
        return db.query(Review).filter(Review.agent_id == agent_id).offset(skip).limit(limit).all()

    def get_recommended_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[Review]:
        """Get recommended products."""
        return db.query(Review).filter(Review.is_recommended == True).offset(skip).limit(limit).all()

    def get_average_rating_by_product(self, db: Session, product_id: int) -> Optional[float]:
        """Get average rating for product."""
        from sqlalchemy import func
        result = db.query(func.avg(Review.rating)).filter(Review.product_id == product_id).scalar()
        return round(result, 2) if result else None

    def get_average_rating_by_agent(self, db: Session, agent_id: int) -> Optional[float]:
        """Get average rating for agent."""
        from sqlalchemy import func
        result = db.query(func.avg(Review.agent_rating)).filter(
            Review.agent_id == agent_id,
            Review.agent_rating != None
        ).scalar()
        return round(result, 2) if result else None

    def get_product_review_count(self, db: Session, product_id: int) -> int:
        """Get review count for product."""
        return db.query(Review).filter(Review.product_id == product_id).count()


crud_review = CRUDReview(Review)
