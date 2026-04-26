// /**
//  * Admin Dashboard Page
//  */

// import React, { useState, useEffect } from 'react';
// import { adminAPI } from '../../services/api';
// import toast from 'react-hot-toast';
// import { AdminLayout } from '../../components/AdminLayout';

// export function AdminDashboardPage() {
//   const [stats, setStats] = useState(null);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     loadDashboardStats();
//   }, []);

//   const loadDashboardStats = async () => {
//     try {
//       setLoading(true);
//       const response = await adminAPI.getDashboardStats();
//       setStats(response.data);
//       console.log('Dashboard stats:', response.data); // DEBUG
//     } catch (error) {
//       console.error('Error loading dashboard:', error);
//       toast.error('Failed to load dashboard stats');
//     } finally {
//       setLoading(false);
//     }
//   };

//   if (loading) {
//     return (
//       <AdminLayout>
//         <div className="flex justify-center items-center h-64">Loading dashboard...</div>
//       </AdminLayout>
//     );
//   }

//   if (!stats) {
//     return (
//       <AdminLayout>
//         <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
//           <p className="text-red-700">Failed to load dashboard</p>
//         </div>
//       </AdminLayout>
//     );
//   }

//   return (
//     <AdminLayout>
//       <div className="space-y-6">
//         <h1 className="text-3xl font-bold text-gray-800">Admin Dashboard</h1>

//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
//           {/* Total Users */}
//           <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
//             <p className="text-blue-600 text-sm font-medium">Total Users</p>
//             <p className="text-3xl font-bold text-blue-700 mt-2">
//               {((stats.total_customers || 0) + (stats.total_agents || 0))}
//             </p>
//             <p className="text-xs text-blue-600 mt-1">
//               Customers: {stats.total_customers || 0}
//             </p>
//             <p className="text-xs text-blue-600">
//               Agents: {stats.total_agents || 0}
//             </p>
//           </div>

//           {/* Today's Orders */}
//           <div className="bg-green-50 border border-green-200 rounded-lg p-6">
//             <p className="text-green-600 text-sm font-medium">Today's Orders</p>
//             <p className="text-3xl font-bold text-green-700 mt-2">
//               {stats.today_orders_count || 0}
//             </p>
//             <p className="text-xs text-green-600 mt-1">
//               Pending Deliveries: {stats.pending_deliveries || 0}
//             </p>
//           </div>

//           {/* Today's Revenue */}
//           <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
//             <p className="text-purple-600 text-sm font-medium">Today's Revenue</p>
//             <p className="text-3xl font-bold text-purple-700 mt-2">
//               ₹{(stats.today_revenue || 0).toFixed(2)}
//             </p>
//           </div>

//           {/* Total Products */}
//           <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
//             <p className="text-orange-600 text-sm font-medium">Total Products</p>
//             <p className="text-3xl font-bold text-orange-700 mt-2">
//               {stats.total_products || 0}
//             </p>
//           </div>
//         </div>

//         {/* Actions */}
//         <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
//           <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer">
//             <h3 className="text-lg font-semibold text-gray-800 mb-2">Manage Products</h3>
//             <p className="text-gray-600 text-sm mb-4">Add, edit, or remove products</p>
//             <a
//               href="/admin/products"
//               className="inline-block px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg font-medium text-sm"
//             >
//               Go to Products
//             </a>
//           </div>

//           <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer">
//             <h3 className="text-lg font-semibold text-gray-800 mb-2">View All Orders</h3>
//             <p className="text-gray-600 text-sm mb-4">Monitor and manage all orders</p>
//             <a
//               href="/admin/orders"
//               className="inline-block px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm"
//             >
//               Go to Orders
//             </a>
//           </div>

//           <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition cursor-pointer">
//             <h3 className="text-lg font-semibold text-gray-800 mb-2">Manage Agents</h3>
//             <p className="text-gray-600 text-sm mb-4">Assign deliveries and view performance</p>
//             <a
//               href="/admin/agents"
//               className="inline-block px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm"
//             >
//               Go to Agents
//             </a>
//           </div>
//         </div>
//       </div>
//     </AdminLayout>
//   );
// }




