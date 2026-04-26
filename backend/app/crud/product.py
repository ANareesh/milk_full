"""Product CRUD operations."""
from sqlalchemy.orm import Session
from typing import List, Optional

from app.crud.base import CRUDBase
from app.models.product import Product, ProductType
from app.schemas.product import ProductCreate, ProductUpdate


class CRUDProduct(CRUDBase[Product, ProductCreate, ProductUpdate]):
    """CRUD operations for Product model."""

    def get_active_products(self, db: Session, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get active products."""
        return db.query(Product).filter(Product.is_active == True).offset(skip).limit(limit).all()

    def get_by_type(self, db: Session, product_type: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Get products by type."""
        return db.query(Product).filter(
            Product.product_type == product_type,
            Product.is_active == True
        ).offset(skip).limit(limit).all()

    def get_by_name(self, db: Session, name: str) -> Optional[Product]:
        """Get product by name."""
        return db.query(Product).filter(Product.name == name).first()

    def search_products(self, db: Session, query: str, skip: int = 0, limit: int = 100) -> List[Product]:
        """Search products by name or description."""
        search_query = f"%{query}%"
        return db.query(Product).filter(
            (Product.name.ilike(search_query) | Product.description.ilike(search_query)),
            Product.is_active == True
        ).offset(skip).limit(limit).all()

    def update_quantity(self, db: Session, product: Product, quantity: float) -> Product:
        """Update product quantity."""
        product.available_quantity = quantity
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def reduce_quantity(self, db: Session, product: Product, quantity: float) -> Product:
        """Reduce product quantity."""
        product.available_quantity -= quantity
        db.add(product)
        db.commit()
        db.refresh(product)
        return product

    def increase_quantity(self, db: Session, product: Product, quantity: float) -> Product:
        """Increase product quantity."""
        product.available_quantity += quantity
        db.add(product)
        db.commit()
        db.refresh(product)
        return product


crud_product = CRUDProduct(Product)
