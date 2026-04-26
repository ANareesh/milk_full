// /**
//  * Admin Deliveries Management Page
//  */

// import React, { useState, useEffect } from 'react';
// import { deliveryAPI, agentAPI } from '../../services/api';
// import toast from 'react-hot-toast';
// import { AdminLayout } from '../../components/AdminLayout';
// import { formatDate } from '../../utils/date';

// export function AdminDeliveriesPage() {
//   const [deliveries, setDeliveries] = useState([]);
//   const [agents, setAgents] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [filterStatus, setFilterStatus] = useState('pending');
//   const [showAssignModal, setShowAssignModal] = useState(false);
//   const [selectedDelivery, setSelectedDelivery] = useState(null);
//   const [selectedAgentId, setSelectedAgentId] = useState('');

//   useEffect(() => {
//     loadDeliveries();
//     loadAgents();
//   }, []);
//   const loadDeliveries = async () => {
//   try {
//     setLoading(true);
//     const response = filterStatus === 'pending' 
//       ? await deliveryAPI.getPending()
//       : await deliveryAPI.getAll();  // Don't pass 'all' parameter
//     setDeliveries(response.data);
//   } catch (error) {
//     toast.error('Failed to load deliveries');
//   } finally {
//     setLoading(false);
//   }
// };

// //   const loadDeliveries = async () => {
// //     try {
// //       setLoading(true);
// //       const endpoint = filterStatus === 'pending' 
// //         ? deliveryAPI.getPending()
// //         : deliveryAPI.getAll(filterStatus);
// //       const response = await endpoint;
// //       setDeliveries(response.data);
// //     } catch (error) {
// //       toast.error('Failed to load deliveries');
// //     } finally {
// //       setLoading(false);
// //     }
// //   };

//   const loadAgents = async () => {
//     try {
//       const response = await agentAPI.getAvailable();
//       setAgents(response.data);
//     } catch (error) {
//       console.error('Failed to load agents');
//     }
//   };

//   const handleAssignClick = (delivery) => {
//     setSelectedDelivery(delivery);
//     setSelectedAgentId('');
//     setShowAssignModal(true);
//   };

//   const handleAssignAgent = async () => {
//     if (!selectedAgentId) {
//       toast.error('Please select an agent');
//       return;
//     }

//     if (!window.confirm('Assign this agent to the delivery?')) return;

//     try {
//       await deliveryAPI.assignAgent(selectedDelivery.id, parseInt(selectedAgentId));
//       toast.success('Agent assigned successfully');
//       setShowAssignModal(false);
//       loadDeliveries();
//     } catch (error) {
//       toast.error(error.response?.data?.detail || 'Failed to assign agent');
//     }
//   };
  

//   if (loading) {
//     return (
//       <AdminLayout>
//         <div className="flex justify-center items-center h-64">Loading...</div>
//       </AdminLayout>
//     );
//   }

//   return (
//     <AdminLayout>
//       <div className="space-y-6">
//         <h1 className="text-3xl font-bold text-gray-800">Deliveries Management</h1>

//         <div className="flex gap-2 flex-wrap">
//           <button
//             onClick={() => {
//               setFilterStatus('pending');
//               loadDeliveries();
//             }}
//             className={`px-4 py-2 rounded-lg font-medium ${
//               filterStatus === 'pending' 
//                 ? 'bg-green-600 text-white' 
//                 : 'bg-white text-gray-700 border border-gray-300'
//             }`}
//           >
//             Pending ({deliveries.filter(d => !d.agent_id).length})
//           </button>
//           <button
//             onClick={() => {
//               setFilterStatus('all');
//               loadDeliveries();
//             }}
//             className={`px-4 py-2 rounded-lg font-medium ${
//               filterStatus === 'all' 
//                 ? 'bg-green-600 text-white' 
//                 : 'bg-white text-gray-700 border border-gray-300'
//             }`}
//           >
//             All ({filteredDeliveries.length})
//           </button>
//         </div>

