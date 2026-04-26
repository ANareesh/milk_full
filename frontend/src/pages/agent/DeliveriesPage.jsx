// /**
//  * Agent Deliveries Management Page
//  */

// import React, { useState, useEffect } from 'react';
// import { deliveryAPI } from '../../services/api';
// import toast from 'react-hot-toast';
// import { AgentLayout } from '../../components/AgentLayout';
// import { formatDate } from '../../utils/date';

// export function AgentDeliveriesPage() {
//   const [deliveries, setDeliveries] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [selectedDelivery, setSelectedDelivery] = useState(null);
//   const [otpForm, setOtpForm] = useState({ otp: '' });
//   const [viewOtpForm, setViewOtpForm] = useState(false);

//   useEffect(() => {
//     loadDeliveries();
//     // Refresh every 30 seconds
//     const interval = setInterval(loadDeliveries, 30000);
//     return () => clearInterval(interval);
//   }, []);

//   const loadDeliveries = async () => {
//     try {
//       setLoading(true);
//       console.log('Fetching deliveries...');
//       const response = await deliveryAPI.getMyDeliveries();
//       console.log('Response:', response.data);
//       setDeliveries(response.data);
//     } catch (error) {
//       console.error('Error details:', error);
//       toast.error('Failed to load deliveries');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleStartDelivery = async (deliveryId) => {
//     try {
//       await deliveryAPI.start(deliveryId);
//       toast.success('Delivery started');
//       loadDeliveries();
//     } catch (error) {
//       toast.error('Failed to start delivery');
//     }
//   };

//   const handleCompleteDelivery = async (deliveryId) => {
//     setSelectedDelivery(deliveryId);
//     setViewOtpForm(true);
//   };

//   const handleVerifyOtp = async () => {
//     if (!otpForm.otp) {
//       toast.error('Please enter OTP');
//       return;
//     }

//     try {
//       await deliveryAPI.verifyOtp(selectedDelivery, { otp: otpForm.otp });
//       toast.success('Delivery marked as complete');
//       setViewOtpForm(false);
//       setOtpForm({ otp: '' });
//       loadDeliveries();
//     } catch (error) {
//       toast.error('Invalid OTP');
//     }
//   };

//   const handleFailDelivery = async (deliveryId) => {
//     const reason = prompt('Enter reason for delivery failure:');
//     if (!reason) return;

//     try {
//       await deliveryAPI.fail(deliveryId, { reason });
//       toast.success('Delivery marked as failed');
//       loadDeliveries();
//     } catch (error) {
//       toast.error('Failed to update delivery');
//     }
//   };

//   const getStatusBadge = (status) => {
//     const colors = {
//       pending: 'bg-yellow-100 text-yellow-800',
//       in_progress: 'bg-purple-100 text-purple-800',
//       delivered: 'bg-green-100 text-green-800',
//       failed: 'bg-red-100 text-red-800',
//     };
//     return colors[status] || 'bg-gray-100 text-gray-800';
//   };

//   if (loading) {
//     return (
//       <AgentLayout>
//         <div className="flex justify-center items-center h-64">Loading...</div>
//       </AgentLayout>
//     );
//   }

//   return (
//     <AgentLayout>
//       <div className="space-y-6">
//         <h1 className="text-3xl font-bold text-gray-800">My Deliveries</h1>

//         {deliveries.length === 0 ? (
//           <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
//             <p className="text-gray-600">No deliveries assigned. Check back later!</p>
//           </div>
//         ) : (
//           <div className="space-y-4">
//             {deliveries.map((delivery) => (
//               <div key={delivery.id} className="bg-white rounded-lg shadow-md p-6">
//                 <div className="flex justify-between items-start mb-4">
//                   <div>
//                     <h3 className="text-lg font-semibold">Order #{delivery.order_number}</h3>
//                     <p className="text-gray-600 text-sm">
//                       Assigned to: {delivery.agent_name || 'N/A'}
//                     </p>
//                   </div>
//                   <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(delivery.status)}`}>
//                     {delivery.status.replace('_', ' ').toUpperCase()}
//                   </span>
//                 </div>

