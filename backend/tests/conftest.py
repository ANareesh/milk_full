"""Test configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
import os

from app.core.database import Base, get_db
from app.main import app
from app.models.user import User, UserRole
from app.models.customer import Customer
from app.models.agent import Agent
from app.models.product import Product, ProductType
from app.core.security import PasswordUtils

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="function")
def db():
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def admin_user(db: Session):
    """Create test admin user."""
    user = User(
        username="admin_test",
        email="admin@test.com",
        full_name="Admin User",
        phone_number="1234567890",
        role=UserRole.admin,
        hashed_password=PasswordUtils.hash_password("password123"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def customer_user(db: Session):
    """Create test customer user."""
    user = User(
        username="customer_test",
        email="customer@test.com",
        full_name="Customer User",
        phone_number="9876543210",
        role=UserRole.customer,
        hashed_password=PasswordUtils.hash_password("password123"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def agent_user(db: Session):
    """Create test agent user."""
    user = User(
        username="agent_test",
        email="agent@test.com",
        full_name="Agent User",
        phone_number="5555555555",
        role=UserRole.agent,
        hashed_password=PasswordUtils.hash_password("password123"),
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def customer_profile(db: Session, customer_user: User):
    """Create customer profile."""
    customer = Customer(
        user_id=customer_user.id,
        address="123 Main St",
        city="Mumbai",
        postal_code="400001",
        preferred_delivery_time="morning",
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


@pytest.fixture
def agent_profile(db: Session, agent_user: User):
    """Create agent profile."""
    agent = Agent(
        user_id=agent_user.id,
        agent_code="AG001",
        assigned_area="Mumbai - Zone A",
        vehicle_number="MH01AB1234",
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    return agent


@pytest.fixture
def test_product(db: Session):
    """Create test product."""
    product = Product(
        name="Full Cream Milk",
        description="Fresh full cream milk",
        product_type=ProductType.full_cream,
        unit="liter",
        unit_price=60.0,
        available_quantity=100.0,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def admin_token(admin_user: User):
    """Get admin user token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "admin_test", "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def customer_token(customer_user: User):
    """Get customer user token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "customer_test", "password": "password123"}
    )
    return response.json()["access_token"]


@pytest.fixture
def agent_token(agent_user: User):
    """Get agent user token."""
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "agent_test", "password": "password123"}
    )
    return response.json()["access_token"]



# Add these fixtures for map testing
@pytest.fixture
def admin_token(db: Session):
    """Create admin user and return token."""
    from app.services.auth import AuthService
    
    admin_user = User(
        email="admin@test.com",
        hashed_password=AuthService.hash_password("password"),
        full_name="Admin User",
        phone="9999999999",
        role="admin"
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    token = AuthService.create_access_token({"sub": admin_user.id, "role": "admin"})
    return token

@pytest.fixture
def customer_token(db: Session):
    """Create customer user and return token."""
    from app.services.auth import AuthService
    
    customer_user = User(
        email="customer@test.com",
        hashed_password=AuthService.hash_password("password"),
        full_name="Customer User",
        phone="9988888888",
        role="customer"
    )
    db.add(customer_user)
    db.commit()
    db.refresh(customer_user)
    
    token = AuthService.create_access_token({"sub": customer_user.id, "role": "customer"})
    return token

@pytest.fixture
def second_agent_id(db: Session):
    """Create second agent for testing."""
    from app.models.agent import Agent
    
    user = User(
        email="agent2@test.com",
        hashed_password=AuthService.hash_password("password"),
        full_name="Second Agent",
        phone="9977777777",
        role="agent"
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    agent = Agent(
        user_id=user.id,
        agent_code="AGT002",
        phone="9977777777"
    )
    db.add(agent)
    db.commit()
    db.refresh(agent)
    
    return agent.id