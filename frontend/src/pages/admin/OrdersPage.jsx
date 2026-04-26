/**
 * Admin Orders Management Page
 */

import React, { useState, useEffect } from 'react';
import { orderAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AdminLayout } from '../../components/AdminLayout';
import { formatDate } from '../../utils/date';

export function AdminOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await orderAPI.getAll();
      setOrders(response.data);
    } catch (error) {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (orderId) => {
    if (!window.confirm('Confirm this order?')) return;
    try {
      await orderAPI.confirm(orderId);
      toast.success('Order confirmed');
      loadOrders();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to confirm order');
    }
  };

  const filteredOrders = filterStatus === 'all' 
    ? orders 
    : orders.filter(order => order.status === filterStatus);

  const getStatusColor = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      confirmed: 'bg-blue-100 text-blue-800',
      out_for_delivery: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      cancelled: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
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
        <h1 className="text-3xl font-bold text-gray-800">Orders Management</h1>

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-4 py-2 rounded-lg font-medium ${filterStatus === 'all' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300'}`}
          >
            All ({orders.length})
          </button>
          <button
            onClick={() => setFilterStatus('pending')}
            className={`px-4 py-2 rounded-lg font-medium ${filterStatus === 'pending' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300'}`}
          >
            Pending ({orders.filter(o => o.status === 'pending').length})
          </button>
          <button
            onClick={() => setFilterStatus('confirmed')}
            className={`px-4 py-2 rounded-lg font-medium ${filterStatus === 'confirmed' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300'}`}
          >
            Confirmed ({orders.filter(o => o.status === 'confirmed').length})
          </button>
          <button
            onClick={() => setFilterStatus('delivered')}
            className={`px-4 py-2 rounded-lg font-medium ${filterStatus === 'delivered' ? 'bg-green-600 text-white' : 'bg-white text-gray-700 border border-gray-300'}`}
          >
            Delivered ({orders.filter(o => o.status === 'delivered').length})
          </button>
        </div>

        {filteredOrders.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No orders with this status</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-lg overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Order #</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Customer</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Amount</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredOrders.map((order) => (
                  <tr key={order.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">{order.order_number}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">Customer #{order.customer_id}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-600">₹{order.total_amount}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                        {order.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">{formatDate(order.created_at)}</td>
                    <td className="px-6 py-4 text-sm flex gap-2">
                      {order.status === 'pending' && (
                        <button
                          onClick={() => handleConfirm(order.id)}
                          className="px-3 py-1 bg-green-600 hover:bg-green-700 text-white rounded text-xs font-medium"
                        >
                          Confirm
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}