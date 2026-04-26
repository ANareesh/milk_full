import React, { useState, useEffect } from 'react';
import { productAPI, subscriptionAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';
import { formatDate } from '../../utils/date';
import { useNavigate } from 'react-router-dom';
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

export function SubscribeProductsPage() {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [showSubscribeModal, setShowSubscribeModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [formData, setFormData] = useState({
    quantity: 1,
    frequency: 'weekly',
    start_date: new Date().toISOString().split('T')[0],
    end_date: '',
    payment_method: 'upi',
    auto_renew: true,
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await productAPI.getAll();
      setProducts(response.data);
    } catch (error) {
      toast.error('Failed to load products');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribeClick = (product) => {
    setSelectedProduct(product);
    setFormData({
      quantity: 1,
      frequency: 'weekly',
      start_date: new Date().toISOString().split('T')[0],
      end_date: '',
      payment_method: 'upi',
      auto_renew: true,
    });
    setShowSubscribeModal(true);
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = async () => {
    try {
      // Validate form
      if (!formData.quantity || formData.quantity < 1) {
        toast.error('Quantity must be at least 1');
        return;
      }

      if (!formData.start_date) {
        toast.error('Start date is required');
        return;
      }

      if (formData.end_date && new Date(formData.end_date) <= new Date(formData.start_date)) {
        toast.error('End date must be after start date');
        return;
      }

      const subscriptionData = {
        product_id: selectedProduct.id,
        quantity: parseInt(formData.quantity),
        frequency: formData.frequency,
        start_date: new Date(formData.start_date).toISOString(),
        end_date: formData.end_date ? new Date(formData.end_date).toISOString() : null,
        payment_method: formData.payment_method,
        auto_renew: formData.auto_renew,
      };

      await subscriptionAPI.create(subscriptionData);
      toast.success('Subscription created successfully!');
      setShowSubscribeModal(false);
      // Optionally refresh or redirect
    } catch (error) {
      const errorMsg = error.response?.data?.detail || 'Failed to create subscription';
      toast.error(errorMsg);
      console.error(error);
    }
  };

  if (loading) {
    return (
      <CustomerLayout>
        <div className="flex justify-center items-center h-64">Loading products...</div>
      </CustomerLayout>
    );
  }

  return (
    <CustomerLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">Subscribe to Products</h1>
        <p className="text-gray-600">Get regular deliveries of your favorite products</p>
         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => {
            const effectivePrice = product.offer_price || (product.unit_price * (1 - product.discount_percentage / 100));
            const hasOffer = product.discount_percentage > 0 || product.offer_price;
            
            return (
              <div key={product.id} className="bg-white rounded-lg shadow-md p-6 relative hover:shadow-lg transition">
                {/* Product Image */}
                {product.image_url && (
                  <img
                    src={`http://localhost:8000${product.image_url}`}
                    alt={product.name}
                    className="w-full h-40 object-cover rounded mb-4"
                  />
                )}

                {/* Offer Badge */}
                {hasOffer && (
                  <div className="absolute top-2 right-2 bg-red-500 text-white px-3 py-1 rounded-full text-sm font-bold">
                    {product.discount_percentage > 0 ? `${product.discount_percentage}% OFF` : 'OFFER'}
                  </div>
                )}

                {/* Product Name & Type */}
                <h2 className="text-xl font-semibold text-gray-800 mb-1">{product.name}</h2>
                <p className="text-xs text-gray-500 mb-2">{product.product_type.replace('_', ' ').toUpperCase()}</p>

                {/* Description */}
                {product.description && (
                  <p className="text-gray-600 text-sm mb-3">{product.description}</p>
                )}

                {/* Pricing */}
                <div className="mb-4">
                  <div className="flex items-center gap-2 mb-2">
                    {hasOffer ? (
                      <>
                        <span className="text-sm text-gray-500 line-through">₹{product.unit_price.toFixed(2)}</span>
                        <span className="text-2xl font-bold text-green-600">₹{effectivePrice.toFixed(2)}</span>
                      </>
                    ) : (
                      <span className="text-2xl font-bold text-green-600">₹{product.unit_price.toFixed(2)}</span>
                    )}
                    <span className="text-xs text-gray-500">/{product.unit}</span>
                  </div>
                  
                  {/* Offer Description */}
                  {product.offer_description && (
                    <p className="text-xs text-red-600 font-semibold mb-2">🎉 {product.offer_description}</p>
                  )}

                  {/* Nutritional Info */}
                  {product.nutritional_info && (
                    <p className="text-xs text-gray-600 bg-gray-50 p-2 rounded mb-2">
                      <strong>Info:</strong> {product.nutritional_info}
                    </p>
                  )}

                  {/* Fat Percentage */}
                  {product.fat_percentage && (
                    <p className="text-xs text-gray-600">
                      📊 Fat: {product.fat_percentage}%
                    </p>
                  )}
                </div>

                {/* Stock & Limits */}
                <div className="text-sm text-gray-600 mb-4">
                  <p>Stock: {product.available_quantity} {product.unit}</p>
                  {product.max_quantity_per_order && (
                    <p className="text-xs">Max per order: {product.max_quantity_per_order}</p>
                  )}
                </div>

                {/* Subscribe Button */}
                {/* Action Buttons */}
                <div className="flex gap-2">
                  <button
                    onClick={() => navigate(`/customer/products/${product.id}`)}
                    disabled={product.available_quantity === 0}
                    className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium"
                  >
                    {product.available_quantity > 0 ? 'View Details' : 'Out of Stock'}
                  </button>
                  <button
                    onClick={() => handleSubscribeClick(product)}
                    disabled={product.available_quantity === 0}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium"
                  >
                    Subscribe
                  </button>
                </div>
                {/* <button
                  onClick={() => handleSubscribeClick(product)}
                  disabled={product.available_quantity === 0}
                  className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium"
                >
                  {product.available_quantity > 0 ? 'Subscribe' : 'Out of Stock'}
                </button> */}
              </div>
            );
          })}
        </div>
        {/* <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <div key={product.id} className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold text-gray-800 mb-2">{product.name}</h2>
              <p className="text-gray-600 text-sm mb-4">{product.description}</p>
              <div className="flex justify-between items-center mb-4">
                <span className="text-2xl font-bold text-green-600">₹{product.unit_price}</span>
                <span className="text-sm text-gray-500">Stock: {product.available_quantity}</span>
              </div>
              <button
                onClick={() => handleSubscribeClick(product)}
                disabled={product.available_quantity === 0}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium"
              >
                {product.available_quantity > 0 ? 'Subscribe' : 'Out of Stock'}
              </button>
            </div>
          ))}
        </div> */}

        {/* Subscribe Modal */}
        {showSubscribeModal && selectedProduct && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4 max-h-96 overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Subscribe to {selectedProduct.name}</h2>

              <div className="space-y-4">
                {/* Quantity */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Quantity *</label>
                  <input
                    type="number"
                    name="quantity"
                    value={formData.quantity}
                    onChange={handleFormChange}
                    min="1"
                    max="100"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>

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
                  <p className="text-xs text-gray-500 mt-1">Leave empty for ongoing subscription</p>
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
                      ₹{((selectedProduct.offer_price || (selectedProduct.unit_price * (1 - selectedProduct.discount_percentage / 100))) * formData.quantity).toFixed(2)}
                    {/* ₹{(selectedProduct.unit_price * formData.quantity).toFixed(2)} */}
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
                  onClick={handleSubmit}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
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