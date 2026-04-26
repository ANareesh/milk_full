import React, { useState, useEffect } from 'react';
import { customerAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AdminLayout } from '../../components/AdminLayout';

export function AdminCustomersPage() {
  const [customers, setCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showPendingBalance, setShowPendingBalance] = useState(false);
  const [pendingBalances, setPendingBalances] = useState([]);

  useEffect(() => {
    loadCustomers();
  }, []);

  const loadCustomers = async () => {
    try {
      setLoading(true);
      const response = await customerAPI.getAll();
      setCustomers(response.data);
    } catch (error) {
      console.error('Error loading customers:', error);
      toast.error('Failed to load customers');
    } finally {
      setLoading(false);
    }
  };

  const loadPendingBalance = async () => {
    try {
      const response = await customerAPI.getPendingBalance();
      setPendingBalances(response.data);
      setShowPendingBalance(true);
    } catch (error) {
      console.error('Error loading pending balance:', error);
      toast.error('Failed to load pending balance');
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64">Loading customers...</div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <h1 className="text-3xl font-bold text-gray-800">Customers Management</h1>
          <button
            onClick={loadPendingBalance}
            className="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
          >
            View Pending Balance
          </button>
        </div>

        {showPendingBalance && pendingBalances.length > 0 && (
          <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
            <h2 className="text-lg font-bold text-orange-800 mb-4">Customers with Pending Balance</h2>
            <div className="space-y-2">
              {pendingBalances.map((item) => (
                <div key={item.id} className="flex justify-between items-center p-3 bg-white rounded">
                  <span className="font-medium">Customer #{item.id}</span>
                  <span className="text-lg font-bold text-red-600">₹{(item.total_amount_due || 0).toFixed(2)}</span>
                </div>
              ))}
              {/* {pendingBalances.map((item) => (
                <div key={item.customer_id} className="flex justify-between items-center p-3 bg-white rounded">
                  <span className="font-medium">Customer #{item.customer_id}</span>
                  <span className="text-lg font-bold text-red-600">₹{item.amount_due.toFixed(2)}</span>
                </div>
              ))} */}
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-600 text-sm">Total Customers</p>
            <p className="text-3xl font-bold text-blue-600">{customers.length}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-600 text-sm">Pending Balance</p>
            <p className="text-3xl font-bold text-red-600">
              ₹{customers.reduce((sum, c) => sum + (c.total_amount_due || 0), 0).toFixed(2)}
            </p>
          </div>
          <div className="bg-white rounded-lg shadow p-4">
            <p className="text-gray-600 text-sm">Registered Today</p>
            <p className="text-3xl font-bold text-green-600">
              {customers.filter(c => new Date(c.created_at).toDateString() === new Date().toDateString()).length}
            </p>
          </div>
        </div>

        {customers.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No customers yet</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-lg overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">ID</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">User ID</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Address</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">City</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Balance Due</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Registered</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {customers.map((customer) => (
                  <tr key={customer.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">{customer.id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">User #{customer.user_id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{customer.address || 'Not set'}</td>
                    <td className="px-6 py-4 text-sm text-gray-900">{customer.city || 'Not set'}</td>
                    <td className="px-6 py-4 text-sm">
                      <span className={customer.total_amount_due > 0 ? 'text-red-600 font-semibold' : 'text-green-600 font-semibold'}>
                        ₹{customer.total_amount_due?.toFixed(2) || '0.00'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(customer.created_at).toLocaleDateString()}
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