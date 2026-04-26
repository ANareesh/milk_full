/**
 * Admin Agent Map View - Real-time all agents on map
 */

import React, { useState, useEffect, useCallback } from 'react';
import { locationAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AdminLayout } from '../../components/AdminLayout';
import { MapPin, Users, Truck, Clock, Navigation } from 'lucide-react';

const mapContainerStyle = {
  width: '100%',
  height: '600px',
  borderRadius: '0.5rem'
};

export function AdminAgentMapPage() {
  const [agents, setAgents] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);
  const [refreshInterval, setRefreshInterval] = useState(5); // seconds

  const loadAgentsMap = useCallback(async () => {
    try {
      const response = await locationAPI.getAdminAgentsMap();
      if (response.data && response.data.data) {
        setAgents(response.data.data.agent_markers || []);
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Error loading agents map:', error);
      toast.error('Failed to load agents map');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadAgentsMap();

    if (autoRefresh) {
      const intervalId = setInterval(() => {
        loadAgentsMap();
      }, refreshInterval * 1000);

      return () => clearInterval(intervalId);
    }
  }, [autoRefresh, refreshInterval, loadAgentsMap]);

  const getAgentColor = (agent) => {
    if (agent.current_deliveries_count > 0) return 'bg-red-500'; // Red - busy
    if (agent.status === 'on_break') return 'bg-amber-500'; // Amber - break
    return 'bg-green-500'; // Green - available
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-96">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p>Loading map...</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Agents Real-time Map</h1>
          <div className="flex gap-2">
            <button
              onClick={() => setAutoRefresh(!autoRefresh)}
              className={`px-4 py-2 rounded-lg font-medium transition ${
                autoRefresh
                  ? 'bg-blue-600 text-white hover:bg-blue-700'
                  : 'bg-gray-300 text-gray-700 hover:bg-gray-400'
              }`}
            >
              {autoRefresh ? '🔄 Auto-refreshing' : '⏸ Paused'}
            </button>
            <select
              value={refreshInterval}
              onChange={(e) => setRefreshInterval(Number(e.target.value))}
              className="px-3 py-2 border border-gray-300 rounded-lg"
              disabled={!autoRefresh}
            >
              <option value={3}>Every 3s</option>
              <option value={5}>Every 5s</option>
              <option value={10}>Every 10s</option>
              <option value={30}>Every 30s</option>
            </select>
            <button
              onClick={loadAgentsMap}
              className="px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700"
            >
              🔄 Refresh Now
            </button>
          </div>
        </div>

        {/* Statistics Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-green-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Agents Online</p>
                  <p className="text-3xl font-bold text-green-600">{stats.agents_online}/{stats.total_agents}</p>
                </div>
                <Users className="text-green-600" size={32} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-red-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">In Delivery</p>
                  <p className="text-3xl font-bold text-red-600">{stats.agents_in_delivery}</p>
                </div>
                <Truck className="text-red-600" size={32} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-blue-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Distance Today</p>
                  <p className="text-3xl font-bold text-blue-600">{stats.total_distance_covered_today_km} km</p>
                </div>
                <Navigation className="text-blue-600" size={32} />
              </div>
            </div>
            <div className="bg-white rounded-lg shadow p-4 border-l-4 border-purple-600">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-gray-600 text-sm">Avg Delivery Time</p>
                  <p className="text-3xl font-bold text-purple-600">{stats.average_delivery_time_minutes}m</p>
                </div>
                <Clock className="text-purple-600" size={32} />
              </div>
            </div>
          </div>
        )}

        {/* Map Container */}
        <div className="bg-white rounded-lg shadow-lg overflow-hidden">
          <div className="w-full h-auto bg-gradient-to-br from-blue-100 to-blue-50 flex flex-col items-center justify-center p-12">
            <MapPin size={64} className="text-blue-400 mb-4" />
            <p className="text-xl font-semibold text-gray-700">Interactive Map Loading</p>
            <p className="text-gray-600 mt-2">Set REACT_APP_GOOGLE_MAPS_API_KEY environment variable to enable maps</p>
            <p className="text-sm text-gray-500 mt-4">Add to .env.local: REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key</p>
          </div>
        </div>

        {/* Legend */}
        <div className="bg-white rounded-lg shadow p-4">
          <h3 className="font-bold text-lg mb-4">Map Legend</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-green-500 rounded-full border-2 border-white"></div>
              <span>Available for Delivery</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-red-500 rounded-full border-2 border-white"></div>
              <span>In Active Delivery</span>
            </div>
            <div className="flex items-center gap-3">
              <div className="w-6 h-6 bg-amber-500 rounded-full border-2 border-white"></div>
              <span>On Break</span>
            </div>
          </div>
        </div>

        {/* Agents List */}
        <div className="bg-white rounded-lg shadow overflow-x-auto">
          <table className="min-w-full">
            <thead className="bg-gray-100">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold">Agent</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Deliveries</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Speed</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Earnings</th>
                <th className="px-6 py-3 text-left text-sm font-semibold">Last Updated</th>
              </tr>
            </thead>
            <tbody className="divide-y">
              {agents.map((agent) => (
                <tr key={agent.agent_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div>
                      <p className="font-semibold">{agent.agent_name}</p>
                      <p className="text-xs text-gray-500">{agent.assigned_area}</p>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      agent.current_deliveries_count > 0 ? 'bg-red-100 text-red-800' :
                      agent.status === 'on_break' ? 'bg-amber-100 text-amber-800' :
                      'bg-green-100 text-green-800'
                    }`}>
                      {agent.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-semibold">{agent.current_deliveries_count}</td>
                  <td className="px-6 py-4">{agent.speed ? `${agent.speed.toFixed(1)} km/h` : '-'}</td>
                  <td className="px-6 py-4 font-semibold text-green-600">₹{agent.total_earnings.toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm text-gray-600">
                    {new Date(agent.last_updated).toLocaleTimeString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AdminLayout>
  );
}