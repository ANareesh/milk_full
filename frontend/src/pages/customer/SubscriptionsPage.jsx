import React, { useState, useEffect } from 'react';
import { subscriptionAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';
import { formatDate } from '../../utils/date';

export function SubscriptionsPage() {
  const [subscriptions, setSubscriptions] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);
  const [activeFilter, setActiveFilter] = useState('all');
  const [showPauseModal, setShowPauseModal] = useState(false);
  const [selectedSub, setSelectedSub] = useState(null);
  const [pauseData, setPauseData] = useState({ pause_reason: '', pause_days: 7 });

  useEffect(() => {
    loadSubscriptions();
    loadStats();
  }, []);

  const loadSubscriptions = async () => {
    try {
      setLoading(true);
      const response = await subscriptionAPI.getMySubscriptions();
      setSubscriptions(response.data.subscriptions);
    } catch (error) {
      toast.error('Failed to load subscriptions');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await subscriptionAPI.getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats', error);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return 'bg-green-100 text-green-800';
      case 'paused':
        return 'bg-yellow-100 text-yellow-800';
      case 'cancelled':
        return 'bg-red-100 text-red-800';
      case 'expired':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handlePause = async () => {
    try {
      await subscriptionAPI.pause(selectedSub.id, pauseData);
      toast.success('Subscription paused successfully');
      setShowPauseModal(false);
      loadSubscriptions();
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to pause subscription';
      toast.error(errorMsg);
    }
  };

  const handleResume = async (id) => {
    try {
      await subscriptionAPI.resume(id);
      toast.success('Subscription resumed successfully');
      loadSubscriptions();
    } catch (error) {
      toast.error('Failed to resume subscription');
    }
  };

  const handleCancel = async (id) => {
    if (!window.confirm('Are you sure you want to cancel this subscription?')) return;

    try {
      await subscriptionAPI.cancel(id);
      toast.success('Subscription cancelled successfully');
      loadSubscriptions();
    } catch (error) {
      toast.error('Failed to cancel subscription');
    }
  };

  const filteredSubscriptions = activeFilter === 'all' 
    ? subscriptions 
    : subscriptions.filter(s => s.status === activeFilter);

  if (loading) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Loading subscriptions...</div>
      </CustomerLayout>
    );
  }

  return (
    <CustomerLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">My Subscriptions</h1>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Total Subscriptions</p>
            <p className="text-3xl font-bold text-blue-600">{stats.total || 0}</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Active</p>
            <p className="text-3xl font-bold text-green-600">{stats.active || 0}</p>
          </div>
          <div className="bg-yellow-50 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Paused</p>
            <p className="text-3xl font-bold text-yellow-600">{stats.paused || 0}</p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-gray-600 text-sm">Monthly Value</p>
            <p className="text-3xl font-bold text-purple-600">₹{(stats.total_monthly_value || 0).toFixed(0)}</p>
          </div>
        </div>

        {/* Filters */}
        <div className="flex gap-2 flex-wrap">
          {['all', 'active', 'paused', 'cancelled'].map((status) => (
            <button
              key={status}
              onClick={() => setActiveFilter(status)}
              className={`px-4 py-2 rounded-lg font-medium capitalize ${
                activeFilter === status
                  ? 'bg-blue-600 text-white'
                  : 'bg-white text-gray-700 border border-gray-300'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {/* Subscriptions List */}
        {filteredSubscriptions.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No subscriptions found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredSubscriptions.map((sub) => (
              <div key={sub.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                  {/* Product Info */}
                  <div>
                    <p className="text-sm text-gray-600">Product</p>
                    <p className="font-semibold text-gray-800">{sub.product_name || `Product #${sub.product_id}`}</p>
                    <p className="text-xs text-gray-500">Qty: {sub.quantity}</p>
                  </div>

                  {/* Frequency & Payment */}
                  <div>
                    <p className="text-sm text-gray-600">Frequency</p>
                    <p className="font-semibold capitalize text-gray-800">{sub.frequency.replace('_', '-')}</p>
                    <p className="text-xs text-gray-500">{sub.payment_method.toUpperCase()}</p>
                  </div>

                  {/* Dates */}
                  <div>
                    <p className="text-sm text-gray-600">Dates</p>
                    <p className="font-semibold text-gray-800 text-sm">{formatDate(sub.next_delivery_date)}</p>
                    <p className="text-xs text-gray-500">
                      {sub.end_date ? `Until ${formatDate(sub.end_date)}` : 'Ongoing'}
                    </p>
                  </div>

                  {/* Amount */}
                  <div>
                    <p className="text-sm text-gray-600">Per Delivery</p>
                    <p className="text-2xl font-bold text-green-600">₹{sub.total_amount.toFixed(2)}</p>
                    <p className="text-xs text-gray-500">{sub.total_orders_created} orders created</p>
                  </div>

                  {/* Status & Actions */}
                  <div className="flex flex-col items-end gap-2">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(sub.status)}`}>
                      {sub.status.toUpperCase()}
                    </span>
                    <div className="flex gap-2">
                      {sub.status === 'active' && (
                        <button
                          onClick={() => {
                            setSelectedSub(sub);
                            setShowPauseModal(true);
                          }}
                          className="text-sm px-2 py-1 bg-yellow-600 hover:bg-yellow-700 text-white rounded"
                        >
                          Pause
                        </button>
                      )}
                      {sub.status === 'paused' && (
                        <button
                          onClick={() => handleResume(sub.id)}
                          className="text-sm px-2 py-1 bg-green-600 hover:bg-green-700 text-white rounded"
                        >
                          Resume
                        </button>
                      )}
                      {sub.status !== 'cancelled' && (
                        <button
                          onClick={() => handleCancel(sub.id)}
                          className="text-sm px-2 py-1 bg-red-600 hover:bg-red-700 text-white rounded"
                        >
                          Cancel
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pause Modal */}
        {showPauseModal && selectedSub && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold text-gray-800 mb-4">Pause Subscription</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Reason (Optional)</label>
                  <textarea
                    value={pauseData.pause_reason}
                    onChange={(e) => setPauseData({ ...pauseData, pause_reason: e.target.value })}
                    placeholder="Why are you pausing?"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows="3"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Pause for (days)</label>
                  <input
                    type="number"
                    value={pauseData.pause_days}
                    onChange={(e) => setPauseData({ ...pauseData, pause_days: parseInt(e.target.value) })}
                    min="1"
                    max="365"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
              </div>

              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowPauseModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handlePause}
                  className="flex-1 px-4 py-2 bg-yellow-600 hover:bg-yellow-700 text-white rounded-lg font-medium"
                >
                  Pause
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </CustomerLayout>
  );
}