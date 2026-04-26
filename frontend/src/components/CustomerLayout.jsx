/**
 * Customer Layout Component with Navigation
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Map } from 'lucide-react';

export function CustomerLayout({ children }) {
  const navigate = useNavigate();
  const { logout, user } = useAuth();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-md">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <Link to="/" className="text-2xl font-bold text-green-600">
              ASN Dairy Farm
            </Link>

            <div className="flex items-center gap-6">
              <Link to="/customer/products" className="text-gray-700 hover:text-green-600 font-medium">
                Products
              </Link>
              <Link to="/customer/orders" className="text-gray-700 hover:text-green-600 font-medium">
                Orders
              </Link>
              <Link to="/customer/payments" className="text-gray-700 hover:text-green-600 font-medium">
                Payments
              </Link>
              <Link to="/customer/profile" className="text-gray-700 hover:text-green-600 font-medium">
                Profile
              </Link>
              <Link to="/subscriptions">My Subscriptions</Link>
              <Link to="/subscribe">Subscribe to Products</Link>
              <Link
                to="/customer/delivery-tracking"
                className="block px-4 py-2 text-gray-700 hover:bg-gray-100 transition"
              >
                <div className="flex items-center gap-2">
                  <Map className="w-4 h-4" />
                  Track Delivery
                </div>
              </Link>
              <div className="flex items-center gap-3 border-l pl-4">
                <span className="text-sm text-gray-600">{user?.username}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>
    </div>
  );
}
