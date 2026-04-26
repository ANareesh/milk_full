"""Test product endpoints."""
import pytest
from fastapi.testclient import TestClient
from tests.utils import get_auth_headers

from app.main import app

client = TestClient(app)


class TestProducts:
    """Product endpoint tests."""

    def test_list_products(self, test_product):
        """Test listing products."""
        response = client.get("/api/v1/products/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert data[0]["name"] == "Full Cream Milk"

    def test_list_products_pagination(self, test_product, db):
        """Test products pagination."""
        # Create multiple products
        from app.models.product import Product, ProductType
        for i in range(15):
            product = Product(
                name=f"Product {i}",
                product_type=ProductType.toned,
                unit_price=50.0 + i,
                available_quantity=100.0,
                is_active=True,
            )
            db.add(product)
        db.commit()

        # Test limit
        response = client.get("/api/v1/products/?limit=5")
        assert response.status_code == 200
        assert len(response.json()) == 5

        # Test skip
        response = client.get("/api/v1/products/?skip=5&limit=5")
        assert response.status_code == 200
        assert len(response.json()) == 5

    def test_search_products(self, test_product):
        """Test product search."""
        response = client.get("/api/v1/products/search?query=cream")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_search_no_results(self, test_product):
        """Test search with no results."""
        response = client.get("/api/v1/products/search?query=xyz_nonexistent")
        assert response.status_code == 200
        assert len(response.json()) == 0

    def test_get_products_by_type(self, test_product):
        """Test getting products by type."""
        response = client.get("/api/v1/products/type/full_cream")
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_product_details(self, test_product):
        """Test getting product details."""
        response = client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == "Full Cream Milk"

    def test_get_nonexistent_product(self):
        """Test getting non-existent product."""
        response = client.get("/api/v1/products/99999")
        assert response.status_code == 404

    def test_create_product_admin(self, admin_token):
        """Test creating product (admin only)."""
        headers = get_auth_headers(admin_token)
        response = client.post(
            "/api/v1/products/",
            headers=headers,
            json={
                "name": "New Product",
                "description": "New dairy product",
                "product_type": "toned",
                "unit": "liter",
                "unit_price": 55.0,
                "available_quantity": 50.0,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Product"

    def test_create_product_non_admin(self, customer_token):
        """Test creating product (non-admin denied)."""
        headers = get_auth_headers(customer_token)
        response = client.post(
            "/api/v1/products/",
            headers=headers,
            json={
                "name": "New Product",
                "product_type": "toned",
                "unit_price": 55.0,
            }
        )
        assert response.status_code == 403

    def test_update_product(self, test_product, admin_token):
        """Test updating product."""
        headers = get_auth_headers(admin_token)
        response = client.put(
            f"/api/v1/products/{test_product.id}",
            headers=headers,
            json={
                "unit_price": 75.0,
                "available_quantity": 200.0,
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["unit_price"] == 75.0

    def test_delete_product(self, test_product, admin_token):
        """Test deleting product."""
        headers = get_auth_headers(admin_token)
        response = client.delete(
            f"/api/v1/products/{test_product.id}",
            headers=headers,
        )
        assert response.status_code == 200

        # Verify deletion
        response = client.get(f"/api/v1/products/{test_product.id}")
        assert response.status_code == 404
