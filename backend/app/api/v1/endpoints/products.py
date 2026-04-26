"""Product endpoints for browsing and viewing."""
from fastapi import APIRouter, Depends, HTTPException, status, Query,UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.crud.product import crud_product
from app.crud.review import crud_review
from app.schemas.product import ProductResponse, ProductCreate, ProductUpdate
from app.core.dependencies import get_current_admin_user
from app.models.user import User
from app.services.file_upload import upload_product_image, delete_product_image
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=List[ProductResponse])
async def list_products(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """List all active products."""
    products = crud_product.get_active_products(db, skip=skip, limit=limit)
    return products


@router.get("/search", response_model=List[ProductResponse])
async def search_products(
    query: str = Query(..., min_length=1),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Search products by name or description."""
    products = crud_product.search_products(db, query, skip=skip, limit=limit)
    return products


@router.get("/type/{product_type}", response_model=List[ProductResponse])
async def get_products_by_type(
    product_type: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """Get products by type."""
    products = crud_product.get_by_type(db, product_type, skip=skip, limit=limit)
    return products


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int, db: Session = Depends(get_db)):
    """Get product details."""
    product = crud_product.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    return product


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Create new product (admin only)."""
    product = crud_product.create(db, product_data)
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Update product (admin only)."""
    product = crud_product.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    product = crud_product.update(db, product, product_data)
    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Delete product (admin only)."""
    product = crud_product.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    crud_product.delete(db, product_id)
    return {"message": "Product deleted successfully"}



@router.post("/{product_id}/upload-image")
async def upload_product_image_endpoint(
    product_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Upload image for a product (admin only)."""
    product = crud_product.get(db, product_id)
    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    
    # Save old image URL for cleanup
    old_image_url = product.image_url
    
    # Upload new image
    image_url = await upload_product_image(file)
    
    # Update product with new image URL
    product.image_url = image_url
    db.add(product)
    db.commit()
    db.refresh(product)
    
    # Delete old image if it existed
    if old_image_url:
        delete_product_image(old_image_url)
    
    return {"image_url": image_url, "message": "Image uploaded successfully"}