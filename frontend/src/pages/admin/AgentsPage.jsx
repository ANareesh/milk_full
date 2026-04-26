/**
 * Admin Agents Management Page
 */

import React, { useState, useEffect } from 'react';
import { agentAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AdminLayout } from '../../components/AdminLayout';

export function AdminAgentsPage() {
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [availableAgents, setAvailableAgents] = useState([]);
  const [showAvailable, setShowAvailable] = useState(false);

  useEffect(() => {
    loadAgents();
  }, []);

  const loadAgents = async () => {
    try {
      setLoading(true);
      const response = await agentAPI.getAll();
      setAgents(response.data);
    } catch (error) {
      toast.error('Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const loadAvailableAgents = async () => {
    try {
      const response = await agentAPI.getAvailable();
      setAvailableAgents(response.data);
      setShowAvailable(true);
    } catch (error) {
      toast.error('Failed to load available agents');
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64">Loading...</div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Agents Management</h1>
          <button
            onClick={loadAvailableAgents}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
          >
            View Available Agents
          </button>
        </div>

        {showAvailable && availableAgents.length > 0 && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-6">
            <h2 className="text-lg font-bold text-green-800 mb-4">Available Agents</h2>
            <div className="space-y-2">
              {availableAgents.map((agent) => (
                <div key={agent.id} className="flex justify-between items-center p-3 bg-white rounded">
                  <span className="font-medium">Agent #{agent.user_id}</span>
                  <span className="text-sm text-gray-600">
                    Completed: {agent.total_deliveries || 0} deliveries
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {agents.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No agents yet</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {agents.map((agent) => (
              <div key={agent.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-lg font-semibold">Agent #{agent.user_id}</h3>
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${agent.status === 'available' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}`}>
                    {agent.status}
                  </span>
                </div>

                <div className="space-y-3">
                  <div>
                    <p className="text-gray-600 text-sm">Total Deliveries</p>
                    <p className="text-2xl font-bold text-blue-600">{agent.total_deliveries || 0}</p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm">Total Earnings</p>
                    <p className="text-2xl font-bold text-green-600">₹{agent.total_earnings?.toFixed(2) || '0.00'}</p>
                  </div>

                  <div>
                    <p className="text-gray-600 text-sm">Rating</p>
                    <p className="text-xl font-semibold text-orange-600">
                      {agent.rating?.toFixed(1) || 'N/A'} ⭐
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </AdminLayout>
  );
}
