# Complete Setup Guide - ASN Dairy Farm

Quick start guide to run the entire system locally.

## ⚡ 5-Minute Quick Start

### Backend (Terminal 1)

```bash
cd backend
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate

pip install -r requirements.txt
python run.py
```

**Backend running at**: `http://localhost:8000`
**API Docs at**: `http://localhost:8000/docs`

### Frontend (Terminal 2)

```bash
cd frontend
npm install
npm run dev
```

**Frontend running at**: `http://localhost:3000`

---

## 📋 Full Setup Instructions

### Prerequisites

Verify you have these installed:

```bash
# Python
python --version  # Should be 3.9+

# Node.js
node --version    # Should be 16+
npm --version     # Should be 8+

# PostgreSQL (optional, SQLite used by default)
psql --version    # Only if using PostgreSQL
```

---

## 🔧 Backend Setup

### 1. Navigate to Backend

```bash
cd backend
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env file (optional for development)
# Default settings work with SQLite
```

### 5. Initialize Database

Database will be created automatically on first run.

```bash
# Optional: If you want to pre-initialize
python -c "from app.core.database import init_db; init_db()"
```

### 6. Run Backend Server

```bash
python run.py
```

**Output should show**:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

### 7. Verify Backend

- Open `http://localhost:8000/docs` in browser
- You should see Swagger UI with all endpoints

---

## 🎨 Frontend Setup

### 1. Navigate to Frontend

```bash
cd frontend
```

### 2. Install Dependencies

```bash
npm install
```

This installs:
- React 18.2.0
- Tailwind CSS 3.3.0
- React Router v6
- Axios
- And more...

### 3. Configure Environment

```bash
# Copy environment template
cp .env.example .env.local

# Edit if needed (usually works as-is)
cat .env.local  # Verify settings
```

### 4. Start Development Server

```bash
npm run dev
```

**Output should show**:
```
  VITE v5.0.0  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  press h + enter to show help
```

### 5. Verify Frontend

- Open `http://localhost:3000` in browser
- You should see the Login page

---

## 🧪 Testing Everything

### 1. Test Backend API

```bash
# In a new terminal (with virtual env activated)
cd backend

# Run tests
pytest tests/ -v

# Expected output: All tests pass with ✓ marks
```

### 2. Test Backend Manually

```bash
# Using curl in terminal:
curl http://localhost:8000/health

# Should return: {"status":"ok"}

# Or visit in browser:
# http://localhost:8000/docs
```

### 3. Test Frontend

With frontend running at `http://localhost:3000`:

1. **Test Registration**
   - Click "Register"
   - Fill customer details
   - Click "Create Account"

2. **Test Login**
   - Enter registered credentials
   - Click "Login"
   - Should redirect to customer dashboard

3. **Test Product Browsing** (Customer)
   - Should see product list
   - Can search products
   - Can view product details

4. **Test Order Creation**
   - Click "Order Now" on a product
   - Fill quantity and delivery date
   - Click "Place Order"

---

## 🚀 Next Steps

### Import Sample Data (Optional)

```bash
cd backend
python -c "
from app.core.database import SessionLocal
from app.models import Product
from sqlalchemy import insert

db = SessionLocal()
products = [
    {'name': 'Whole Milk', 'product_type': 'whole_milk', 'unit_price': 60, 'available_quantity': 100, 'unit': 'L'},
    {'name': 'Toned Milk', 'product_type': 'toned_milk', 'unit_price': 45, 'available_quantity': 150, 'unit': 'L'},
    {'name': 'Skimmed Milk', 'product_type': 'skimmed_milk', 'unit_price': 35, 'available_quantity': 120, 'unit': 'L'},
]
db.execute(insert(Product), products)
db.commit()
print('Sample products created!')
"
```

### Test with Different Roles

1. **Create Customer Account**
   - Register as customer
   - Browse products, place orders

2. **Create Agent Account**
   - Register as agent with code: `AGENT123`
   - View assigned deliveries

3. **Create Admin Account**
   - Use backend admin user (if created)
   - Access admin dashboard

---

## 🛠️ Troubleshooting

### Backend Issues

**"Address already in use" error**
```bash
# Kill process on port 8000
# Windows:
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux:
lsof -i :8000
kill -9 <PID>
```

**Database error**
```bash
# Delete existing database and recreate
cd backend
rm dairy_farm.db  # SQLite
python run.py  # Recreates database
```

**Import error**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend Issues

**Port 3000 already in use**
```bash
npm run dev -- --port 3001
```

