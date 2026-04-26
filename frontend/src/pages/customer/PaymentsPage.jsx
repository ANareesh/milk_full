/**
 * Customer Payments Page
 */

import React, { useState, useEffect } from 'react';
import { paymentAPI, orderAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';
import { formatDate } from '../../utils/date';

export function CustomerPaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [pendingOrders, setPendingOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPaymentForm, setShowPaymentForm] = useState(false);
  const [selectedOrderId, setSelectedOrderId] = useState('');
  const [paymentForm, setPaymentForm] = useState({
    amount: '',
    paymentMethod: 'upi',
    upiId: '',
  });

  useEffect(() => {
    loadPaymentsAndOrders();
  }, []);

  const loadPaymentsAndOrders = async () => {
    try {
      setLoading(true);
      
      // Load completed payments
      const paymentsResponse = await paymentAPI.getMyPayments();
      setPayments(paymentsResponse.data || []);
      
      // Load pending orders that need payment
      const ordersResponse = await orderAPI.getMyOrders();
      const unpaid = ordersResponse.data?.filter(order => 
        order.status === 'pending' || order.status === 'confirmed'
      ) || [];
      setPendingOrders(unpaid);
    } catch (error) {
      console.error('Error loading payments:', error);
      toast.error('Failed to load payments');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentSubmit = async (e) => {
    e.preventDefault();

    if (!paymentForm.amount || !paymentForm.paymentMethod) {
      toast.error('Please fill all fields');
      return;
    }

    if (!selectedOrderId && pendingOrders.length > 0) {
      toast.error('Please select an order to pay');
      return;
    }

    try {
      let response;
      const paymentData = {
        amount: parseFloat(paymentForm.amount),
        payment_method: paymentForm.paymentMethod,
        order_id: selectedOrderId || null,
      };

      if (paymentForm.paymentMethod === 'upi') {
        response = await paymentAPI.createUPI({
          ...paymentData,
          upi_id: paymentForm.upiId,
        });
      } else if (paymentForm.paymentMethod === 'card') {
        toast.error('Card payment requires integration');
        return;
      } else if (paymentForm.paymentMethod === 'cash') {
        response = await paymentAPI.createCash(paymentData);
      }

      toast.success('Payment recorded successfully');
      setShowPaymentForm(false);
      setSelectedOrderId('');
      setPaymentForm({ amount: '', paymentMethod: 'upi', upiId: '' });
      loadPaymentsAndOrders();
    } catch (error) {
      toast.error('Payment failed');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      completed: 'bg-green-100 text-green-800',
      pending: 'bg-yellow-100 text-yellow-800',
      failed: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Loading payments...</div>
      </CustomerLayout>
    );
  }

  const totalDue = pendingOrders.reduce((sum, order) => sum + (order.total_amount || 0), 0);
  const totalPaid = payments.reduce((sum, payment) => sum + (payment.amount || 0), 0);

  return (
    <CustomerLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Payment History</h1>
          {totalDue > 0 && (
            <button
              onClick={() => setShowPaymentForm(!showPaymentForm)}
              className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
            >
              Make Payment
            </button>
          )}
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-600 text-sm">Amount Due</p>
            <p className="text-3xl font-bold text-red-600">₹{totalDue.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-600 text-sm">Amount Paid</p>
            <p className="text-3xl font-bold text-green-600">₹{totalPaid.toFixed(2)}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-600 text-sm">Total Orders</p>
            <p className="text-3xl font-bold text-blue-600">{pendingOrders.length + payments.length}</p>
          </div>
        </div>

        {showPaymentForm && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">New Payment</h2>
            <form onSubmit={handlePaymentSubmit} className="space-y-4">
              {/* Select Order */}
              {pendingOrders.length > 0 && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Select Order *
                  </label>
                  <select
                    value={selectedOrderId}
                    onChange={(e) => {
                      const orderId = e.target.value;
                      setSelectedOrderId(orderId);
                      // Auto-fill amount with order total
                      const selectedOrder = pendingOrders.find(o => o.id === parseInt(orderId));
                      if (selectedOrder) {
                        setPaymentForm({
                          ...paymentForm,
                          amount: selectedOrder.total_amount.toString()
                        });
                      }
                    }}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg bg-white"
                    required
                  >
                    <option value="">-- Choose an order --</option>
                    {pendingOrders.map((order) => (
                      <option key={order.id} value={order.id}>
                        Order #{order.order_number} - ₹{(order.total_amount || 0).toFixed(2)}
                      </option>
                    ))}
                  </select>
                </div>
              )}

              {/* Selected Order Details */}
              {selectedOrderId && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                  {pendingOrders.map((order) => {
                    if (order.id === parseInt(selectedOrderId)) {
                      return (
                        <div key={order.id}>
                          <p className="text-sm font-semibold text-gray-800">Order Details</p>
                          <p className="text-lg font-bold text-blue-600 mt-2">Order #{order.order_number}</p>
                          <p className="text-sm text-gray-600">Placed: {formatDate(order.created_at)}</p>
                          <p className="text-sm text-gray-600">Status: <span className="font-semibold">{order.status.toUpperCase()}</span></p>
                          <p className="text-lg font-bold text-red-600 mt-2">Amount Due: ₹{(order.total_amount || 0).toFixed(2)}</p>
                        </div>
                      );
                    }
                    return null;
                  })}
                </div>
              )}

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Amount (₹)
                </label>
                <input
                  type="number"
                  step="0.01"
                  value={paymentForm.amount}
                  onChange={(e) => setPaymentForm({ ...paymentForm, amount: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  placeholder="Enter amount to pay"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Payment Method
                </label>
                <select
                  value={paymentForm.paymentMethod}
                  onChange={(e) => setPaymentForm({ ...paymentForm, paymentMethod: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                >
                  <option value="upi">UPI</option>
                  <option value="card">Credit Card</option>
                  <option value="cash">Cash on Delivery</option>
                </select>
              </div>

              {paymentForm.paymentMethod === 'upi' && (
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    UPI ID
                  </label>
                  <input
                    type="text"
                    value={paymentForm.upiId}
                    onChange={(e) => setPaymentForm({ ...paymentForm, upiId: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    placeholder="your-mobile@upi"
                  />
                </div>
              )}

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                >
                  Process Payment
                </button>
                <button
                  type="button"
                  onClick={() => setShowPaymentForm(false)}
                  className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {/* Pending Orders - Amounts Due */}
        {pendingOrders.length > 0 && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <h2 className="text-lg font-bold text-orange-800 mb-4">Pending Payments</h2>
            <div className="space-y-3">
              {pendingOrders.map((order) => (
                <div key={order.id} className="bg-white rounded-lg p-4 flex justify-between items-center">
                  <div>
                    <p className="font-semibold">Order #{order.order_number}</p>
                    <p className="text-sm text-gray-600">Placed: {formatDate(order.created_at)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-lg font-bold text-red-600">₹{(order.total_amount || 0).toFixed(2)}</p>
                    <span className={`text-xs px-2 py-1 rounded ${getStatusBadge(order.status)}`}>
                      {order.status.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Completed Payments */}
        <div className="bg-white rounded-lg shadow-lg overflow-x-auto">
          <div className="px-6 py-4 border-b border-gray-200">
            <h2 className="text-lg font-bold text-gray-800">Completed Payments</h2>
          </div>
          {payments.length > 0 ? (
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Date</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Amount</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Method</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {payments.map((payment) => (
                  <tr key={payment.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm">{formatDate(payment.created_at)}</td>
                    <td className="px-6 py-4 text-sm font-semibold">₹{(payment.amount || 0).toFixed(2)}</td>
                    <td className="px-6 py-4 text-sm">{payment.payment_method || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusBadge(payment.status)}`}>
                        {payment.status?.toUpperCase()}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <div className="px-6 py-8 text-center">
              <p className="text-gray-600">
                {pendingOrders.length > 0 
                  ? 'No completed payments yet. Complete a pending payment to see it here.' 
                  : 'No payment history yet.'}
              </p>
            </div>
          )}
        </div>
      </div>
    </CustomerLayout>
  );
}