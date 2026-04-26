"""Test authentication endpoints."""
import pytest
from tests.utils import get_auth_headers
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestAuthentication:
    """Authentication endpoint tests."""

    def test_register_customer_success(self):
        """Test successful customer registration."""
        response = client.post(
            "/api/v1/auth/register/customer",
            json={
                "username": "newcustomer",
                "email": "newcustomer@test.com",
                "password": "SecurePass123!",
                "full_name": "New Customer",
                "phone_number": "1234567890",
                "role": "customer",
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newcustomer"
        assert data["email"] == "newcustomer@test.com"
        assert data["role"] == "customer"

    def test_register_customer_duplicate_username(self):
        """Test duplicate username registration."""
        # Register first user
        client.post(
            "/api/v1/auth/register/customer",
            json={
                "username": "duplicate_user",
                "email": "first@test.com",
                "password": "SecurePass123!",
                "full_name": "User One",
                "role": "customer",
            }
        )
        
        # Try to register with same username
        response = client.post(
            "/api/v1/auth/register/customer",
            json={
                "username": "duplicate_user",
                "email": "second@test.com",
                "password": "SecurePass123!",
                "full_name": "User Two",
                "role": "customer",
            }
        )
        assert response.status_code == 400

    def test_register_customer_duplicate_email(self):
        """Test duplicate email registration."""
        # Register first user
        client.post(
            "/api/v1/auth/register/customer",
            json={
                "username": "user_one",
                "email": "duplicate@test.com",
                "password": "SecurePass123!",
                "full_name": "User One",
                "role": "customer",
            }
        )
        
        # Try to register with same email
        response = client.post(
            "/api/v1/auth/register/customer",
            json={
                "username": "user_two",
                "email": "duplicate@test.com",
                "password": "SecurePass123!",
                "full_name": "User Two",
                "role": "customer",
            }
        )
        assert response.status_code == 400

    def test_login_success(self, customer_user):
        """Test successful login."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "customer_test", "password": "password123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_password(self, customer_user):
        """Test login with wrong password."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "customer_test", "password": "wrong_password"}
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self):
        """Test login with non-existent user."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401

    def test_login_with_email(self, customer_user):
        """Test login using email instead of username."""
        response = client.post(
            "/api/v1/auth/login",
            json={"username": "customer@test.com", "password": "password123"}
        )
        assert response.status_code == 200

    def test_refresh_token_success(self, customer_token):
        """Test token refresh."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": customer_token}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_token_invalid(self):
        """Test token refresh with invalid token."""
        response = client.post(
            "/api/v1/auth/refresh",
            json={"refresh_token": "invalid_token"}
        )
        assert response.status_code == 401