//                 <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
//                   <div>
//                     <p className="text-gray-600 text-sm">Customer</p>
//                     <p className="font-semibold">{delivery.customer_id ? 'Customer #' + delivery.customer_id : 'N/A'}</p>
//                   </div>
//                   <div>
//                     <p className="text-gray-600 text-sm">Delivery Date</p>
//                     <p className="font-semibold">{formatDate(delivery.actual_delivery_date)}</p>
//                   </div>
//                   <div>
//                     <p className="text-gray-600 text-sm">Amount</p>
//                     <p className="font-semibold text-green-600">₹{delivery.total_amount || '0.00'}</p>
//                   </div>
//                   <div>
//                     <p className="text-gray-600 text-sm">Notes</p>
//                     <p className="font-semibold text-sm">{delivery.delivery_notes || 'No notes'}</p>
//                   </div>
//                 </div>

//                 <div className="flex gap-2 flex-wrap">
//                   {delivery.status === 'pending' && (
//                     <button
//                       onClick={() => handleStartDelivery(delivery.id)}
//                       className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm"
//                     >
//                       Start Delivery
//                     </button>
//                   )}

//                   {delivery.status === 'in_progress' && (
//                     <>
//                       <button
//                         onClick={() => handleCompleteDelivery(delivery.id)}
//                         className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm"
//                       >
//                         Mark as Complete
//                       </button>
//                       <button
//                         onClick={() => handleFailDelivery(delivery.id)}
//                         className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm"
//                       >
//                         Mark as Failed
//                       </button>
//                     </>
//                   )}
//                 </div>
//               </div>
//             ))}
//           </div>
//         )}

//         {/* OTP Verification Modal */}
//         {viewOtpForm && selectedDelivery && (
//           <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
//             <div className="bg-white rounded-lg p-8 max-w-md w-full">
//               <h2 className="text-2xl font-bold text-gray-800 mb-4">Verify Customer OTP</h2>

//               <div className="space-y-4">
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Enter OTP from Customer
//                   </label>
//                   <input
//                     type="text"
//                     value={otpForm.otp}
//                     onChange={(e) => setOtpForm({ otp: e.target.value })}
//                     className="w-full px-4 py-2 border border-gray-300 rounded-lg text-center text-2xl tracking-widest"
//                     placeholder="000000"
//                     maxLength="6"
//                   />
//                 </div>

//                 <p className="text-gray-600 text-sm">
//                   Ask the customer for the OTP sent to their phone
//                 </p>

//                 <div className="flex gap-2">
//                   <button
//                     onClick={handleVerifyOtp}
//                     className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//                   >
//                     Verify & Complete
//                   </button>
//                   <button
//                     onClick={() => {
//                       setViewOtpForm(false);
//                       setOtpForm({ otp: '' });
//                     }}
//                     className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
//                   >
//                     Cancel
//                   </button>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}
//       </div>
//     </AgentLayout>
//   );
// }

/**
 * Agent Deliveries Management Page
 */

