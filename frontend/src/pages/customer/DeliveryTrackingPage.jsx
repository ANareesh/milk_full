/**
 * Customer Delivery Tracking Page
 */

import React, { useState, useEffect } from 'react';
import { locationAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';
import { MapPin, Phone, Clock, Truck, AlertCircle } from 'lucide-react';

export function DeliveryTrackingPage() {
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const loadDeliveryTracking = async () => {
    try {
      const response = await locationAPI.getCustomerDeliveryTracking();
      if (response.data && response.data.data) {
        setTracking(response.data.data);
      }
    } catch (error) {
      console.error('Error loading delivery tracking:', error);
      toast.error('Failed to load delivery tracking');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDeliveryTracking();

    if (autoRefresh) {
      const intervalId = setInterval(() => {
        loadDeliveryTracking();
      }, 5000); // Refresh every 5 seconds

      return () => clearInterval(intervalId);
    }
  }, [autoRefresh]);

  if (loading) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Loading delivery tracking...</p>
          </div>
        </div>
      </CustomerLayout>
    );
  }

  if (!tracking || !tracking.has_active_delivery) {
    return (
      <CustomerLayout>
        <div className="space-y-6">
          <h1 className="text-3xl font-bold text-gray-800">Delivery Tracking</h1>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <AlertCircle className="mx-auto text-blue-600 mb-2" size={48} />
            <p className="text-lg font-semibold text-blue-900">No Active Delivery</p>
            <p className="text-blue-700 mt-2">You don't have any active deliveries right now.</p>
          </div>
        </div>
      </CustomerLayout>
    );
  }

  const delivery = tracking.delivery_marker;

  return (
    <CustomerLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Track Your Delivery</h1>
          <button
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={`px-4 py-2 rounded-lg font-medium transition ${
              autoRefresh
                ? 'bg-blue-600 text-white hover:bg-blue-700'
                : 'bg-gray-300 text-gray-700'
            }`}
          >
            {autoRefresh ? '🔄 Live Tracking' : '⏸ Paused'}
          </button>
        </div>

        {/* Status Card */}
        <div className={`rounded-lg shadow-lg p-6 ${
          delivery.status === 'delivered' ? 'bg-green-50 border border-green-200' :
          delivery.status === 'in_progress' ? 'bg-blue-50 border border-blue-200' :
          'bg-amber-50 border border-amber-200'
        }`}>
          <div className="flex items-start gap-4">
            <div className={`p-3 rounded-full ${
              delivery.status === 'delivered' ? 'bg-green-200' :
              delivery.status === 'in_progress' ? 'bg-blue-200' :
              'bg-amber-200'
            }`}>
              <Truck size={32} className={
                delivery.status === 'delivered' ? 'text-green-700' :
                delivery.status === 'in_progress' ? 'text-blue-700' :
                'text-amber-700'
              } />
            </div>
            <div>
              <p className={`text-sm font-semibold ${
                delivery.status === 'delivered' ? 'text-green-700' :
                delivery.status === 'in_progress' ? 'text-blue-700' :
                'text-amber-700'
              }`}>
                {tracking.status_message}
              </p>
              <p className="text-lg font-bold mt-1">
                {delivery.agent_name}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                Distance Remaining: {delivery.distance_remaining_km.toFixed(1)} km
              </p>
            </div>
          </div>
        </div>

        {/* Agent Info */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Agent Information</h3>
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <MapPin size={20} className="text-blue-600" />
                <div>
                  <p className="text-sm text-gray-600">Name</p>
                  <p className="font-semibold">{delivery.agent_name}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Phone size={20} className="text-green-600" />
                <div>
                  <p className="text-sm text-gray-600">Contact</p>
                  <p className="font-semibold">{delivery.agent_phone}</p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Clock size={20} className="text-orange-600" />
                <div>
                  <p className="text-sm text-gray-600">Est. Arrival</p>
                  <p className="font-semibold">
                    {delivery.estimated_arrival
                      ? new Date(delivery.estimated_arrival).toLocaleTimeString()
                      : 'Calculating...'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-bold mb-4">Order Details</h3>
            <div className="space-y-3">
              <div>
                <p className="text-sm text-gray-600">Order ID</p>
                <p className="font-semibold">#{delivery.order_id}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className={`font-semibold px-3 py-1 rounded inline-block ${
                  delivery.status === 'delivered' ? 'bg-green-100 text-green-800' :
                  delivery.status === 'in_progress' ? 'bg-blue-100 text-blue-800' :
                  'bg-amber-100 text-amber-800'
                }`}>
                  {delivery.status.charAt(0).toUpperCase() + delivery.status.slice(1)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Last Updated</p>
                <p className="font-semibold text-sm">
                  {new Date(delivery.last_updated).toLocaleTimeString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Map Container */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="w-full h-auto bg-gradient-to-br from-blue-100 to-blue-50 flex flex-col items-center justify-center p-12">
            <MapPin size={64} className="text-blue-400 mb-4" />
            <p className="text-xl font-semibold text-gray-700">Live Delivery Map</p>
            <p className="text-gray-600 mt-2">Set REACT_APP_GOOGLE_MAPS_API_KEY environment variable to see agent location on map</p>
            <p className="text-sm text-gray-500 mt-4">Add to .env.local: REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key</p>
          </div>
        </div>

        {/* Help Section */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="font-bold mb-3">Need Help?</h3>
          <p className="text-gray-700">
            If you don't see your delivery tracking, make sure you have an active order in progress. 
            This page updates automatically every 5 seconds when live tracking is enabled.
          </p>
        </div>
      </div>
    </CustomerLayout>
  );
}