"""Instructions for running the ASN Dairy Farm Backend."""

# ASN Dairy Farm Backend - Setup and Running

## Prerequisites
- Python 3.9+
- PostgreSQL (or SQLite for development)
- pip

## Installation

1. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Setup database:**
   ```bash
   # Copy environment file
   cp .env.example .env
   
   # Update .env with your database credentials
   # For development, you can use SQLite by default
   ```

4. **Run migrations (if using PostgreSQL):**
   ```bash
   alembic upgrade head
   ```

## Running the Application

### Development Server
```bash
python run.py
```

The API will be available at http://localhost:8000

### API Documentation
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Running Tests

### Run all tests
```bash
pytest
```

### Run tests with coverage
```bash
pytest --cov=app
```

### Run specific test file
```bash
pytest tests/api/test_auth.py
```

### Run tests with verbose output
```bash
pytest -v
```

## Environment Variables

Key environment variables (set in .env):
- `DATABASE_URL`: Database connection string
- `SECRET_KEY`: JWT secret key
- `STRIPE_API_KEY`: Stripe API key (for payment integration)
- `REDIS_URL`: Redis connection string

## Project Structure

```
backend/
├── app/
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic validation schemas
│   ├── crud/            # CRUD operations
│   ├── services/        # Business logic
│   ├── api/
│   │   └── v1/
│   │       └── endpoints/   # API endpoints
│   ├── core/            # Core configurations
│   └── utils/           # Utility functions
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
└── run.py              # Entry point
```

## Architecture

The application follows a layered architecture:

1. **API Layer** (`api/v1/endpoints/`) - HTTP endpoints, request/response handling
2. **Service Layer** (`services/`) - Business logic and orchestration
3. **CRUD Layer** (`crud/`) - Database operations
4. **Model Layer** (`models/`) - SQLAlchemy ORM models
5. **Schema Layer** (`schemas/`) - Pydantic validation

## Key Features

### Authentication & Authorization
- JWT-based token authentication
- Role-based access control (Admin, Agent, Customer)
- Password hashing with bcrypt

### Database Models
- User management
- Customer management with location
- Delivery agent management
- Product catalog
- Orders and subscriptions
- Delivery tracking
- Payment processing
- Reviews and ratings

### API Endpoints

**Authentication:**
- POST `/api/v1/auth/register/customer`
- POST `/api/v1/auth/register/agent`
- POST `/api/v1/auth/login`
- POST `/api/v1/auth/refresh`

**Products:**
- GET `/api/v1/products/` - List products
- GET `/api/v1/products/search` - Search products
- POST `/api/v1/products/` - Create product (admin)
- PUT `/api/v1/products/{id}` - Update product (admin)
- DELETE `/api/v1/products/{id}` - Delete product (admin)

**Orders:**
- POST `/api/v1/orders/` - Create order
- GET `/api/v1/orders/my-orders` - Get my orders
- GET `/api/v1/orders/{id}` - Order details
- POST `/api/v1/orders/{id}/cancel` - Cancel order

**Deliveries:**
- POST `/api/v1/deliveries/{id}/assign-agent` - Assign agent
- POST `/api/v1/deliveries/{id}/start` - Start delivery
- POST `/api/v1/deliveries/{id}/complete` - Complete delivery
- GET `/api/v1/deliveries/agent/my-deliveries` - My deliveries

**Payments:**
- POST `/api/v1/payments/upi` - UPI payment
- POST `/api/v1/payments/card` - Card payment
- POST `/api/v1/payments/cash` - Cash payment
- GET `/api/v1/payments/my-payments` - Payment history

**Subscriptions:**
- POST `/api/v1/subscriptions/` - Create subscription
- GET `/api/v1/subscriptions/my-subscriptions` - My subscriptions
- PUT `/api/v1/subscriptions/{id}` - Update subscription
- POST `/api/v1/subscriptions/{id}/pause` - Pause subscription
- POST `/api/v1/subscriptions/{id}/cancel` - Cancel subscription

**Reports:**
- GET `/api/v1/admin/reports/dashboard-stats` - Dashboard stats
- GET `/api/v1/admin/reports/revenue-report` - Revenue report
- GET `/api/v1/admin/reports/delivery-report` - Delivery report

## Performance Optimization

- Database connection pooling
- Efficient pagination
- Query optimization
- Redis caching support
- Async/await for I/O operations

## Database Schema Features

- Proper indexing on frequently queried fields
- Foreign key constraints
- UUID generation for order/payment numbers
- Timestamps with timezone support
- Status enumerations for type safety

## Testing

Comprehensive test suite covering:
- Authentication and authorization
- CRUD operations
- Service layer logic
- API endpoint functionality
- Edge cases and error handling

Run tests: `pytest`

## Error Handling

Proper HTTP status codes and error messages:
- 400 Bad Request - Invalid input
- 401 Unauthorized - Missing/invalid authentication
- 403 Forbidden - Insufficient permissions
- 404 Not Found - Resource not found
- 500 Internal Server Error - Server errors

## Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY` in environment
- [ ] Configure PostgreSQL for production
- [ ] Set up proper logging
- [ ] Configure CORS with actual domain
- [ ] Setup SSL/TLS
- [ ] Run migrations
- [ ] Configure backups
- [ ] Monitor application
- [ ] Setup error tracking (e.g., Sentry)

### Deployment Command
```bash
gunicorn app.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## Support and Documentation

For more information:
- API Docs: http://localhost:8000/docs
- Project specification: See business requirements
