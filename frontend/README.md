/**
 * Frontend README with Setup Instructions
 */

# ASN Dairy Farm - Frontend

React.js + Tailwind CSS web application for the milk delivery management system.

## Features

### Customer Features
- Browse all milk products with search and filtering
- Place orders with delivery date selection
- Track orders in real-time
- View order history and payment status
- Manage profile and payment methods
- View outstanding balance

### Agent Features
- View assigned deliveries
- Start and complete deliveries
- Verify customer OTP for delivery completion
- Track earnings and performance
- View profile and rating

### Admin Features
- Dashboard with key metrics
- Manage products (CRUD)
- View all orders with filtering
- Manage customers and track pending balances
- Manage agents and assign deliveries
- View revenue and delivery reports

## Tech Stack

- **Framework**: React 18.2.0
- **Styling**: Tailwind CSS 3.3.0
- **Routing**: React Router v6
- **HTTP Client**: Axios with interceptors
- **State Management**: React Context API
- **Notifications**: React Hot Toast
- **Charts**: Recharts
- **Build Tool**: Vite

## Project Structure

```
frontend/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ProtectedRoute.jsx
│   │   ├── CustomerLayout.jsx
│   │   ├── AgentLayout.jsx
│   │   └── AdminLayout.jsx
│   ├── pages/               # Page components
│   │   ├── LoginPage.jsx
│   │   ├── RegisterPage.jsx
│   │   ├── customer/
│   │   │   ├── ProductsPage.jsx
│   │   │   ├── OrdersPage.jsx
│   │   │   ├── PaymentsPage.jsx
│   │   │   └── ProfilePage.jsx
│   │   ├── agent/
│   │   │   ├── DeliveriesPage.jsx
│   │   │   └── ProfilePage.jsx
│   │   └── admin/
│   │       ├── DashboardPage.jsx
│   │       ├── ProductsPage.jsx
│   │       ├── OrdersPage.jsx
│   │       ├── CustomersPage.jsx
│   │       └── AgentsPage.jsx
│   ├── services/
│   │   └── api.js              # Centralized API service with interceptors
│   ├── context/
│   │   └── AuthContext.jsx     # Global authentication state
│   ├── utils/
│   │   ├── date.js             # Date formatting utilities
│   │   └── storage.js          # Local storage management
│   ├── styles/
│   │   └── index.css           # Global styles and utilities
│   ├── App.jsx                  # Main app component and routing
│   └── index.jsx                # Entry point
├── index.html                   # HTML template
├── vite.config.js              # Vite configuration
├── tailwind.config.js          # Tailwind CSS configuration
├── postcss.config.js           # PostCSS configuration
├── package.json                 # Dependencies and scripts
└── README.md                    # This file
```

## Installation

### Prerequisites
- Node.js >= 16
- npm or yarn

### Setup Steps

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env.local
   ```
   
   Configure in `.env.local`:
   ```
   VITE_API_URL=http://localhost:8000
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```
   
   The application will be available at `http://localhost:3000`

## Development Workflow

### Running the Application

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

### Key Workflows

**Customer Workflow**:
1. Register as customer
2. Browse products with search/filter
3. Place orders with delivery date
4. Track orders in real-time
5. Make payments (UPI, Card, Cash)
6. View payment history

**Agent Workflow**:
1. Register as agent
2. View assigned deliveries
3. Start delivery and navigate to location
4. Complete delivery by verifying customer OTP
5. Track earnings and performance

**Admin Workflow**:
1. Login as admin
2. View dashboard metrics
3. Manage products (add, edit, delete)
4. Monitor all orders
5. Track customer balances
6. Monitor agent performance
7. Generate reports

## API Integration

All API calls are handled through the centralized `api.js` service:

```javascript
import { productAPI, orderAPI, paymentAPI } from '../services/api';

// Example: Get all products
const products = await productAPI.list();

// Example: Create order
await orderAPI.create({ product_id, quantity, delivery_date });

// Example: Make payment
await paymentAPI.createUPI({ amount, upi_id });
```

### Available API Groups
- `authAPI` - Authentication endpoints
- `productAPI` - Product management
- `orderAPI` - Order management
- `deliveryAPI` - Delivery tracking
- `paymentAPI` - Payment processing
- `customerAPI` - Customer profile
- `agentAPI` - Agent profile
- `subscriptionAPI` - Subscriptions
- `reviewAPI` - Reviews and ratings
- `adminAPI` - Admin reports and management

## Authentication

Uses JWT-based authentication with context API:

```javascript
import { useAuth } from '../context/AuthContext';

function MyComponent() {
  const { user, role, login, logout, register } = useAuth();
  
  return <div>Welcome {user?.username}</div>;
}
```

## Styling

### Tailwind CSS Configuration

Custom color palette configured in `tailwind.config.js`:
- **Primary**: Green (#22c55e) - Fresh dairy feel
- **Secondary**: Light Blue (#3b82f6)
- **Accent**: Orange (#f97316)

### Utility Classes

Custom utility classes available:
- `.btn-primary` - Green primary button
- `.btn-secondary` - Gray secondary button
- `.btn-danger` - Red danger button
- `.card` - Standard card styling
- `.card-lg` - Large card with shadow
- `.input-field` - Styled input with focus states
- `.form-label` - Label styling

## Component Structure

### Layout Components
- **CustomerLayout** - Navigation and layout for customer pages
- **AgentLayout** - Navigation and layout for agent pages
- **AdminLayout** - Navigation and layout for admin pages

### Protected Routes
Routes are protected using `ProtectedRoute` component that validates:
- User is authenticated
- User has required role (customer, agent, admin)
- Redirects to login if not authenticated

## Production Deployment

### Build Steps

```bash
# Build for production
npm run build

# Output in dist/ directory
```

### Deployment Options

**Vercel** (Recommended)
```bash
npm install -g vercel
vercel
```

**Netlify**
```bash
npm run build
# Deploy dist/ folder to Netlify
```

**Docker**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "run", "preview"]
```

### Environment Variables for Production

```
VITE_API_URL=https://api.asndairyfarm.com
```

## Performance Optimizations

- Code splitting with React Router
- Lazy loading of images
- Minified CSS and JavaScript
- Gzip compression
- CDN delivery
- Caching strategies in service workers

## Browser Support

- Chrome/Edge >= 90
- Firefox >= 88
- Safari >= 14
- Modern mobile browsers

## Troubleshooting

### API Connection Issues
- Ensure backend is running on `http://localhost:8000`
- Check CORS configuration if deployed separately
- Verify JWT tokens are being sent correctly

### Authentication Issues
- Clear localStorage: `localStorage.clear()`
- Check token expiration in browser console
- Verify refresh token logic in AuthContext

### Build Errors
- Delete `node_modules` and run `npm install`
- Clear Vite cache: `rm -rf node_modules/.vite`
- Check Node version: `node --version` (>= 16)

## Contributing

1. Create feature branch: `git checkout -b feature/name`
2. Commit changes: `git commit -m "Add feature"`
3. Push to branch: `git push origin feature/name`
4. Create Pull Request

## License

Proprietary - ASN Dairy Farm

## Support

For issues and support, contact: support@asndairyfarm.com
