/**
 * Agent Layout Component with Navigation
 */

import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { MapPin } from 'lucide-react';

export function AgentLayout({ children }) {
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
              <Link 
                to="/agent/deliveries" 
                className="text-gray-700 hover:text-green-600 font-medium transition"
              >
                🚚 Deliveries
              </Link>
              
              <Link 
                to="/agent/gps-tracking" 
                className="text-gray-700 hover:text-green-600 font-medium transition flex items-center gap-2"
              >
                <MapPin className="w-4 h-4" />
                GPS Tracking
              </Link>
              
              <Link 
                to="/agent/profile" 
                className="text-gray-700 hover:text-green-600 font-medium transition"
              >
                👤 Profile
              </Link>

              <div className="flex items-center gap-3 border-l pl-4">
                <span className="text-sm text-gray-600">{user?.username}</span>
                <button
                  onClick={handleLogout}
                  className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm transition"
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