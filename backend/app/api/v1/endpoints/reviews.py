"""Review endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.dependencies import get_current_customer_user, get_current_admin_user
from app.crud.review import crud_review
from app.crud.order import crud_order
from app.crud.delivery import crud_delivery
from app.crud.customer import crud_customer
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.models.user import User
from app.models.review import Review

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Create product review (customer)."""
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        logger.info(f"Creating review for user {current_user.id}, order {review_data.order_id}")
        
        customer = crud_customer.get_by_user_id(db, current_user.id)
        if not customer:
            logger.error(f"Customer profile not found for user {current_user.id}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
        
        # Verify customer ordered this product
        order = crud_order.get(db, review_data.order_id)
        if not order:
            logger.error(f"Order {review_data.order_id} not found")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")
        
        if order.customer_id != customer.id:
            logger.error(f"Order {review_data.order_id} doesn't belong to customer {customer.id}")
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You didn't place this order")
        
        # Create review object from request data
        review_dict = review_data.dict(exclude_unset=True)
        review_dict["customer_id"] = customer.id
        
        logger.info(f"Review dict before delivery check: {review_dict}")
        
        # Get delivery and agent info
        delivery = crud_delivery.get_by_order(db, review_data.order_id)
        if delivery:
            logger.info(f"Found delivery {delivery.id} for order {review_data.order_id}")
            logger.info(f"Delivery agent_id: {delivery.agent_id}")
            if delivery.agent_id:
                review_dict["agent_id"] = delivery.agent_id
                logger.info(f"Set agent_id to {delivery.agent_id}")
            else:
                logger.warning(f"Delivery {delivery.id} has no agent_id assigned")
        else:
            logger.warning(f"No delivery found for order {review_data.order_id}")
        
        logger.info(f"Final review dict: {review_dict}")
        
        # Create Review model instance directly
        db_review = Review(**review_dict)
        db.add(db_review)
        db.commit()
        db.refresh(db_review)
        
        logger.info(f"Review created successfully: {db_review.id}, agent_id: {db_review.agent_id}, agent_rating: {db_review.agent_rating}")
        return db_review
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating review: {str(e)}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create review: {str(e)}")


@router.get("/product/{product_id}", response_model=List[ReviewResponse])
async def get_product_reviews(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get reviews for product."""
    reviews = crud_review.get_by_product(db, product_id, skip=skip, limit=limit)
    return reviews


@router.get("/my-reviews", response_model=List[ReviewResponse])
async def get_my_reviews(
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Get my reviews (customer)."""
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if not customer:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer profile not found")
    
    reviews = crud_review.get_by_customer(db, customer.id)
    return reviews


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: int,
    update_data: ReviewUpdate,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Update review (customer)."""
    review = crud_review.get(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if review.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    review = crud_review.update(db, review, update_data)
    return review


@router.delete("/{review_id}")
async def delete_review(
    review_id: int,
    current_user: User = Depends(get_current_customer_user),
    db: Session = Depends(get_db),
):
    """Delete review (customer)."""
    review = crud_review.get(db, review_id)
    if not review:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Review not found")
    
    customer = crud_customer.get_by_user_id(db, current_user.id)
    if review.customer_id != customer.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied")
    
    crud_review.delete(db, review_id)
    return {"message": "Review deleted successfully"}


@router.get("/product/{product_id}/rating", response_model=dict)
async def get_product_rating(
    product_id: int,
    db: Session = Depends(get_db),
):
    """Get product average rating."""
    avg_rating = crud_review.get_average_rating_by_product(db, product_id)
    review_count = crud_review.get_product_review_count(db, product_id)
    return {
        "product_id": product_id,
        "average_rating": avg_rating or 0,
        "review_count": review_count
    }
