/**
 * Agent Profile Page
 */

import React, { useState, useEffect } from 'react';
import { agentAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AgentLayout } from '../../components/AgentLayout';

export function AgentProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await agentAPI.getProfile();
      setProfile(response.data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <AgentLayout>
        <div className="flex justify-center items-center h-64">Loading...</div>
      </AgentLayout>
    );
  }

  if (!profile) {
    return (
      <AgentLayout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">Failed to load profile</p>
        </div>
      </AgentLayout>
    );
  }

  return (
    <AgentLayout>
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">Agent Profile</h1>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Total Deliveries</p>
            <p className="text-3xl font-bold text-blue-600">{profile.total_deliveries || 0}</p>
          </div>

          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Total Earnings</p>
            <p className="text-3xl font-bold text-green-600">
              ₹{profile.total_earnings?.toFixed(2) || '0.00'}
            </p>
          </div>

          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Status</p>
            <p className="text-lg font-semibold text-purple-600">
              {profile.status === 'available' ? '✓ Available' : 'Unavailable'}
            </p>
          </div>

          <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Rating</p>
            <p className="text-lg font-semibold text-orange-600">
              {profile.rating?.toFixed(1) || 'N/A'} ⭐
            </p>
          </div>
        </div>

        {profile.current_location && (
          <div className="mt-6 bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-semibold text-gray-800 mb-2">Current Location</h3>
            <p className="text-gray-600">
              Latitude: {profile.current_location.latitude?.toFixed(4) || 'N/A'}<br />
              Longitude: {profile.current_location.longitude?.toFixed(4) || 'N/A'}
            </p>
          </div>
        )}
      </div>
    </AgentLayout>
  );
}
