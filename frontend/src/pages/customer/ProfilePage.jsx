/**
 * Customer Profile Page
 */

import React, { useState, useEffect } from 'react';
import { customerAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';

export function CustomerProfilePage() {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({});

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await customerAPI.getProfile();
      setProfile(response.data);
      setFormData(response.data);
    } catch (error) {
      toast.error('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSave = async () => {
    try {
      await customerAPI.updateProfile(formData);
      toast.success('Profile updated successfully');
      setIsEditing(false);
      loadProfile();
    } catch (error) {
      toast.error('Failed to update profile');
    }
  };

  if (loading) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Loading...</div>
      </CustomerLayout>
    );
  }

  if (!profile) {
    return (
      <CustomerLayout>
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700">Failed to load profile</p>
        </div>
      </CustomerLayout>
    );
  }

  return (
    <CustomerLayout>
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-800 mb-6">My Profile</h1>

        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
              {isEditing ? (
                <input
                  type="text"
                  name="address"
                  value={formData.address || ''}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              ) : (
                <p className="text-gray-900">{profile.address || '-'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">City</label>
              {isEditing ? (
                <input
                  type="text"
                  name="city"
                  value={formData.city || ''}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              ) : (
                <p className="text-gray-900">{profile.city || '-'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Postal Code</label>
              {isEditing ? (
                <input
                  type="text"
                  name="postal_code"
                  value={formData.postal_code || ''}
                  onChange={handleChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              ) : (
                <p className="text-gray-900">{profile.postal_code || '-'}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Preferred Delivery Time
              </label>
              {isEditing ? (
                <input
                  type="text"
                  name="preferred_delivery_time"
                  value={formData.preferred_delivery_time || ''}
                  onChange={handleChange}
                  placeholder="e.g., morning, evening"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              ) : (
                <p className="text-gray-900">{profile.preferred_delivery_time || '-'}</p>
              )}
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-blue-700">
              <strong>Outstanding Balance:</strong> ₹{profile.total_amount_due?.toFixed(2) || '0.00'}
            </p>
          </div>

          <div className="flex gap-2 pt-6">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
              >
                Edit Profile
              </button>
            ) : (
              <>
                <button
                  onClick={handleSave}
                  className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                >
                  Save Changes
                </button>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setFormData(profile);
                  }}
                  className="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </>
            )}
          </div>
        </div>
      </div>
    </CustomerLayout>
  );
}
