"""Main FastAPI application factory."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.api.v1.endpoints import subscriptions
from app.core.config import get_settings
from app.core.database import init_db
from app.api.v1.endpoints import (
    auth, products, orders, deliveries, payments,
    customers, agents, subscriptions, reviews, admin,locations
)
from fastapi.staticfiles import StaticFiles
from pathlib import Path

logger = logging.getLogger(__name__)
settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=settings.project_name,
        version=settings.project_version,
        description="ASN Dairy Farm - Milk Delivery & Management System API",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    # Static files for product images
    static_dir = Path("uploads")
    if not static_dir.exists():
        static_dir.mkdir(parents=True, exist_ok=True)
    
    app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Initialize database
    init_db()
    
    # Health check endpoint
    @app.get("/health", tags=["health"])
    async def health_check():
        """Health check endpoint."""
        return {
            "status": "healthy",
            "service": settings.project_name,
            "version": settings.project_version,
        }
    
    # API v1 routes
    api_prefix = settings.api_v1_str
    
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(products.router, prefix=api_prefix)
    app.include_router(orders.router, prefix=api_prefix)
    app.include_router(deliveries.router, prefix=api_prefix)
    app.include_router(payments.router, prefix=api_prefix)
    app.include_router(customers.router, prefix=api_prefix)
    app.include_router(agents.router, prefix=api_prefix)
    app.include_router(subscriptions.router, prefix=api_prefix)
    app.include_router(reviews.router, prefix=api_prefix)
    app.include_router(admin.router, prefix=api_prefix)
    app.include_router(subscriptions.router, prefix="/api/v1")
    app.include_router(locations.router, prefix=api_prefix)  # ✅ MAKE SURE THIS LINE EXISTS

    
    logger.info(f"FastAPI application '{settings.project_name}' initialized successfully")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
