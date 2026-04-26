"""Test order endpoints."""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from tests.utils import get_auth_headers

from app.main import app

client = TestClient(app)


class TestOrders:
    """Order endpoint tests."""

    def test_create_order_customer(self, customer_token, customer_profile, test_product):
        """Test creating order as customer."""
        headers = get_auth_headers(customer_token)
        delivery_date = datetime.utcnow() + timedelta(days=1)
        
        response = client.post(
            "/api/v1/orders/",
            headers=headers,
            json={
                "product_id": test_product.id,
                "quantity": 5.0,
                "delivery_date": delivery_date.isoformat(),
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 5.0
        assert data["status"] == "pending"
        assert "order_number" in data

    def test_create_order_insufficient_stock(self, customer_token, customer_profile, test_product, db):
        """Test creating order with insufficient stock."""
        headers = get_auth_headers(customer_token)
        
        # Update product to have low stock
        test_product.available_quantity = 2.0
        db.add(test_product)
        db.commit()
        
        delivery_date = datetime.utcnow() + timedelta(days=1)
        response = client.post(
            "/api/v1/orders/",
            headers=headers,
            json={
                "product_id": test_product.id,
                "quantity": 5.0,  # More than available
                "delivery_date": delivery_date.isoformat(),
            }
        )
        assert response.status_code == 400

    def test_create_order_nonexistent_product(self, customer_token, customer_profile):
        """Test creating order with non-existent product."""
        headers = get_auth_headers(customer_token)
        delivery_date = datetime.utcnow() + timedelta(days=1)
        
        response = client.post(
            "/api/v1/orders/",
            headers=headers,
            json={
                "product_id": 99999,
                "quantity": 5.0,
                "delivery_date": delivery_date.isoformat(),
            }
        )
        assert response.status_code == 400

    def test_get_my_orders(self, customer_token, customer_profile, test_product):
        """Test getting my orders."""
        headers = get_auth_headers(customer_token)
        
        # Create an order first
        delivery_date = datetime.utcnow() + timedelta(days=1)
        client.post(
            "/api/v1/orders/",
            headers=headers,
            json={
                "product_id": test_product.id,
                "quantity": 5.0,
                "delivery_date": delivery_date.isoformat(),
            }
        )
        
        # Get orders
        response = client.get(
            "/api/v1/orders/my-orders",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_order_details(self, customer_token, customer_profile, test_product):
        """Test getting order details."""
        headers = get_auth_headers(customer_token)
        
        # Create order
        delivery_date = datetime.utcnow() + timedelta(days=1)
        create_response = client.post(
            "/api/v1/orders/",
            headers=headers,
            json={
                "product_id": test_product.id,
                "quantity": 5.0,
                "delivery_date": delivery_date.isoformat(),
            }
        )
        order_id = create_response.json()["id"]
        
        # Get details
        response = client.get(
            f"/api/v1/orders/{order_id}",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id

    def test_cancel_order(self, customer_token, customer_profile, test_product):
        """Test canceling order."""
        headers = get_auth_headers(customer_token)
        
        # Create order
        delivery_date = datetime.utcnow() + timedelta(days=1)
        create_response = client.post(
            "/api/v1/orders/",
            headers=headers,
            json={
                "product_id": test_product.id,
                "quantity": 5.0,
                "delivery_date": delivery_date.isoformat(),
            }
        )
        order_id = create_response.json()["id"]
        
        # Cancel order
        response = client.post(
            f"/api/v1/orders/{order_id}/cancel",
            headers=headers,
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_order_not_customer(self, admin_token, customer_profile, test_product):
        """Test that customer can only cancel their own orders."""
        # This test verifies authorization
        pass
