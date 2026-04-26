/**
 * Admin Products Management Page
 */

import React, { useState, useEffect } from 'react';
import { productAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AdminLayout } from '../../components/AdminLayout';
// import { productAPI } from '../../services/api';

export function AdminProductsPage() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    product_type: 'full_cream',
    unit: 'L',
    unit_price: '',
    available_quantity: '',
    fat_percentage: '',
  });

  useEffect(() => {
    loadProducts();
  }, []);

  const loadProducts = async () => {
    try {
      setLoading(true);
      const response = await productAPI.list();
      setProducts(response.data);
    } catch (error) {
      toast.error('Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (editingId) {
        await productAPI.update(editingId, {
          ...formData,
          unit_price: parseFloat(formData.unit_price),
          available_quantity: parseFloat(formData.available_quantity),
          fat_percentage: formData.fat_percentage ? parseFloat(formData.fat_percentage) : null,
        });
        toast.success('Product updated');
      } else {
        await productAPI.create({
          ...formData,
          unit_price: parseFloat(formData.unit_price),
          available_quantity: parseFloat(formData.available_quantity),
          fat_percentage: formData.fat_percentage ? parseFloat(formData.fat_percentage) : null,
        });
        toast.success('Product created');
      }

      setShowForm(false);
      setEditingId(null);
      setFormData({
        name: '',
        description: '',
        product_type: 'full_cream',
        unit: 'L',
        unit_price: '',
        available_quantity: '',
        fat_percentage: '',
      });
      loadProducts();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to save product');
    }
  };

  const handleEdit = (product) => {
    setEditingId(product.id);
    setFormData({
      name: product.name,
      description: product.description || '',
      product_type: product.product_type,
      unit: product.unit,
      unit_price: product.unit_price,
      available_quantity: product.available_quantity,
      fat_percentage: product.fat_percentage || '',
    });
    setShowForm(true);
  };

const handleImageUpload = async (productId, e) => {
  const file = e.target.files[0];
  if (!file) return;
  
  try {
    const response = await productAPI.uploadImage(productId, file);
    console.log('Image uploaded:', response.data.image_url);
    // Refresh product list or update state with new image URL
  } catch (error) {
    console.error('Upload failed:', error);
    alert('Failed to upload image');
  }
};


  const handleDelete = async (productId) => {
    if (!window.confirm('Are you sure you want to delete this product?')) return;

    try {
      await productAPI.delete(productId);
      toast.success('Product deleted');
      loadProducts();
    } catch (error) {
      toast.error('Failed to delete product');
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
          <h1 className="text-3xl font-bold text-gray-800">Products Management</h1>
          <button
            onClick={() => {
              setShowForm(!showForm);
              setEditingId(null);
              setFormData({
                name: '',
                description: '',
                product_type: 'full_cream',
                unit: 'L',
                unit_price: '',
                available_quantity: '',
                fat_percentage: '',
              });
            }}
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
          >
            {showForm ? 'Cancel' : 'Add Product'}
          </button>
        </div>

        {showForm && (
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              {editingId ? 'Edit Product' : 'Add New Product'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Name</label>
                  <input
                    type="text"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Product Type</label>
                  <select
                    name="product_type"
                    value={formData.product_type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="full_cream">Whole / Full Cream</option>
                    <option value="skimmed">Skimmed Milk</option>
                    <option value="toned">Toned Milk</option>
                    <option value="double_toned">Double Toned</option>
                    <option value="cow_milk">Cow Milk</option>
                    <option value="buffalo_milk">Buffalo Milk</option>
                    <option value="goat_milk">Goat Milk</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Unit Price (₹)</label>
                  <input
                    type="number"
                    step="0.01"
                    name="unit_price"
                    value={formData.unit_price}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Unit</label>
                  <select
                    name="unit"
                    value={formData.unit}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  >
                    <option value="L">Litre</option>
                    <option value="ml">Millilitre</option>
                    <option value="kg">Kilogram</option>
                    <option value="g">Gram</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Available Quantity</label>
                  <input
                    type="number"
                    step="0.1"
                    name="available_quantity"
                    value={formData.available_quantity}
                    onChange={handleInputChange}
                    required
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Fat Percentage</label>
                  <input
                    type="number"
                    step="0.1"
                    name="fat_percentage"
                    value={formData.fat_percentage}
                    onChange={handleInputChange}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                />
              </div>

              <div className="flex gap-2">
                <button
                  type="submit"
                  className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                >
                  {editingId ? 'Update Product' : 'Create Product'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowForm(false)}
                  className="px-6 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        {products.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No products yet. Create your first product!</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-lg overflow-hidden">
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Type</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Price</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Stock</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900">{product.name}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{product.product_type}</td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-600">
                      ₹{product.unit_price}/{product.unit}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {product.available_quantity} {product.unit}
                    </td>
                    <td className="px-6 py-4 text-sm flex gap-2 items-center">
                      {product.image_url && (
                        <img 
                          src={`http://localhost:8000${product.image_url}`} 
                          alt={product.name}
                          className="w-8 h-8 rounded object-cover"
                        />
                      )}
                      <button
                        onClick={() => handleEdit(product)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium"
                      >
                        Edit
                      </button>
                      <label className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white rounded text-xs font-medium cursor-pointer">
                        Upload Image
                        <input
                          type="file"
                          accept="image/*"
                          className="hidden"
                          onChange={(e) => handleImageUpload(product.id, e)}
                        />
                      </label>
                      <button
                        onClick={() => handleDelete(product.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium"
                      >
                        Delete
                      </button>
                    </td>
                    {/* <td className="px-6 py-4 text-sm flex gap-2">
                      <button
                        onClick={() => handleEdit(product)}
                        className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => handleDelete(product.id)}
                        className="px-3 py-1 bg-red-600 hover:bg-red-700 text-white rounded text-xs font-medium"
                      >
                        Delete
                      </button>
                    </td> */}
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
