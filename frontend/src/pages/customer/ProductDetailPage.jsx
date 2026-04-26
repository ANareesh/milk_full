import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { productAPI, orderAPI, subscriptionAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';

const FREQUENCIES = [
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'bi_weekly', label: 'Bi-Weekly' },
  { value: 'monthly', label: 'Monthly' },
];

const PAYMENT_METHODS = [
  { value: 'upi', label: 'UPI' },
  { value: 'card', label: 'Credit/Debit Card' },
  { value: 'cash', label: 'Cash on Delivery' },
];

export function ProductDetailPage() {
  const { productId } = useParams();
  const navigate = useNavigate();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quantity, setQuantity] = useState(1);
  const [showOrderModal, setShowOrderModal] = useState(false);
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const [formData, setFormData] = useState({
    frequency: 'weekly',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    payment_method: 'upi',
    auto_renew: true,
  });

  useEffect(() => {
    loadProduct();
  }, [productId]);

  const loadProduct = async () => {
    try {
      setLoading(true);
      const response = await productAPI.getDetails(productId);
      setProduct(response.data);
    } catch (error) {
      toast.error('Failed to load product');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleOrderClick = async () => {
    if (!quantity || quantity < 1) {
      toast.error('Please enter valid quantity');
      return;
    }

    try {
      await orderAPI.create({
        product_id: product.id,
        quantity: parseFloat(quantity),
        delivery_date: new Date().toISOString(),
      });
      toast.success('Order placed successfully!');
      setShowOrderModal(false);
      setQuantity(1);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to place order');
    }
  };

  const handleSubscribeClick = async () => {
    if (!quantity || quantity < 1) {
      toast.error('Please enter valid quantity');
      return;
    }

    if (formData.end_date && new Date(formData.end_date) <= new Date(formData.start_date)) {
      toast.error('End date must be after start date');
      return;
    }

    try {
      await subscriptionAPI.create({
        product_id: product.id,
        quantity: parseInt(quantity),
        frequency: formData.frequency,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
        payment_method: formData.payment_method,
        auto_renew: formData.auto_renew,
      });
      toast.success('Subscription created successfully!');
      setShowSubscribeModal(false);
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to create subscription');
    }
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  if (loading) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Loading product...</div>
      </CustomerLayout>
    );
  }

  if (!product) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Product not found</div>
      </CustomerLayout>
    );
  }

  const effectivePrice = product.offer_price || (product.unit_price * (1 - product.discount_percentage / 100));
  const hasOffer = product.discount_percentage > 0 || product.offer_price;
  const savings = product.unit_price - effectivePrice;

  return (
    <CustomerLayout>
      <div className="space-y-8">
        {/* Breadcrumb */}
        <button onClick={() => navigate(-1)} className="text-blue-600 hover:underline">
          ← Back
        </button>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Product Image */}
          <div className="flex justify-center items-center bg-gray-100 rounded-lg p-8">
            {product.image_url ? (
              <img
                src={`http://localhost:8000${product.image_url}`}
                alt={product.name}
                className="max-w-full h-auto max-h-96 object-contain"
              />
            ) : (
              <div className="text-gray-400 text-center">
                <p>No image available</p>
              </div>
            )}
          </div>

          {/* Product Details */}
          <div className="space-y-6">
            {/* Offer Badge */}
            {hasOffer && (
              <div className="bg-yellow-100 border-l-4 border-yellow-500 p-4">
                <p className="text-yellow-800 font-semibold">
                  🎉 {product.offer_description || `Order via App and get Upto ${product.discount_percentage}% OFF`}
                </p>
              </div>
            )}

            {/* Product Name & Type */}
            <div>
              <h1 className="text-4xl font-bold text-gray-800 mb-2">{product.name}</h1>
              <p className="text-lg text-gray-600">{product.unit}</p>
              <p className="text-sm text-gray-500 mt-2">{product.product_type.replace('_', ' ').toUpperCase()}</p>
            </div>

            {/* Pricing */}
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="flex items-center gap-4 mb-2">
                {hasOffer ? (
                  <>
                    <span className="text-4xl font-bold text-green-600">₹{effectivePrice.toFixed(2)}</span>
                    <span className="text-2xl text-gray-400 line-through">₹{product.unit_price.toFixed(2)}</span>
                  </>
                ) : (
                  <span className="text-4xl font-bold text-green-600">₹{product.unit_price.toFixed(2)}</span>
                )}
              </div>
              {hasOffer && (
                <p className="text-sm text-green-600 font-semibold">
                  Save ₹{savings.toFixed(2)} ({product.discount_percentage}% off)
                </p>
              )}
            </div>

            {/* Stock Status */}
            <div>
              {product.available_quantity > 0 ? (
                <p className="text-green-600 font-semibold">✓ In Stock ({product.available_quantity} {product.unit})</p>
              ) : (
                <p className="text-red-600 font-semibold">✗ Out of Stock</p>
              )}
            </div>

            {/* Quantity Selector */}
            <div className="flex items-center gap-4">
              <label className="text-gray-700 font-medium">Quantity:</label>
              <div className="flex items-center border border-gray-300 rounded-lg">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  −
                </button>
                <input
                  type="number"
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseFloat(e.target.value) || 1))}
                  className="w-16 text-center border-none focus:outline-none"
                  step="0.5"
                />
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="px-4 py-2 text-gray-600 hover:bg-gray-100"
                >
                  +
                </button>
              </div>
              <span className="text-gray-600">
                Total: ₹{(effectivePrice * quantity).toFixed(2)}
              </span>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => setShowOrderModal(true)}
                disabled={product.available_quantity === 0}
                className="flex-1 px-6 py-3 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-semibold text-lg"
              >
                Order Now
              </button>
              <button
                onClick={() => setShowSubscribeModal(true)}
                disabled={product.available_quantity === 0}
                className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-semibold text-lg"
              >
                Subscribe
              </button>
            </div>
          </div>
        </div>

        {/* Features Section */}
        <div className="bg-white p-8 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold text-gray-800 mb-6">Key Features</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {product.nutritional_info && (
              <div className="flex gap-3 items-start">
                <span className="text-2xl">📊</span>
                <div>
                  <p className="font-semibold text-gray-800">Nutritional Info</p>
                  <p className="text-gray-600 text-sm">{product.nutritional_info}</p>
                </div>
              </div>
            )}
            {product.fat_percentage && (
              <div className="flex gap-3 items-start">
                <span className="text-2xl">🥛</span>
                <div>
                  <p className="font-semibold text-gray-800">Fat Content</p>
                  <p className="text-gray-600 text-sm">{product.fat_percentage}% Pure Milk Fat</p>
                </div>
              </div>
            )}
            {product.discount_percentage > 0 && (
              <div className="flex gap-3 items-start">
                <span className="text-2xl">🎉</span>
                <div>
                  <p className="font-semibold text-gray-800">Special Offer</p>
                  <p className="text-gray-600 text-sm">{product.discount_percentage}% Discount Available</p>
                </div>
              </div>
            )}
            <div className="flex gap-3 items-start">
              <span className="text-2xl">🚚</span>
              <div>
                <p className="font-semibold text-gray-800">Fast Delivery</p>
                <p className="text-gray-600 text-sm">Delivered fresh to your doorstep</p>
              </div>
            </div>
            <div className="flex gap-3 items-start">
              <span className="text-2xl">✓</span>
              <div>
                <p className="font-semibold text-gray-800">Quality Assured</p>
                <p className="text-gray-600 text-sm">100% Pure & Tested</p>
              </div>
            </div>
            <div className="flex gap-3 items-start">
              <span className="text-2xl">🔄</span>
              <div>
                <p className="font-semibold text-gray-800">Subscription Available</p>
                <p className="text-gray-600 text-sm">Regular deliveries convenient</p>
              </div>
            </div>
          </div>
        </div>

        {/* Description Section */}
        {product.description && (
          <div className="bg-white p-8 rounded-lg shadow-md">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">About This Product</h2>
            <p className="text-gray-700 leading-relaxed">{product.description}</p>
          </div>
        )}

        {/* Order Modal */}
        {showOrderModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Place Order</h2>
              <p className="text-gray-600 mb-4">Confirm your order for {product.name}</p>
              
              <div className="bg-blue-50 p-4 rounded-lg mb-6">
                <p className="text-sm text-gray-600">Order Total:</p>
                <p className="text-2xl font-bold text-green-600">₹{(effectivePrice * quantity).toFixed(2)}</p>
              </div>

              <div className="flex gap-3">
                <button
                  onClick={() => setShowOrderModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleOrderClick}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                >
                  Confirm Order
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Subscribe Modal */}
        {showSubscribeModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-lg p-8 max-w-md w-full max-h-96 overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Subscribe to {product.name}</h2>

              <div className="space-y-4">
                {/* Frequency */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Delivery Frequency *</label>
                  <select
                    name="frequency"
                    value={formData.frequency}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {FREQUENCIES.map((f) => (
                      <option key={f.value} value={f.value}>
                        {f.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Start Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Start Date *</label>
                  <input
                    type="date"
                    name="start_date"
                    value={formData.start_date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* End Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">End Date (Optional)</label>
                  <input
                    type="date"
                    name="end_date"
                    value={formData.end_date}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

                {/* Payment Method */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Payment Method *</label>
                  <select
                    name="payment_method"
                    value={formData.payment_method}
                    onChange={handleFormChange}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {PAYMENT_METHODS.map((m) => (
                      <option key={m.value} value={m.value}>
                        {m.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Auto Renew */}
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    name="auto_renew"
                    checked={formData.auto_renew}
                    onChange={handleFormChange}
                    className="w-4 h-4 text-blue-600 rounded"
                  />
                  <label className="ml-2 text-sm text-gray-700">Auto-renew this subscription</label>
                </div>

                {/* Total */}
                <div className="bg-blue-50 p-3 rounded-lg">
                  <p className="text-sm text-gray-600">Price per delivery:</p>
                  <p className="text-lg font-bold text-green-600">
                    ₹{(effectivePrice * quantity).toFixed(2)}
                  </p>
                </div>
              </div>

              {/* Buttons */}
              <div className="flex gap-3 mt-6">
                <button
                  onClick={() => setShowSubscribeModal(false)}
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubscribeClick}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
                >
                  Subscribe
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </CustomerLayout>
  );
}