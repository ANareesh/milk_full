/**
 * Main App Component
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';

// Customer Pages
import { CustomerProductsPage } from './pages/customer/ProductsPage';
import { CustomerOrdersPage } from './pages/customer/OrdersPage';
import { CustomerProfilePage } from './pages/customer/ProfilePage';
import { CustomerPaymentsPage } from './pages/customer/PaymentsPage';
import { SubscribeProductsPage } from './pages/customer/SubscribeProductsPage';
import { SubscriptionsPage } from './pages/customer/SubscriptionsPage';
import { DeliveryTrackingPage } from './pages/customer/DeliveryTrackingPage';

// Agent Pages
import { AgentDeliveriesPage } from './pages/agent/DeliveriesPage';
import { AgentProfilePage } from './pages/agent/ProfilePage';
import { GPSTrackingPage } from './pages/agent/GPSTrackingPage';

// Admin Pages
import { AdminDashboardPage } from './pages/admin/DashboardPage';
import { AdminProductsPage } from './pages/admin/ProductsPage';
import { AdminOrdersPage } from './pages/admin/OrdersPage';
import { AdminAgentsPage } from './pages/admin/AgentsPage';
import { AdminCustomersPage } from './pages/admin/CustomersPage';
import { AdminDeliveriesPage } from './pages/admin/DeliveriesPage';
import { AdminAgentMapPage } from './pages/admin/AgentMapPage';
import { ProductDetailPage } from './pages/customer/ProductDetailPage';

function AppRoutes() {
  const { role } = useAuth();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route path="/forgot-password" element={<ForgotPasswordPage />} />
      <Route path="/reset-password" element={<ResetPasswordPage />} />

      {/* Customer routes */}
      <Route
        path="/customer/products"
        element={
          <ProtectedRoute requiredRole="customer">
            <CustomerProductsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/customer/orders"
        element={
          <ProtectedRoute requiredRole="customer">
            <CustomerOrdersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/customer/profile"
        element={
          <ProtectedRoute requiredRole="customer">
            <CustomerProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/customer/payments"
        element={
          <ProtectedRoute requiredRole="customer">
            <CustomerPaymentsPage />
          </ProtectedRoute>
        }
      />
      {/* Customer Delivery Tracking */}
      <Route
        path="/customer/delivery-tracking"
        element={
          <ProtectedRoute requiredRole="customer">
            <DeliveryTrackingPage />
          </ProtectedRoute>
        }
      />
      <Route path="/customer/products/:productId" element={<ProtectedRoute><ProductDetailPage /></ProtectedRoute>} />
      {/* Subscription routes */}
      <Route
        path="/subscribe"
        element={
          <ProtectedRoute requiredRole="customer">
            <SubscribeProductsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/subscriptions"
        element={
          <ProtectedRoute requiredRole="customer">
            <SubscriptionsPage />
          </ProtectedRoute>
        }
      />

      {/* Agent routes */}
      <Route
        path="/agent/deliveries"
        element={
          <ProtectedRoute requiredRole="agent">
            <AgentDeliveriesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/agent/profile"
        element={
          <ProtectedRoute requiredRole="agent">
            <AgentProfilePage />
          </ProtectedRoute>
        }
      />
      <Route
          path="/agent/gps-tracking"
          element={
            <ProtectedRoute requiredRole="agent">
              <GPSTrackingPage />
            </ProtectedRoute>
          }
      />

      {/* Admin routes */}
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminDashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/products"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminProductsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/orders"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminOrdersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/agents"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminAgentsPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/customers"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminCustomersPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/deliveries"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminDeliveriesPage />
          </ProtectedRoute>
        }
      />
      {/* Admin Agent Map */}
      <Route
        path="/admin/agents-map"
        element={
          <ProtectedRoute requiredRole="admin">
            <AdminAgentMapPage />
          </ProtectedRoute>
        }
      />

      {/* Default routes */}
      <Route
        path="/"
        element={
          role === 'admin' ? (
            <Navigate to="/admin/dashboard" />
          ) : role === 'agent' ? (
            <Navigate to="/agent/deliveries" />
          ) : role === 'customer' ? (
            <Navigate to="/customer/products" />
          ) : (
            <Navigate to="/login" />
          )
        }
      />
    </Routes>
  );
}

export function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster position="top-right" />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