**Dependencies not working**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

**Blank page in browser**
```bash
# Clear browser cache (Ctrl+Shift+Delete)
# Check console for errors (F12)
# Verify backend is running
curl http://localhost:8000/health
```

---

## 📁 Project Files Overview

### Backend Key Files

```
backend/
├── run.py                    # Start server here
├── app/main.py              # FastAPI app setup
├── app/core/
│   ├── config.py            # Settings
│   ├── database.py          # DB connection
│   ├── security.py          # JWT auth
│   └── dependencies.py      # Role checks
├── app/models/              # Database models (9 files)
├── app/schemas/             # Validation schemas (9 files)
├── app/crud/                # Database operations (10 files)
├── app/services/            # Business logic (4 files)
└── app/api/v1/endpoints/    # API routes (10 files)
```

### Frontend Key Files

```
frontend/
├── src/
│   ├── App.jsx                    # Main routes
│   ├── api.js                     # API client
│   ├── context/AuthContext.jsx    # Auth state
│   ├── pages/                     # Page components
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── customer/              # Customer pages
│   │   ├── agent/                 # Agent pages
│   │   └── admin/                 # Admin pages
│   └── styles/index.css           # Global styles
├── tailwind.config.js             # Styling config
├── vite.config.js                 # Build config
└── package.json                   # Dependencies
```

---

## 🔐 Default Test Accounts

After running the application, use these to login:

### Sample Credentials for Testing

**Customer Account** (Create via registration):
- Email: customer@example.com
- Password: Password123!
- Role: Customer

**Agent Account** (Create via registration):
- Email: agent@example.com
- Password: Password123!
- Agent Code: AGENT123
- Role: Agent

**Admin Account** (Backend only):
```bash
# Create admin user
cd backend
python -c "
from app.core.database import SessionLocal
from app.models import User
from app.core.security import PasswordUtils

db = SessionLocal()
admin = User(
    username='admin',
    email='admin@example.com',
    hashed_password=PasswordUtils.hash_password('Admin123!'),
    role='admin',
    is_active=True
)
db.add(admin)
db.commit()
print('Admin user created!')
"
```

---

## 📊 API Overview

### Main Endpoints for Testing

```
Authentication
- POST http://localhost:8000/api/v1/auth/register/customer
- POST http://localhost:8000/api/v1/auth/login

Products (Customer)
- GET http://localhost:8000/api/v1/products/
- GET http://localhost:8000/api/v1/products/search?q=milk

Orders (Customer)
- POST http://localhost:8000/api/v1/orders/
- GET http://localhost:8000/api/v1/orders/my-orders

Deliveries (Agent)
- GET http://localhost:8000/api/v1/deliveries/agent/my-deliveries
- POST http://localhost:8000/api/v1/deliveries/{id}/start

Admin
- GET http://localhost:8000/api/v1/admin/dashboard-stats
- GET http://localhost:8000/api/v1/products/admin/all
```

Full API docs: `http://localhost:8000/docs` (when backend is running)

---

## 🚀 Running in Production

### Backend

```bash
# Install production dependencies
pip install gunicorn python-dotenv

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Frontend

```bash
# Build for production
npm run build

# Output in dist/ folder
# Deploy to hosting (Vercel, Netlify, etc.)
```

---

## 📚 Documentation Links

- **Backend README**: [backend/README.md](backend/README.md)
- **Frontend README**: [frontend/README.md](frontend/README.md)
- **Main README**: [README.md](README.md)
- **API Documentation**: http://localhost:8000/docs (when running)

---

## ✅ Verification Checklist

After setup, verify:

- [ ] Backend running at http://localhost:8000
- [ ] Frontend running at http://localhost:3000
- [ ] API docs accessible at http://localhost:8000/docs
- [ ] Can load login page in browser
- [ ] Can register new customer account
- [ ] Can login with created account
- [ ] Can see products on dashboard
- [ ] Backend tests pass: `pytest tests/ -v`

---

## 🆘 Need Help?

Common issues and solutions:

1. **"Cannot find module"** → Run `npm install` or `pip install -r requirements.txt`
2. **Port already in use** → Check processes and kill, or use different port
3. **Database errors** → Delete db file and restart
4. **CORS errors** → Check backend is running, proxy is configured
5. **Blank page** → Check browser console (F12) for errors

---

## 🎉 You're All Set!

The system is now ready for:
- ✅ Development and testing
- ✅ Feature development
- ✅ Integration testing
- ✅ Deployment preparation

Happy coding! 🚀
