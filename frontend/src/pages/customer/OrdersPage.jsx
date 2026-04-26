/**
 * Customer Orders Tracking Page
 */

import React, { useState, useEffect } from 'react';
import { orderAPI, deliveryAPI, reviewAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';
import { formatDate } from '../../utils/date';

export function CustomerOrdersPage() {
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedOrderForTracking, setSelectedOrderForTracking] = useState(null);
  const [deliveryDetails, setDeliveryDetails] = useState(null);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [selectedOrderForReview, setSelectedOrderForReview] = useState(null);
  const [reviewForm, setReviewForm] = useState({
    rating: 5,
    quality_rating: 5,
    delivery_rating: 5,
    agent_rating: 5,
    comment: '',
    is_recommended: true,
  });

  useEffect(() => {
    loadOrders();
  }, []);

  const loadOrders = async () => {
    try {
      setLoading(true);
      const response = await orderAPI.getMyOrders();
      setOrders(response.data);
    } catch (error) {
      toast.error('Failed to load orders');
    } finally {
      setLoading(false);
    }
  };

  const handleTrackOrder = async (order) => {
    try {
      const response = await deliveryAPI.getDetails(order.id);
      setDeliveryDetails(response.data);
      setSelectedOrderForTracking(order);
    } catch (error) {
      toast.error('Failed to load delivery details');
    }
  };

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) return;

    try {
      await orderAPI.cancel(orderId);
      toast.success('Order cancelled');
      loadOrders();
    } catch (error) {
      toast.error('Failed to cancel order');
    }
  };

  const handleGiveRating = (order) => {
    setSelectedOrderForReview(order);
    setReviewForm({
      rating: 5,
      quality_rating: 5,
      delivery_rating: 5,
      agent_rating: 5,
      comment: '',
      is_recommended: true,
    });
    setShowReviewForm(true);
  };

  const handleSubmitReview = async () => {
    if (!selectedOrderForReview) return;

    try {
      await reviewAPI.create({
        order_id: selectedOrderForReview.id,
        product_id: selectedOrderForReview.product_id,
        ...reviewForm,
      });
      toast.success('Review submitted successfully!');
      setShowReviewForm(false);
      setSelectedOrderForReview(null);
      loadOrders();
    } catch (error) {
      toast.error('Failed to submit review');
    }
  };

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
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Loading...</div>
      </CustomerLayout>
    );
  }

  return (
    <CustomerLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">My Orders</h1>

        {orders.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No orders yet. Start by browsing our products!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {orders.map((order) => (
              <div key={order.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="text-lg font-semibold">{order.order_number}</h3>
                    <p className="text-gray-600 text-sm">
                      {formatDate(order.created_at)}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(order.status)}`}>
                    {order.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="mt-4 grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-gray-600">Quantity</p>
                    <p className="font-semibold">{order.quantity} {order.product_id ? 'units' : ''}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Total Amount</p>
                    <p className="font-semibold text-green-600">₹{order.total_amount}</p>
                  </div>
                  <div>
                    <p className="text-gray-600">Delivery Date</p>
                    <p className="font-semibold">{formatDate(order.delivery_date)}</p>
                  </div>
                </div>

                <div className="mt-4 flex gap-2">
                  <button
                    onClick={() => handleTrackOrder(order)}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm"
                  >
                    Track Order
                  </button>
                  {order.status === 'pending' && (
                    <button
                      onClick={() => handleCancelOrder(order.id)}
                      className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm"
                    >
                      Cancel
                    </button>
                  )}
                  {order.status === 'delivered' && (
                    <button
                      onClick={() => handleGiveRating(order)}
                      className="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium text-sm"
                    >
                      Give Rating
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Tracking Modal */}
        {selectedOrderForTracking && deliveryDetails && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Order Tracking</h2>

              <div className="space-y-4">
                <div className="bg-gray-100 p-4 rounded">
                  <p className="text-gray-600 text-sm">Order ID</p>
                  <p className="font-semibold">{selectedOrderForTracking.order_number}</p>
                </div>

                <div className="bg-gray-100 p-4 rounded">
                  <p className="text-gray-600 text-sm">Delivery Status</p>
                  <p className="font-semibold text-green-600">
                    {deliveryDetails.status.replace('_', ' ').toUpperCase()}
                  </p>
                </div>

                {deliveryDetails.delivery_time && (
                  <div className="bg-green-50 p-4 rounded border border-green-200">
                    <p className="text-green-700">
                      ✓ Delivered on {formatDate(deliveryDetails.delivery_time)}
                    </p>
                  </div>
                )}

                {deliveryDetails.failed_reason && (
                  <div className="bg-red-50 p-4 rounded border border-red-200">
                    <p className="text-red-700">
                      Delivery failed: {deliveryDetails.failed_reason}
                    </p>
                  </div>
                )}

                <button
                  onClick={() => {
                    setSelectedOrderForTracking(null);
                    setDeliveryDetails(null);
                  }}
                  className="w-full px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Review Form Modal */}
        {showReviewForm && selectedOrderForReview && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-8 max-w-lg w-full max-h-screen overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Rate Your Order</h2>
              
              <div className="space-y-4">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                  <p className="text-sm text-gray-600">Order #{selectedOrderForReview.order_number}</p>
                  <p className="font-semibold">Delivered on {formatDate(selectedOrderForReview.delivery_date)}</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Overall Rating (1-5) ⭐
                  </label>
                  <select
                    value={reviewForm.rating}
                    onChange={(e) => setReviewForm({ ...reviewForm, rating: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="1">1 - Poor</option>
                    <option value="2">2 - Fair</option>
                    <option value="3">3 - Good</option>
                    <option value="4">4 - Very Good</option>
                    <option value="5">5 - Excellent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quality Rating 🎯
                  </label>
                  <select
                    value={reviewForm.quality_rating}
                    onChange={(e) => setReviewForm({ ...reviewForm, quality_rating: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="1">1 - Poor</option>
                    <option value="2">2 - Fair</option>
                    <option value="3">3 - Good</option>
                    <option value="4">4 - Very Good</option>
                    <option value="5">5 - Excellent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Delivery Speed 🚚
                  </label>
                  <select
                    value={reviewForm.delivery_rating}
                    onChange={(e) => setReviewForm({ ...reviewForm, delivery_rating: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="1">1 - Very Slow</option>
                    <option value="2">2 - Slow</option>
                    <option value="3">3 - Average</option>
                    <option value="4">4 - Fast</option>
                    <option value="5">5 - Very Fast</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Delivery Agent 👤
                  </label>
                  <select
                    value={reviewForm.agent_rating}
                    onChange={(e) => setReviewForm({ ...reviewForm, agent_rating: parseInt(e.target.value) })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="1">1 - Poor</option>
                    <option value="2">2 - Fair</option>
                    <option value="3">3 - Good</option>
                    <option value="4">4 - Very Good</option>
                    <option value="5">5 - Excellent</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Comments (Optional)
                  </label>
                  <textarea
                    value={reviewForm.comment}
                    onChange={(e) => setReviewForm({ ...reviewForm, comment: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                    placeholder="Share your experience..."
                    rows="3"
                  />
                </div>

                <div>
                  <label className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={reviewForm.is_recommended}
                      onChange={(e) => setReviewForm({ ...reviewForm, is_recommended: e.target.checked })}
                      className="rounded"
                    />
                    <span className="text-sm text-gray-700">I would recommend this product</span>
                  </label>
                </div>

                <div className="flex gap-2 mt-6">
                  <button
                    onClick={handleSubmitReview}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                  >
                    Submit Review
                  </button>
                  <button
                    onClick={() => {
                      setShowReviewForm(false);
                      setSelectedOrderForReview(null);
                    }}
                    className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </CustomerLayout>
  );
}
