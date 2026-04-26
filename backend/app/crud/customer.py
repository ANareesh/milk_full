"""Customer CRUD operations."""
from sqlalchemy.orm import Session
from typing import Optional

from app.crud.base import CRUDBase
from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


class CRUDCustomer(CRUDBase[Customer, CustomerCreate, CustomerUpdate]):
    """CRUD operations for Customer model."""

    def get_by_user_id(self, db: Session, user_id: int) -> Optional[Customer]:
        """Get customer by user id."""
        return db.query(Customer).filter(Customer.user_id == user_id).first()

    def get_by_city(self, db: Session, city: str, skip: int = 0, limit: int = 100):
        """Get customers by city."""
        return db.query(Customer).filter(Customer.city == city).offset(skip).limit(limit).all()

    def get_customers_with_pending_balance(self, db: Session, skip: int = 0, limit: int = 100):
        """Get customers with pending balance."""
        return db.query(Customer).filter(Customer.total_amount_due > 0).offset(skip).limit(limit).all()

    def update_amount_due(self, db: Session, customer: Customer, amount: float) -> Customer:
        """Update amount due."""
        customer.total_amount_due += amount
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer

    def set_location(self, db: Session, customer: Customer, latitude: float, longitude: float) -> Customer:
        """Set customer location."""
        customer.latitude = latitude
        customer.longitude = longitude
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer


crud_customer = CRUDCustomer(Customer)