//         {filteredDeliveries.length === 0 ? (
//           <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
//             <p className="text-gray-600">No deliveries to show</p>
//           </div>
//         ) : (
//           <div className="bg-white rounded-lg shadow-lg overflow-x-auto">
//             <table className="min-w-full">
//               <thead className="bg-gray-100">
//                 <tr>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Order #</th>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Customer</th>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Amount</th>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Delivery Date</th>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Assigned Agent</th>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
//                   <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
//                 </tr>
//               </thead>
//               <tbody className="divide-y">
//                 {filteredDeliveries.map((delivery) => (
//                   <tr key={delivery.id} className="hover:bg-gray-50">
//                     <td className="px-6 py-4 text-sm font-semibold text-gray-900">
//                       {delivery.order_number || `Order #${delivery.order_id}`}
//                     </td>
//                     <td className="px-6 py-4 text-sm text-gray-900">
//                       Customer #{delivery.customer_id}
//                     </td>
//                     <td className="px-6 py-4 text-sm font-semibold text-green-600">
//                       ₹{delivery.total_amount || '-'}
//                     </td>
//                     <td className="px-6 py-4 text-sm text-gray-900">
//                       {formatDate(delivery.scheduled_date)}
//                     </td>
//                     <td className="px-6 py-4 text-sm text-gray-900">
//                       {delivery.agent_name || (
//                         <span className="text-red-600 font-medium">Unassigned</span>
//                       )}
//                     </td>
//                     <td className="px-6 py-4 text-sm">
//                       <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
//                         {delivery.status.replace('_', ' ').toUpperCase()}
//                       </span>
//                     </td>
//                     <td className="px-6 py-4 text-sm flex gap-2">
//                       {!delivery.agent_id && (
//                         <button
//                           onClick={() => handleAssignClick(delivery)}
//                           className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium"
//                         >
//                           Assign Agent
//                         </button>
//                       )}
//                     </td>
//                   </tr>
//                 ))}
//               </tbody>
//             </table>
//           </div>
//         )}

//         {/* Assign Agent Modal */}
//         {showAssignModal && selectedDelivery && (
//           <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
//             <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
//               <h2 className="text-xl font-bold text-gray-800 mb-4">
//                 Assign Agent to Order {selectedDelivery.order_number}
//               </h2>
              
//               <div className="space-y-4">
//                 <div>
//                   <p className="text-sm text-gray-600 mb-2">
//                     Delivery Date: {formatDate(selectedDelivery.scheduled_date)}
//                   </p>
//                   <p className="text-sm text-gray-600">
//                     Amount: ₹{selectedDelivery.total_amount}
//                   </p>
//                 </div>

//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Select Agent *
//                   </label>
//                   <select
//                     value={selectedAgentId}
//                     onChange={(e) => setSelectedAgentId(e.target.value)}
//                     className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
//                   >
//                     <option value="">-- Choose an agent --</option>
//                     {agents.map((agent) => (
//                       <option key={agent.id} value={agent.id}>
//                         {agent.user?.full_name || agent.user?.username} ({agent.status})
//                       </option>
//                     ))}
//                   </select>
//                 </div>

//                 <div className="flex gap-3">
//                   <button
//                     onClick={() => setShowAssignModal(false)}
//                     className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
//                   >
//                     Cancel
//                   </button>
//                   <button
//                     onClick={handleAssignAgent}
//                     className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//                   >
//                     Assign
//                   </button>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </AdminLayout>
//   );
// }






/**
 * Admin Deliveries Management Page
 */

import React, { useState, useEffect } from 'react';
import { deliveryAPI, agentAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AdminLayout } from '../../components/AdminLayout';
import { formatDate } from '../../utils/date';

