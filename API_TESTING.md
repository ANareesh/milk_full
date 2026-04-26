# API Testing Guide - cURL Examples

Complete reference for testing all ASN Dairy Farm API endpoints using cURL.

## 📋 Prerequisites

- Backend running at `http://localhost:8000`
- cURL installed (built-in on most systems)

## 🔐 Authentication Flow

### 1. Register Customer Account

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/customer" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_customer",
    "email": "john@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!"
  }'
```

**Response** (Success):
```json
{
  "id": 1,
  "username": "john_customer",
  "email": "john@example.com",
  "role": "customer",
  "is_active": true
}
```

### 2. Register Agent Account

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register/agent" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_agent",
    "email": "agent@example.com",
    "password": "SecurePass123!",
    "confirm_password": "SecurePass123!",
    "agent_code": "AGENT123"
  }'
```

### 3. Login User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_customer",
    "password": "SecurePass123!"
  }'
```

**Response** (Save these tokens!):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Store token for next requests**:
```bash
# Linux/macOS
export TOKEN="your_access_token_here"

# Windows PowerShell
$TOKEN = "your_access_token_here"
```

### 4. Refresh Access Token

```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "your_refresh_token_here"
  }'
```

---

## 📦 Product Endpoints

### Get All Products

```bash
curl -X GET "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN"
```

### Search Products

```bash
curl -X GET "http://localhost:8000/api/v1/products/search?q=whole" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Products by Type

```bash
curl -X GET "http://localhost:8000/api/v1/products/type/whole_milk" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Single Product

```bash
curl -X GET "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Create Product (Admin Only)

```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Full Cream Milk",
    "product_type": "whole_milk",
    "unit": "L",
    "unit_price": 65,
    "available_quantity": 200,
    "description": "Fresh whole milk",
    "fat_percentage": 4.5
  }'
```

### Update Product (Admin Only)

```bash
curl -X PUT "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "unit_price": 70,
    "available_quantity": 150
  }'
```

### Delete Product (Admin Only)

```bash
curl -X DELETE "http://localhost:8000/api/v1/products/1" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 🛒 Order Endpoints

### Create Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2.5,
    "delivery_date": "2024-12-25T10:00:00"
  }'
```

### Get My Orders

```bash
curl -X GET "http://localhost:8000/api/v1/orders/my-orders" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Single Order

```bash
curl -X GET "http://localhost:8000/api/v1/orders/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Confirm Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/confirm" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Cancel Order

```bash
curl -X POST "http://localhost:8000/api/v1/orders/1/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

### Get All Orders (Admin)

```bash
curl -X GET "http://localhost:8000/api/v1/orders/admin/all" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 💳 Payment Endpoints

### Create UPI Payment

```bash
curl -X POST "http://localhost:8000/api/v1/payments/upi" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 162.50,
    "upi_id": "user@upi"
  }'
```

### Create Card Payment

```bash
curl -X POST "http://localhost:8000/api/v1/payments/card" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 162.50,
    "card_number": "4111111111111111",
    "card_holder": "John Doe",
    "expiry": "12/25",
    "cvv": "123"
  }'
```

### Create Cash Payment

```bash
curl -X POST "http://localhost:8000/api/v1/payments/cash" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "order_id": 1,
    "amount": 162.50
  }'
```

### Get My Payments

```bash
curl -X GET "http://localhost:8000/api/v1/payments/my-payments" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Single Payment

```bash
curl -X GET "http://localhost:8000/api/v1/payments/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Refund Payment (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/payments/1/refund" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer requested refund"
  }'
```

---

## 🚚 Delivery Endpoints

### Get My Deliveries (Agent)

```bash
curl -X GET "http://localhost:8000/api/v1/deliveries/agent/my-deliveries" \
  -H "Authorization: Bearer $AGENT_TOKEN"
```

### Assign Agent to Delivery (Admin)

```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/1/assign-agent" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_id": 1
  }'
```

### Start Delivery (Agent)

```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/1/start" \
  -H "Authorization: Bearer $AGENT_TOKEN"
```

### Generate Delivery OTP (Customer - internal)

```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/1/generate-otp" \
  -H "Authorization: Bearer $TOKEN"
```

### Verify OTP and Complete Delivery (Agent)

```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/1/verify-otp" \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "otp": "123456"
  }'
```

### Mark Delivery as Failed (Agent)

```bash
curl -X POST "http://localhost:8000/api/v1/deliveries/1/fail" \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "reason": "Customer not available"
  }'
```

---

## 👤 Customer Endpoints

### Get Customer Profile

```bash
curl -X GET "http://localhost:8000/api/v1/customers/profile" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Customer Profile

```bash
curl -X PUT "http://localhost:8000/api/v1/customers/profile" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "address": "123 Main St",
    "city": "Mumbai",
    "postal_code": "400001",
    "preferred_delivery_time": "morning"
  }'
```

### Get Active Subscriptions

```bash
curl -X GET "http://localhost:8000/api/v1/customers/subscriptions/active" \
  -H "Authorization: Bearer $TOKEN"
```

### Get All Customers (Admin)