import React, { useState, useEffect } from 'react';
import { adminAPI } from '../../services/api';
import { AdminLayout } from '../../components/AdminLayout';
import toast from 'react-hot-toast';
import { format, subDays, startOfMonth, endOfMonth } from 'date-fns';
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import {
  Download, Filter, Calendar, TrendingUp, Users, Truck, 
  ShoppingCart, DollarSign, AlertCircle
} from 'lucide-react';
import jsPDF from 'jspdf';
import 'jspdf-autotable';

export function AdminDashboardPage() {
  // State Management
  const [dashboardStats, setDashboardStats] = useState(null);
  const [revenueReport, setRevenueReport] = useState(null);
  const [deliveryReport, setDeliveryReport] = useState(null);
  const [productReport, setProductReport] = useState(null);
  const [customerReport, setCustomerReport] = useState(null);
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');
  
  // Filter State
  const [dateRange, setDateRange] = useState({
    startDate: subDays(new Date(), 30),
    endDate: new Date()
  });
  const [reportDays, setReportDays] = useState(30);
  const [filters, setFilters] = useState({
    showRevenue: true,
    showDelivery: true,
    showProducts: true,
    showCustomers: true,
  });

  // Load all data
  useEffect(() => {
    loadAllData();
  }, [reportDays]);

  const loadAllData = async () => {
    setLoading(true);
    try {
      const [dashboard, revenue, delivery, product, customer] = await Promise.all([
        adminAPI.getDashboardStats(),
        adminAPI.getRevenueReport(reportDays),
        adminAPI.getDeliveryReport(reportDays),
        adminAPI.getProductReport(),
        adminAPI.getCustomerReport(),
      ]);

      setDashboardStats(dashboard.data);
      setRevenueReport(revenue.data);
      setDeliveryReport(delivery.data);
      setProductReport(product.data);
      setCustomerReport(customer.data);
    } catch (error) {
      toast.error('Failed to load dashboard data');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  // Export to CSV
  const exportToCSV = (data, filename) => {
    try {
      if (!data || data.length === 0) {
        toast.error('No data to export');
        return;
      }

      const headers = Object.keys(data[0]);
      const csv = [
        headers.join(','),
        ...data.map(row =>
          headers.map(header => {
            const value = row[header];
            if (typeof value === 'string' && value.includes(',')) {
              return `"${value}"`;
            }
            return value;
          }).join(',')
        )
      ].join('\n');

      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const link = document.createElement('a');
      const url = URL.createObjectURL(blob);
      link.setAttribute('href', url);
      link.setAttribute('download', `${filename}_${format(new Date(), 'yyyy-MM-dd')}.csv`);
      link.click();
      toast.success('CSV exported successfully');
    } catch (error) {
      toast.error('Failed to export CSV');
    }
  };

  // Export to PDF
  const exportToPDF = (title, data, columns = null) => {
    try {
      if (!data || (Array.isArray(data) && data.length === 0)) {
        toast.error('No data to export');
        return;
      }

      const pdf = new jsPDF();
      const pageWidth = pdf.internal.pageSize.getWidth();
      const pageHeight = pdf.internal.pageSize.getHeight();

      // Title
      pdf.setFontSize(16);
      pdf.text(title, 14, 15);
      pdf.setFontSize(10);
      pdf.text(`Generated on ${format(new Date(), 'MMM dd, yyyy HH:mm')}`, 14, 22);

      // Prepare table data
      let tableData = [];
      let colHeaders = [];

      if (Array.isArray(data)) {
        colHeaders = columns || Object.keys(data[0]);
        tableData = data.map(row =>
          colHeaders.map(col => {
            const value = row[col];
            if (typeof value === 'number') return value.toFixed(2);
            return value || '-';
          })
        );
      } else {
        // For single objects
        colHeaders = Object.keys(data);
        tableData = [[...Object.values(data).map(v => 
          typeof v === 'number' ? v.toFixed(2) : v
        )]];
      }

      pdf.autoTable({
        head: [colHeaders],
        body: tableData,
        startY: 28,
        headStyles: { fillColor: [66, 133, 244], textColor: [255, 255, 255] },
        alternateRowStyles: { fillColor: [245, 245, 245] },
        margin: { top: 28 },
      });

      pdf.save(`${title}_${format(new Date(), 'yyyy-MM-dd')}.pdf`);
      toast.success('PDF exported successfully');
    } catch (error) {
      toast.error('Failed to export PDF');
    }
  };

  if (loading) {
    return (
      <AdminLayout>
        <div className="flex justify-center items-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </AdminLayout>
    );
  }

  return (
    <AdminLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-start mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Admin Dashboard</h1>
            <p className="text-gray-600 mt-1">Complete business analytics and insights</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={loadAllData}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Refresh
            </button>
          </div>
        </div>

        {/* Date Range Selector */}
        <div className="bg-white rounded-lg shadow p-4">
          <div className="flex items-center gap-4 flex-wrap">
            <div className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-gray-600" />
              <select
                value={reportDays}
                onChange={(e) => setReportDays(parseInt(e.target.value))}
                className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value={7}>Last 7 days</option>
                <option value={14}>Last 14 days</option>
                <option value={30}>Last 30 days</option>
                <option value={60}>Last 60 days</option>
                <option value={90}>Last 90 days</option>
              </select>
            </div>
            
            <div className="flex items-center gap-2 ml-auto">
              <Filter className="w-5 h-5 text-gray-600" />
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.showRevenue}
                  onChange={(e) => setFilters({...filters, showRevenue: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm">Revenue</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={filters.showDelivery}
                  onChange={(e) => setFilters({...filters, showDelivery: e.target.checked})}
                  className="w-4 h-4"
                />
                <span className="text-sm">Delivery</span>
              </label>
            </div>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Total Customers */}
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-blue-600 text-sm font-medium">Total Customers</p>
                <p className="text-3xl font-bold text-blue-900 mt-2">
                  {dashboardStats?.total_customers || 0}
                </p>
              </div>
              <Users className="w-8 h-8 text-blue-400" />
            </div>
            <p className="text-xs text-blue-600 mt-2">All registered customers</p>
          </div>

          {/* Total Agents */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-green-600 text-sm font-medium">Active Agents</p>
                <p className="text-3xl font-bold text-green-900 mt-2">
                  {dashboardStats?.total_agents || 0}
                </p>
              </div>
              <Truck className="w-8 h-8 text-green-400" />
            </div>
            <p className="text-xs text-green-600 mt-2">Available for delivery</p>
          </div>

          {/* Today's Orders */}
          <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-lg p-6 shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-orange-600 text-sm font-medium">Today's Orders</p>
                <p className="text-3xl font-bold text-orange-900 mt-2">
                  {dashboardStats?.today_orders_count || 0}
                </p>
              </div>
              <ShoppingCart className="w-8 h-8 text-orange-400" />
            </div>
            <p className="text-xs text-orange-600 mt-2">Placed today</p>
          </div>

          {/* Today's Revenue */}
          <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 shadow">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-purple-600 text-sm font-medium">Today's Revenue</p>
                <p className="text-3xl font-bold text-purple-900 mt-2">
                  ₹{(dashboardStats?.today_revenue || 0).toFixed(0)}
                </p>
              </div>
              <DollarSign className="w-8 h-8 text-purple-400" />
            </div>
            <p className="text-xs text-purple-600 mt-2">Total revenue today</p>
          </div>
        </div>

        {/* Tabs */}
        <div className="border-b border-gray-200">
          <div className="flex gap-8 px-1">
            {['overview', 'revenue', 'delivery', 'products', 'customers'].map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`py-4 px-1 border-b-2 font-medium capitalize transition ${
                  activeTab === tab
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-600 hover:text-gray-900'
                }`}
              >
                {tab}
              </button>
            ))}
          </div>
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && dashboardStats && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Pending Status */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Pending Deliveries</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-4xl font-bold text-yellow-600">
                      {dashboardStats?.pending_deliveries || 0}
                    </p>
                    <p className="text-gray-600 text-sm mt-1">Awaiting assignment</p>
                  </div>
                  <AlertCircle className="w-12 h-12 text-yellow-400" />
                </div>
              </div>

              {/* Products Stock */}
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Total Products</h3>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-4xl font-bold text-blue-600">
                      {dashboardStats?.total_products || 0}
                    </p>
                    <p className="text-gray-600 text-sm mt-1">Active products</p>
                  </div>
                  <ShoppingCart className="w-12 h-12 text-blue-400" />
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Revenue Tab */}
        {activeTab === 'revenue' && revenueReport && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Revenue Analytics</h3>
                  <p className="text-gray-600 text-sm mt-1">
                    Last {reportDays} days - Total: ₹{(revenueReport?.total_revenue || 0).toFixed(2)}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => exportToCSV(revenueReport?.daily_breakdown, 'Revenue_Report')}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" /> CSV
                  </button>
                  <button
                    onClick={() => exportToPDF('Revenue Report', revenueReport?.daily_breakdown)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                  >
                    <Download className="w-4 h-4" /> PDF
                  </button>
                </div>
              </div>

              {/* Revenue Chart */}
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={revenueReport?.daily_breakdown || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                  />
                  <YAxis />
                  <Tooltip 
                    formatter={(value) => `₹${value?.toFixed(2)}`}
                    labelFormatter={(label) => `Date: ${label}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="amount" 
                    stroke="#3b82f6" 
                    dot={{ fill: '#3b82f6', r: 4 }}
                    strokeWidth={2}
                    name="Daily Revenue"
                  />
                </LineChart>
              </ResponsiveContainer>

              {/* Revenue Summary Table */}
              <div className="mt-6 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-gray-200">
                      <th className="text-left py-3 px-4 font-semibold">Date</th>
                      <th className="text-right py-3 px-4 font-semibold">Amount</th>
                      <th className="text-right py-3 px-4 font-semibold">Transactions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {(revenueReport?.daily_breakdown || []).slice(-10).reverse().map((item, idx) => (
                      <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                        <td className="py-3 px-4">{item.date}</td>
                        <td className="py-3 px-4 text-right font-semibold text-green-600">
                          ₹{item.amount?.toFixed(2)}
                        </td>
                        <td className="py-3 px-4 text-right">{item.transactions}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Delivery Tab */}
        {activeTab === 'delivery' && deliveryReport && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-center mb-6">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">Delivery Performance</h3>
                  <p className="text-gray-600 text-sm mt-1">
                    Last {reportDays} days - Success Rate: {(deliveryReport?.delivery_success_rate || 0).toFixed(1)}%
                  </p>
                </div>
                <button
                  onClick={() => exportToPDF('Delivery Report', deliveryReport)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                >
                  <Download className="w-4 h-4" /> PDF
                </button>
              </div>

              {/* Delivery Stats Cards */}
              <div className="grid grid-cols-3 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <p className="text-blue-600 text-sm">Total Deliveries</p>
                  <p className="text-2xl font-bold text-blue-900">
                    {deliveryReport?.total_deliveries || 0}
                  </p>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <p className="text-green-600 text-sm">Delivered</p>
                  <p className="text-2xl font-bold text-green-900">
                    {deliveryReport?.delivered_count || 0}
                  </p>
                </div>
                <div className="bg-red-50 rounded-lg p-4">
                  <p className="text-red-600 text-sm">Failed</p>
                  <p className="text-2xl font-bold text-red-900">
                    {deliveryReport?.failed_count || 0}
                  </p>
                </div>
              </div>

              {/* Success Rate Chart */}
              <ResponsiveContainer width="100%" height={250}>
                <PieChart>
                  <Pie
                    data={[
                      { name: 'Delivered', value: deliveryReport?.delivered_count || 0 },
                      { name: 'Failed', value: deliveryReport?.failed_count || 0 }
                    ]}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    <Cell fill="#10b981" />
                    <Cell fill="#ef4444" />
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>

              {/* Agent Performance Table */}
              <div className="mt-8">
                <h4 className="font-semibold text-gray-900 mb-4">Agent Performance</h4>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-gray-200">
                        <th className="text-left py-3 px-4 font-semibold">Agent ID</th>
                        <th className="text-right py-3 px-4 font-semibold">Delivered</th>
                        <th className="text-right py-3 px-4 font-semibold">Failed</th>
                        <th className="text-right py-3 px-4 font-semibold">Earnings</th>
                      </tr>
                    </thead>
                    <tbody>
                      {Object.entries(deliveryReport?.agent_performance || {}).map(([agentId, stats]) => (
                        <tr key={agentId} className="border-b border-gray-100 hover:bg-gray-50">
                          <td className="py-3 px-4">Agent #{agentId}</td>
                          <td className="py-3 px-4 text-right text-green-600 font-semibold">
                            {stats.delivered}
                          </td>
                          <td className="py-3 px-4 text-right text-red-600">
                            {stats.failed}
                          </td>
                          <td className="py-3 px-4 text-right font-semibold">
                            ₹{stats.earnings?.toFixed(2)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Products Tab */}
        {activeTab === 'products' && productReport && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Product Sales Analysis</h3>
                <p className="text-gray-600 text-sm mt-1">All-time product performance</p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => exportToCSV(productReport?.products, 'Product_Report')}
                  className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 flex items-center gap-2"
                >
                  <Download className="w-4 h-4" /> CSV
                </button>
                <button
                  onClick={() => exportToPDF('Product Report', productReport?.products)}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
                >
                  <Download className="w-4 h-4" /> PDF
                </button>
              </div>
            </div>

            {/* Product Chart */}
            <ResponsiveContainer width="100%" height={300}>
              <BarChart 
                data={(productReport?.products || [])
                  .sort((a, b) => b.total_sales_amount - a.total_sales_amount)
                  .slice(0, 10)}
              >
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis 
                  dataKey="name" 
                  angle={-45}
                  textAnchor="end"
                  height={100}
                  tick={{ fontSize: 12 }}
                />
                <YAxis />
                <Tooltip formatter={(value) => `₹${value?.toFixed(2)}`} />
                <Legend />
                <Bar dataKey="total_sales_amount" fill="#3b82f6" name="Sales Amount" />
              </BarChart>
            </ResponsiveContainer>

            {/* Products Table */}
            <div className="mt-6 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="text-left py-3 px-4 font-semibold">Product Name</th>
                    <th className="text-right py-3 px-4 font-semibold">Orders</th>
                    <th className="text-right py-3 px-4 font-semibold">Qty Sold</th>
                    <th className="text-right py-3 px-4 font-semibold">Revenue</th>
                  </tr>
                </thead>
                <tbody>
                  {(productReport?.products || []).map((product, idx) => (
                    <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4 font-medium">{product.name}</td>
                      <td className="py-3 px-4 text-right">{product.orders_count}</td>
                      <td className="py-3 px-4 text-right">{product.total_quantity_sold}</td>
                      <td className="py-3 px-4 text-right font-semibold text-green-600">
                        ₹{product.total_sales_amount?.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Customers Tab */}
        {activeTab === 'customers' && customerReport && (
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex justify-between items-center mb-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900">Customer Analytics</h3>
                <p className="text-gray-600 text-sm mt-1">Customer engagement and pending balances</p>
              </div>
              <button
                onClick={() => exportToPDF('Customer Report', customerReport)}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center gap-2"
              >
                <Download className="w-4 h-4" /> PDF
              </button>
            </div>

            {/* Customer Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 rounded-lg p-4">
                <p className="text-blue-600 text-sm">Total Customers</p>
                <p className="text-2xl font-bold text-blue-900 mt-1">
                  {customerReport?.total_customers || 0}
                </p>
              </div>
              <div className="bg-yellow-50 rounded-lg p-4">
                <p className="text-yellow-600 text-sm">Pending Balance</p>
                <p className="text-2xl font-bold text-yellow-900 mt-1">
                  {customerReport?.customers_with_pending_balance || 0}
                </p>
              </div>
              <div className="bg-red-50 rounded-lg p-4">
                <p className="text-red-600 text-sm">Total Pending</p>
                <p className="text-2xl font-bold text-red-900 mt-1">
                  ₹{(customerReport?.total_pending_amount || 0).toFixed(0)}
                </p>
              </div>
              <div className="bg-green-50 rounded-lg p-4">
                <p className="text-green-600 text-sm">Avg Pending/Customer</p>
                <p className="text-2xl font-bold text-green-900 mt-1">
                  ₹{(customerReport?.average_pending_per_customer || 0).toFixed(0)}
                </p>
              </div>
            </div>

            {/* Distribution Chart */}
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={[
                    { 
                      name: 'With Pending Balance', 
                      value: customerReport?.customers_with_pending_balance || 0 
                    },
                    { 
                      name: 'Paid Up', 
                      value: (customerReport?.total_customers || 0) - (customerReport?.customers_with_pending_balance || 0)
                    }
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell fill="#f59e0b" />
                  <Cell fill="#10b981" />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}