export function AdminDeliveriesPage() {
  const [deliveries, setDeliveries] = useState([]);
  const [agents, setAgents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filterStatus, setFilterStatus] = useState('pending');
  const [showAssignModal, setShowAssignModal] = useState(false);
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [selectedAgentId, setSelectedAgentId] = useState('');

  // Load deliveries and agents when component mounts
  useEffect(() => {
    loadDeliveries();
    loadAgents();
  }, [filterStatus]); // Re-run when filterStatus changes

  const loadDeliveries = async () => {
    try {
      setLoading(true);
      let response;
      if (filterStatus === 'pending') {
        response = await deliveryAPI.getPending();
      } else {
        response = await deliveryAPI.getAll();
      }
      setDeliveries(response.data);
    } catch (error) {
      toast.error('Failed to load deliveries');
      console.error('Error loading deliveries:', error);
    } finally {
      setLoading(false);
    }
  };
  const loadAgents = async () => {
  try {
    // Change from getAll() to getAvailable() to show only available agents
    const response = await agentAPI.getAvailable();
    setAgents(response.data);
  } catch (error) {
    toast.error('Failed to load agents');
  }
};
  // const loadAgents = async () => {
  //   try {
  //     const response = await agentAPI.getAll(); // Changed to getAll() to show all agents
  //     setAgents(response.data);
  //   } catch (error) {
  //     toast.error('Failed to load agents');
  //     console.error('Error loading agents:', error);
  //   }
  // };

  // Filter deliveries based on selected status
  const filteredDeliveries = filterStatus === 'pending' 
    ? deliveries.filter(d => !d.agent_id)
    : deliveries;

  const handleAssignClick = (delivery) => {
    setSelectedDelivery(delivery);
    setSelectedAgentId('');
    setShowAssignModal(true);
  };

  const handleAssignAgent = async () => {
    if (!selectedAgentId) {
      toast.error('Please select an agent');
      return;
    }

    if (!window.confirm('Assign this agent to the delivery?')) return;

    try {
      await deliveryAPI.assignAgent(selectedDelivery.id, parseInt(selectedAgentId));
      toast.success('Agent assigned successfully');
      setShowAssignModal(false);
      setFilterStatus('all');
      loadDeliveries();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to assign agent');
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
        <h1 className="text-3xl font-bold text-gray-800">Deliveries Management</h1>

        <div className="flex gap-2 flex-wrap">
          <button
            onClick={() => setFilterStatus('pending')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filterStatus === 'pending' 
                ? 'bg-green-600 text-white' 
                : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            Pending ({deliveries.filter(d => !d.agent_id).length})
          </button>
          <button
            onClick={() => setFilterStatus('all')}
            className={`px-4 py-2 rounded-lg font-medium ${
              filterStatus === 'all' 
                ? 'bg-green-600 text-white' 
                : 'bg-white text-gray-700 border border-gray-300'
            }`}
          >
            All ({deliveries.length})
          </button>
        </div>

        {filteredDeliveries.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No deliveries to show</p>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow-lg overflow-x-auto">
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Order #</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Customer</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Amount</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Delivery Date</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Assigned Agent</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y">
                {filteredDeliveries.map((delivery) => (
                  <tr key={delivery.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-semibold text-gray-900">
                      {delivery.order_number || `Order #${delivery.order_id}`}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      Customer #{delivery.customer_id}
                    </td>
                    <td className="px-6 py-4 text-sm font-semibold text-green-600">
                      ₹{delivery.total_amount || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {formatDate(delivery.scheduled_date)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-900">
                      {delivery.agent_name || (
                        <span className="text-red-600 font-medium">Unassigned</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-sm">
                      <span className="px-3 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {delivery.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm flex gap-2">
                      {!delivery.agent_id && (
                        <button
                          onClick={() => handleAssignClick(delivery)}
                          className="px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium"
                        >
                          Assign Agent
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Assign Agent Modal */}
        {showAssignModal && selectedDelivery && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h2 className="text-xl font-bold text-gray-800 mb-4">
                Assign Agent to Order {selectedDelivery.order_number}
              </h2>
              
              <div className="space-y-4">
                <div>
                  <p className="text-sm text-gray-600 mb-2">
                    Delivery Date: {formatDate(selectedDelivery.scheduled_date)}
                  </p>
                  <p className="text-sm text-gray-600">
                    Amount: ₹{selectedDelivery.total_amount}
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Select Agent *
                  </label>
                  <select
                    value={selectedAgentId}
                    onChange={(e) => setSelectedAgentId(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="">-- Choose an agent --</option>
                    {agents.map((agent) => (
                      <option key={agent.id} value={agent.id}>
                        {agent.user?.full_name || agent.user?.username || `Agent #${agent.id}`} ({agent.status})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={() => setShowAssignModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 font-medium"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAssignAgent}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                  >
                    Assign
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </AdminLayout>
  );
}