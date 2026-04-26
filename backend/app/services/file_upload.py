"""File upload service for handling image uploads."""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile, HTTPException, status

# Create uploads directory if it doesn't exist
UPLOAD_DIR = Path("uploads/products")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Allowed file types
ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "gif", "webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


async def upload_product_image(file: UploadFile) -> str:
    """
    Upload a product image and return the relative URL path.
    
    Returns: URL path like /uploads/products/filename.jpg
    """
    
    # Validate file extension
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided"
        )
    
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type .{file_ext} not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Validate file size
    file_content = await file.read()
    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds {MAX_FILE_SIZE / (1024*1024)}MB limit"
        )
    
    # Generate unique filename
    unique_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = UPLOAD_DIR / unique_filename
    
    # Save file
    with open(file_path, "wb") as f:
        f.write(file_content)
    
    # Return relative URL path
    return f"/uploads/products/{unique_filename}"


def delete_product_image(image_url: Optional[str]) -> None:
    """Delete a product image if it exists."""
    if not image_url or not image_url.startswith("/uploads/products/"):
        return
    
    try:
        # Extract filename from URL
        filename = image_url.split("/")[-1]
        file_path = UPLOAD_DIR / filename
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        # Log error but don't fail
        print(f"Error deleting image {image_url}: {e}")