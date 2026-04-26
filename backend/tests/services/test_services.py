"""Test service layer."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.services.auth import auth_service
from app.services.order import order_service
from app.schemas.user import UserCreate
from app.models.user import UserRole


class TestAuthService:
    """Test authentication service."""

    def test_register_user_success(self, db: Session):
        """Test successful user registration."""
        user_data = UserCreate(
            username="newuser",
            email="newuser@test.com",
            password="SecurePass123!",
            full_name="New User",
            role=UserRole.customer,
        )
        user = auth_service.register_user(db, user_data)
        assert user.username == "newuser"
        assert user.email == "newuser@test.com"

    def test_register_user_duplicate_username(self, db: Session, customer_user):
        """Test registration with duplicate username."""
        user_data = UserCreate(
            username="customer_test",
            email="different@test.com",
            password="SecurePass123!",
            full_name="Different User",
            role=UserRole.customer,
        )
        with pytest.raises(ValueError):
            auth_service.register_user(db, user_data)

    def test_authenticate_user(self, db: Session, customer_user):
        """Test user authentication."""
        user = auth_service.authenticate_user(db, "customer_test", "password123")
        assert user is not None
        assert user.username == "customer_test"

    def test_login_returns_tokens(self, db: Session, customer_user):
        """Test login returns tokens."""
        token_response = auth_service.login(db, "customer_test", "password123")
        assert token_response is not None
        assert token_response.access_token
        assert token_response.refresh_token


class TestOrderService:
    """Test order service."""

    def test_create_one_time_order(self, db: Session, customer_profile, test_product):
        """Test creating one-time order."""
        from app.schemas.order import OrderCreateOneTime
        
        delivery_date = datetime.utcnow() + timedelta(days=1)
        order_data = OrderCreateOneTime(
            product_id=test_product.id,
            quantity=5.0,
            delivery_date=delivery_date,
        )
        
        order = order_service.create_one_time_order(db, customer_profile.id, order_data)
        assert order.quantity == 5.0
        assert order.order_type == "one_time"
        assert order.status == "pending"

    def test_create_order_insufficient_stock(self, db: Session, customer_profile, test_product):
        """Test creating order with insufficient stock."""
        from app.schemas.order import OrderCreateOneTime
        
        test_product.available_quantity = 2.0
        db.add(test_product)
        db.commit()
        
        delivery_date = datetime.utcnow() + timedelta(days=1)
        order_data = OrderCreateOneTime(
            product_id=test_product.id,
            quantity=5.0,
            delivery_date=delivery_date,
        )
        
        with pytest.raises(ValueError):
            order_service.create_one_time_order(db, customer_profile.id, order_data)

    def test_cancel_order(self, db: Session, customer_profile, test_product):
        """Test canceling order."""
        from app.schemas.order import OrderCreateOneTime
        from app.crud.order import crud_order
        
        delivery_date = datetime.utcnow() + timedelta(days=1)
        order_data = OrderCreateOneTime(
            product_id=test_product.id,
            quantity=5.0,
            delivery_date=delivery_date,
        )
        
        order = order_service.create_one_time_order(db, customer_profile.id, order_data)
        cancelled = order_service.cancel_order(db, order)
        
        assert cancelled.status == "cancelled"