import React, { useState, useEffect } from 'react';
import { deliveryAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { AgentLayout } from '../../components/AgentLayout';
import { formatDate } from '../../utils/date';

export function AgentDeliveriesPage() {
  const [deliveries, setDeliveries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDelivery, setSelectedDelivery] = useState(null);
  const [otpForm, setOtpForm] = useState({ otp: '' });
  const [viewOtpForm, setViewOtpForm] = useState(false);

  useEffect(() => {
    loadDeliveries();
    // Refresh every 30 seconds
    const interval = setInterval(loadDeliveries, 30000);
    return () => clearInterval(interval);
  }, []);

  const loadDeliveries = async () => {
    try {
      setLoading(true);
      console.log('Fetching deliveries...');
      const response = await deliveryAPI.getMyDeliveries();
      console.log('Response:', response.data);
      setDeliveries(response.data);
    } catch (error) {
      console.error('Error details:', error);
      toast.error('Failed to load deliveries');
    } finally {
      setLoading(false);
    }
  };

  const handleStartDelivery = async (deliveryId) => {
    try {
      await deliveryAPI.start(deliveryId);
      toast.success('Delivery started');
      loadDeliveries();
    } catch (error) {
      toast.error('Failed to start delivery');
    }
  };

  const handleCompleteDelivery = (delivery) => {
    // Store the full delivery object to access OTP
    setSelectedDelivery(delivery);
    setViewOtpForm(true);
  };

  const handleVerifyOtp = async () => {
    if (!otpForm.otp) {
      toast.error('Please enter OTP');
      return;
    }

    try {
      // Use selectedDelivery.id since it's now an object
      await deliveryAPI.verifyOtp(selectedDelivery.id, { otp: otpForm.otp });
      toast.success('Delivery marked as complete');
      setViewOtpForm(false);
      setOtpForm({ otp: '' });
      setSelectedDelivery(null);
      loadDeliveries();
    } catch (error) {
      toast.error('Invalid OTP');
    }
  };

  const handleFailDelivery = async (deliveryId) => {
    const reason = prompt('Enter reason for delivery failure:');
    if (!reason) return;

    try {
      await deliveryAPI.fail(deliveryId, { reason });
      toast.success('Delivery marked as failed');
      loadDeliveries();
    } catch (error) {
      toast.error('Failed to update delivery');
    }
  };

  const getStatusBadge = (status) => {
    const colors = {
      pending: 'bg-yellow-100 text-yellow-800',
      in_progress: 'bg-purple-100 text-purple-800',
      delivered: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    };
    return colors[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) {
    return (
      <AgentLayout>
        <div className="flex justify-center items-center h-64">Loading...</div>
      </AgentLayout>
    );
  }

  return (
    <AgentLayout>
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-gray-800">My Deliveries</h1>

        {deliveries.length === 0 ? (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
            <p className="text-gray-600">No deliveries assigned. Check back later!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {deliveries.map((delivery) => (
              <div key={delivery.id} className="bg-white rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">Order #{delivery.order_number}</h3>
                    <p className="text-gray-600 text-sm">
                      Assigned to: {delivery.agent_name || 'N/A'}
                    </p>
                  </div>
                  <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadge(delivery.status)}`}>
                    {delivery.status.replace('_', ' ').toUpperCase()}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                  <div>
                    <p className="text-gray-600 text-sm">Customer</p>
                    <p className="font-semibold">{delivery.customer_id ? 'Customer #' + delivery.customer_id : 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Delivery Date</p>
                    <p className="font-semibold">{formatDate(delivery.actual_delivery_date)}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Amount</p>
                    <p className="font-semibold text-green-600">₹{delivery.total_amount || '0.00'}</p>
                  </div>
                  <div>
                    <p className="text-gray-600 text-sm">Notes</p>
                    <p className="font-semibold text-sm">{delivery.delivery_notes || 'No notes'}</p>
                  </div>
                </div>

                <div className="flex gap-2 flex-wrap">
                  {delivery.status === 'pending' && (
                    <button
                      onClick={() => handleStartDelivery(delivery.id)}
                      className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium text-sm"
                    >
                      Start Delivery
                    </button>
                  )}

                  {delivery.status === 'in_progress' && (
                    <>
                      <button
                        onClick={() => handleCompleteDelivery(delivery)}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm"
                      >
                        Mark as Complete
                      </button>
                      <button
                        onClick={() => handleFailDelivery(delivery.id)}
                        className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg font-medium text-sm"
                      >
                        Mark as Failed
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* OTP Verification Modal */}
        {viewOtpForm && selectedDelivery && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">Verify Delivery OTP</h2>

              <div className="space-y-4">
                {/* Display the system-generated OTP */}
                <div className="bg-blue-50 border border-blue-300 rounded-lg p-4 mb-4">
                  <p className="text-sm text-gray-600 mb-2">System Generated OTP:</p>
                  <p className="text-3xl font-bold text-blue-600 text-center font-mono tracking-widest">
                    {selectedDelivery.delivery_otp}
                  </p>
                  <p className="text-xs text-gray-500 text-center mt-2">Share this with customer or verify their OTP</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Enter OTP from Customer
                  </label>
                  <input
                    type="text"
                    value={otpForm.otp}
                    onChange={(e) => setOtpForm({ otp: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg text-center text-2xl tracking-widest"
                    placeholder="000000"
                    maxLength="6"
                  />
                </div>

                <p className="text-gray-600 text-sm text-center">
                  Confirm the OTP matches the one shown above
                </p>

                <div className="flex gap-2">
                  <button
                    onClick={handleVerifyOtp}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                  >
                    Verify & Complete
                  </button>
                  <button
                    onClick={() => {
                      setViewOtpForm(false);
                      setOtpForm({ otp: '' });
                      setSelectedDelivery(null);
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
    </AgentLayout>
  );
}