"""Test CRUD operations."""
import pytest
from sqlalchemy.orm import Session

from app.crud.user import crud_user
from app.crud.customer import crud_customer
from app.crud.product import crud_product
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.schemas.customer import CustomerCreate
from app.models.product import ProductType
from app.core.security import PasswordUtils


class TestUserCRUD:
    """Test User CRUD operations."""

    def test_create_user(self, db: Session):
        """Test creating user."""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            password="SecurePass123!",
            full_name="Test User",
            phone_number="1234567890",
            role=UserRole.customer,
        )
        user = crud_user.create(db, user_data)
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert PasswordUtils.verify_password("SecurePass123!", user.hashed_password)

    def test_get_user_by_username(self, db: Session, customer_user):
        """Test getting user by username."""
        user = crud_user.get_by_username(db, "customer_test")
        assert user is not None
        assert user.email == "customer@test.com"

    def test_get_user_by_email(self, db: Session, customer_user):
        """Test getting user by email."""
        user = crud_user.get_by_email(db, "customer@test.com")
        assert user is not None
        assert user.username == "customer_test"

    def test_get_user_by_username_or_email(self, db: Session, customer_user):
        """Test getting user by username or email."""
        user1 = crud_user.get_by_username_or_email(db, "customer_test")
        user2 = crud_user.get_by_username_or_email(db, "customer@test.com")
        assert user1.id == user2.id

    def test_authenticate_user_success(self, db: Session, customer_user):
        """Test authenticating user."""
        user = crud_user.authenticate(db, "customer_test", "password123")
        assert user is not None
        assert user.username == "customer_test"

    def test_authenticate_user_wrong_password(self, db: Session, customer_user):
        """Test authentication with wrong password."""
        user = crud_user.authenticate(db, "customer_test", "wrongpassword")
        assert user is None

    def test_authenticate_user_not_found(self, db: Session):
        """Test authentication with non-existent user."""
        user = crud_user.authenticate(db, "nonexistent", "password123")
        assert user is None

    def test_get_users_by_role(self, db: Session, customer_user, agent_user, admin_user):
        """Test getting users by role."""
        customers = crud_user.get_by_role(db, UserRole.customer)
        assert len(customers) >= 1

        agents = crud_user.get_by_role(db, UserRole.agent)
        assert len(agents) >= 1


class TestCustomerCRUD:
    """Test Customer CRUD operations."""

    def test_create_customer(self, db: Session, customer_user):
        """Test creating customer."""
        customer_data = CustomerCreate(
            user_id=customer_user.id,
            address="456 Test Ave",
            city="Bangalore",
            postal_code="560001",
        )
        customer = crud_customer.create(db, customer_data)
        assert customer.user_id == customer_user.id
        assert customer.city == "Bangalore"

    def test_get_customer_by_user_id(self, db: Session, customer_profile):
        """Test getting customer by user id."""
        customer = crud_customer.get_by_user_id(db, customer_profile.user_id)
        assert customer is not None
        assert customer.city == "Mumbai"

    def test_get_customers_by_city(self, db: Session, customer_profile):
        """Test getting customers by city."""
        customers = crud_customer.get_by_city(db, "Mumbai")
        assert len(customers) >= 1

    def test_update_amount_due(self, db: Session, customer_profile):
        """Test updating customer amount due."""
        initial_due = customer_profile.total_amount_due
        updated = crud_customer.update_amount_due(db, customer_profile, 500.0)
        assert updated.total_amount_due == initial_due + 500.0


class TestProductCRUD:
    """Test Product CRUD operations."""

    def test_get_active_products(self, db: Session, test_product):
        """Test getting active products."""
        products = crud_product.get_active_products(db)
        assert len(products) >= 1

    def test_get_products_by_type(self, db: Session, test_product):
        """Test getting products by type."""
        products = crud_product.get_by_type(db, ProductType.full_cream)
        assert len(products) >= 1
        assert products[0].name == "Full Cream Milk"

    def test_search_products(self, db: Session, test_product):
        """Test searching products."""
        products = crud_product.search_products(db, "cream")
        assert len(products) >= 1

    def test_search_no_results(self, db: Session):
        """Test search with no results."""
        products = crud_product.search_products(db, "xyz_nonexistent_product")
        assert len(products) == 0

    def test_reduce_quantity(self, db: Session, test_product):
        """Test reducing product quantity."""
        initial_quantity = test_product.available_quantity
        updated = crud_product.reduce_quantity(db, test_product, 10.0)
        assert updated.available_quantity == initial_quantity - 10.0

    def test_increase_quantity(self, db: Session, test_product):
        """Test increasing product quantity."""
        initial_quantity = test_product.available_quantity
        updated = crud_product.increase_quantity(db, test_product, 10.0)
        assert updated.available_quantity == initial_quantity + 10.0