```bash
curl -X GET "http://localhost:8000/api/v1/customers/admin/all" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Customers with Pending Balance (Admin)

```bash
curl -X GET "http://localhost:8000/api/v1/customers/admin/pending-balance" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 🚚 Agent Endpoints

### Get Agent Profile

```bash
curl -X GET "http://localhost:8000/api/v1/agents/profile" \
  -H "Authorization: Bearer $AGENT_TOKEN"
```

### Update Agent Location

```bash
curl -X POST "http://localhost:8000/api/v1/agents/location" \
  -H "Authorization: Bearer $AGENT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "latitude": 19.0760,
    "longitude": 72.8777
  }'
```

### Get All Agents (Admin)

```bash
curl -X GET "http://localhost:8000/api/v1/agents/admin/all" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Available Agents (Admin)

```bash
curl -X GET "http://localhost:8000/api/v1/agents/admin/available" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## ⭐ Review Endpoints

### Create Review

```bash
curl -X POST "http://localhost:8000/api/v1/reviews/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "rating": 4,
    "comment": "Great quality milk!"
  }'
```

### Get Reviews for Product

```bash
curl -X GET "http://localhost:8000/api/v1/reviews/product/1" \
  -H "Authorization: Bearer $TOKEN"
```

### Get Product Rating

```bash
curl -X GET "http://localhost:8000/api/v1/reviews/product/1/rating" \
  -H "Authorization: Bearer $TOKEN"
```

### Get My Reviews

```bash
curl -X GET "http://localhost:8000/api/v1/reviews/my-reviews" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Review

```bash
curl -X PUT "http://localhost:8000/api/v1/reviews/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "rating": 5,
    "comment": "Excellent quality!"
  }'
```

### Delete Review

```bash
curl -X DELETE "http://localhost:8000/api/v1/reviews/1" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 📊 Admin Endpoints

### Get Dashboard Statistics

```bash
curl -X GET "http://localhost:8000/api/v1/admin/reports/dashboard-stats" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Revenue Report

```bash
curl -X GET "http://localhost:8000/api/v1/admin/reports/revenue-report" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Delivery Report

```bash
curl -X GET "http://localhost:8000/api/v1/admin/reports/delivery-report" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Product Report

```bash
curl -X GET "http://localhost:8000/api/v1/admin/reports/product-report" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

### Get Customer Report

```bash
curl -X GET "http://localhost:8000/api/v1/admin/reports/customer-report" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

---

## 📋 Subscription Endpoints

### Create Subscription

```bash
curl -X POST "http://localhost:8000/api/v1/subscriptions/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "frequency": "daily",
    "start_date": "2024-12-20T08:00:00"
  }'
```

### Get My Subscriptions

```bash
curl -X GET "http://localhost:8000/api/v1/subscriptions/my-subscriptions" \
  -H "Authorization: Bearer $TOKEN"
```

### Update Subscription

```bash
curl -X PUT "http://localhost:8000/api/v1/subscriptions/1" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "quantity": 3
  }'
```

### Pause Subscription

```bash
curl -X POST "http://localhost:8000/api/v1/subscriptions/1/pause" \
  -H "Authorization: Bearer $TOKEN"
```

### Resume Subscription

```bash
curl -X POST "http://localhost:8000/api/v1/subscriptions/1/resume" \
  -H "Authorization: Bearer $TOKEN"
```

### Cancel Subscription

```bash
curl -X POST "http://localhost:8000/api/v1/subscriptions/1/cancel" \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🧪 Testing Workflow

### Complete Workflow Example

```bash
#!/bin/bash

# 1. Register
REGISTER=$(curl -s -X POST "http://localhost:8000/api/v1/auth/register/customer" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!",
    "confirm_password": "Test123!"
  }')

echo "Registered: $REGISTER"

# 2. Login
LOGIN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!"
  }')

TOKEN=$(echo $LOGIN | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: $TOKEN"

# 3. Browse products
PRODUCTS=$(curl -s -X GET "http://localhost:8000/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN")
echo "Products: $PRODUCTS"

# 4. Create order
ORDER=$(curl -s -X POST "http://localhost:8000/api/v1/orders/" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_id": 1,
    "quantity": 2,
    "delivery_date": "2024-12-25T10:00:00"
  }')
echo "Order created: $ORDER"
```

---

## 🔍 Tips & Tricks

### Pretty Print JSON Response
```bash
curl -s ... | jq '.'
```

### Extract Values from Response
```bash
curl -s ... | jq '.access_token'
```

### Save Bearer Token
```bash
export TOKEN=$(curl -s ... | jq -r '.access_token')
```

### View Response Headers
```bash
curl -i ...
```

### Verbose Output (Debug)
```bash
curl -v ...
```

---

## ✅ Common Status Codes

- **200** - Success
- **201** - Created
- **400** - Bad Request (invalid data)
- **401** - Unauthorized (missing/invalid token)
- **403** - Forbidden (insufficient permissions)
- **404** - Not Found
- **500** - Server Error

---

## 🚀 Production API

Replace `http://localhost:8000` with your production API endpoint:

```bash
export API_URL="https://api.asndairyfarm.com"

curl -X GET "$API_URL/api/v1/products/" \
  -H "Authorization: Bearer $TOKEN"
```

---

**Happy testing! 🎉**
