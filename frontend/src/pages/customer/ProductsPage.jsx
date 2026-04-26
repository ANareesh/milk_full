// /**
//  * Customer Products Browsing Page
//  */

// import React, { useState, useEffect } from 'react';
// import { productAPI, orderAPI } from '../../services/api';
// import toast from 'react-hot-toast';
// import { CustomerLayout } from '../../components/CustomerLayout';
// import { useNavigate } from 'react-router-dom';

// export function CustomerProductsPage() {
//   const [products, setProducts] = useState([]);
//   const navigate = useNavigate();
//   const [loading, setLoading] = useState(true);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [selectedProduct, setSelectedProduct] = useState(null);
//   const [quantity, setQuantity] = useState(1);
//   const [deliveryDate, setDeliveryDate] = useState('');
  

//   useEffect(() => {
//     loadProducts();
//   }, []);

//   const loadProducts = async () => {
//     try {
//       setLoading(true);
//       const response = await productAPI.list();
//       setProducts(response.data);
//     } catch (error) {
//       toast.error('Failed to load products');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleSearch = async (e) => {
//     e.preventDefault();
//     if (!searchQuery.trim()) {
//       loadProducts();
//       return;
//     }

//     try {
//       const response = await productAPI.search(searchQuery);
//       setProducts(response.data);
//     } catch (error) {
//       toast.error('Search failed');
//     }
//   };

//   const handlePlaceOrder = async () => {
//     if (!selectedProduct || !quantity || !deliveryDate) {
//       toast.error('Please fill all fields');
//       return;
//     }
//     const deliveryAddress = localStorage.getItem('selectedLocation');
  
//     if (!deliveryAddress) {
//       toast.error('Please select a delivery location');
//       return;
//     }

//     try {
//       await orderAPI.create({
//         product_id: selectedProduct.id,
//         quantity: parseFloat(quantity),
//         delivery_date: new Date(deliveryDate).toISOString(),
//         delivery_address: deliveryAddress,
//       });
//       toast.success('Order placed successfully!');
//       setSelectedProduct(null);
//       setQuantity(1);
//       setDeliveryDate('');
//     } catch (error) {
//       toast.error(error.response?.data?.detail || 'Failed to place order');
//     }
//   };

//   if (loading) {
//     return (
//       <CustomerLayout>
//         <div className="flex justify-center items-center h-64">Loading...</div>
//       </CustomerLayout>
//     );
//   }

//   return (
//     <CustomerLayout>
//       <div className="space-y-6">
//         {/* Search Bar */}
//         <form onSubmit={handleSearch} className="flex gap-2">
//           <input
//             type="text"
//             placeholder="Search milk products..."
//             value={searchQuery}
//             onChange={(e) => setSearchQuery(e.target.value)}
//             className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
//           />
//           <button
//             type="submit"
//             className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//           >
//             Search
//           </button>
//         </form>

//         {/* Products Grid */}
//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//           {products.map((product) => (
//             <div
//               key={product.id}
//               className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
//             >
//               {product.image_url && (
//                 <img
//                   src={`http://localhost:8000${product.image_url}`}
//                   alt={product.name}
//                   className="w-full h-40 object-cover rounded mb-4"
//                 />
//               )}
//               <h3 className="text-lg font-semibold text-gray-800">{product.name}</h3>
//               <p className="text-gray-600 text-sm mb-2">{product.description}</p>
//               <p className="text-green-600 font-bold text-lg mb-4">
//                 ₹{product.unit_price}/{product.unit}
//               </p>
//               <p className="text-sm text-gray-600 mb-4">
//                 Stock: {product.available_quantity} {product.unit}
//               </p>
//               <div className="flex gap-2">
//                 <button
//                   onClick={() => navigate(`/customer/products/${product.id}`)}
//                   disabled={product.available_quantity === 0}
//                   className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm"
//                 >
//                   View Details
//                 </button>
//                 <button
//                   onClick={() => setSelectedProduct(product)}
//                   disabled={product.available_quantity === 0}
//                   className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm"
//                 >
//                   Order Now
//                 </button>
//               </div>
//               {/* <button
//                 onClick={() => setSelectedProduct(product)}
//                 className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//               >
//                 Order Now
//               </button> */}
//             </div>
//           ))}
//         </div>

//         {/* Order Modal */}
//         {selectedProduct && (
//           <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
//             <div className="bg-white rounded-lg p-8 max-w-md w-full">
//               <h2 className="text-2xl font-bold text-gray-800 mb-4">
//                 Order {selectedProduct.name}
//               </h2>

//               <div className="space-y-4">
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Quantity ({selectedProduct.unit})
//                   </label>
//                   <input
//                     type="number"
//                     min="0.5"
//                     step="0.5"
//                     value={quantity}
//                     onChange={(e) => setQuantity(e.target.value)}
//                     className="w-full px-4 py-2 border border-gray-300 rounded-lg"
//                   />
//                 </div>

//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Delivery Date
//                   </label>
//                   <input
//                     type="datetime-local"
//                     value={deliveryDate}
//                     onChange={(e) => setDeliveryDate(e.target.value)}
//                     className="w-full px-4 py-2 border border-gray-300 rounded-lg"
//                   />
//                 </div>

//                 <div className="bg-gray-100 p-4 rounded">
//                   <p className="text-gray-600">
//                     Total: ₹
//                     {(selectedProduct.unit_price * quantity).toFixed(2)}
//                   </p>
//                 </div>

//                 <div className="flex gap-2">
//                   <button
//                     onClick={handlePlaceOrder}
//                     className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//                   >
//                     Place Order
//                   </button>
//                   <button
//                     onClick={() => setSelectedProduct(null)}
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
//     </CustomerLayout>
//   );
// }


/**
 * Customer Products Browsing Page
 */

import React, { useState, useEffect } from 'react';
import { productAPI, orderAPI } from '../../services/api';
import toast from 'react-hot-toast';
import { CustomerLayout } from '../../components/CustomerLayout';
import { useNavigate } from 'react-router-dom';

export function CustomerProductsPage() {
  const [products, setProducts] = useState([]);
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [quantity, setQuantity] = useState(1);
  const [deliveryDate, setDeliveryDate] = useState('');
  
  // Location states
  const [showLocationModal, setShowLocationModal] = useState(
    !localStorage.getItem('selectedLocation')
  );
  const [selectedLocation, setSelectedLocation] = useState(
    localStorage.getItem('selectedLocation') || ''
  );

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

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) {
      loadProducts();
      return;
    }

    try {
      const response = await productAPI.search(searchQuery);
      setProducts(response.data);
    } catch (error) {
      toast.error('Search failed');
    }
  };

  // Location handler
  const handleLocationSelect = (city) => {
    setSelectedLocation(city);
    localStorage.setItem('selectedLocation', city);
    setShowLocationModal(false);
    toast.success(`Location set to ${city}`);
  };

  const handlePlaceOrder = async () => {
    if (!selectedProduct || !quantity || !deliveryDate) {
      toast.error('Please fill all fields');
      return;
    }
    const deliveryAddress = localStorage.getItem('selectedLocation');
  
    if (!deliveryAddress) {
      toast.error('Please select a delivery location');
      return;
    }

    try {
      await orderAPI.create({
        product_id: selectedProduct.id,
        quantity: parseFloat(quantity),
        delivery_date: new Date(deliveryDate).toISOString(),
        delivery_address: deliveryAddress,
      });
      toast.success('Order placed successfully!');
      setSelectedProduct(null);
      setQuantity(1);
      setDeliveryDate('');
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Failed to place order');
    }
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
        {/* Location Display Banner */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex justify-between items-center">
            <div>
              <p className="text-sm text-gray-600">Delivery Location:</p>
              <p className="text-lg font-bold text-blue-600">
                {selectedLocation || 'Not Selected'}
              </p>
            </div>
            <button
              onClick={() => setShowLocationModal(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
            >
              Change Location
            </button>
          </div>
        </div>

        {/* Search Bar */}
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            placeholder="Search milk products..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          />
          <button
            type="submit"
            className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
          >
            Search
          </button>
        </form>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <div
              key={product.id}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
            >
              {product.image_url && (
                <img
                  src={`http://localhost:8000${product.image_url}`}
                  alt={product.name}
                  className="w-full h-40 object-cover rounded mb-4"
                />
              )}
              <h3 className="text-lg font-semibold text-gray-800">{product.name}</h3>
              <p className="text-gray-600 text-sm mb-2">{product.description}</p>
              <p className="text-green-600 font-bold text-lg mb-4">
                ₹{product.unit_price}/{product.unit}
              </p>
              <p className="text-sm text-gray-600 mb-4">
                Stock: {product.available_quantity} {product.unit}
              </p>
              <div className="flex gap-2">
                <button
                  onClick={() => navigate(`/customer/products/${product.id}`)}
                  disabled={product.available_quantity === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm"
                >
                  View Details
                </button>
                <button
                  onClick={() => setSelectedProduct(product)}
                  disabled={product.available_quantity === 0}
                  className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm"
                >
                  Order Now
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Order Modal */}
        {selectedProduct && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Order {selectedProduct.name}
              </h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quantity ({selectedProduct.unit})
                  </label>
                  <input
                    type="number"
                    min="0.5"
                    step="0.5"
                    value={quantity}
                    onChange={(e) => setQuantity(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Delivery Date
                  </label>
                  <input
                    type="datetime-local"
                    value={deliveryDate}
                    onChange={(e) => setDeliveryDate(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  />
                </div>

                <div className="bg-gray-100 p-4 rounded">
                  <p className="text-gray-600">
                    Total: ₹
                    {(selectedProduct.unit_price * quantity).toFixed(2)}
                  </p>
                </div>

                <div className="flex gap-2">
                  <button
                    onClick={handlePlaceOrder}
                    className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
                  >
                    Place Order
                  </button>
                  <button
                    onClick={() => setSelectedProduct(null)}
                    className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Location Selector Modal */}
        {showLocationModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full max-h-96 overflow-y-auto">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">Select Delivery Location</h2>
              
              {/* Popular Cities */}
              <div className="mb-6">
                <h3 className="font-semibold text-gray-700 mb-3">Popular Cities</h3>
                <div className="grid grid-cols-2 gap-2">
                  {['Bangalore', 'Chandigarh', 'Chennai', 'Delhi NCR', 'Hyderabad', 'Jaipur', 'Mumbai', 'Pune'].map((city) => (
                    <button
                      key={city}
                      onClick={() => handleLocationSelect(city)}
                      className="px-4 py-2 border border-gray-300 hover:bg-blue-50 hover:border-blue-500 rounded-lg text-sm font-medium text-gray-700"
                    >
                      {city}
                    </button>
                  ))}
                </div>
              </div>

              {/* Other Cities */}
              <div>
                <h3 className="font-semibold text-gray-700 mb-3">Other Cities</h3>
                <div className="grid grid-cols-2 gap-2">
                  {['Coimbatore', 'Guntur', 'Kolkata', 'Lucknow', 'Mysore', 'Nashik', 'Surat', 'Vijayawada', 'Warangal'].map((city) => (
                    <button
                      key={city}
                      onClick={() => handleLocationSelect(city)}
                      className="px-4 py-2 border border-gray-300 hover:bg-blue-50 hover:border-blue-500 rounded-lg text-sm font-medium text-gray-700"
                    >
                      {city}
                    </button>
                  ))}
                </div>
              </div>

              <button
                onClick={() => setShowLocationModal(false)}
                className="w-full mt-6 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </CustomerLayout>
  );
}


// /**
//  * Customer Products Browsing Page
//  */

// import React, { useState, useEffect } from 'react';
// import { productAPI, orderAPI } from '../../services/api';
// import toast from 'react-hot-toast';
// import { CustomerLayout } from '../../components/CustomerLayout';
// import { useNavigate } from 'react-router-dom';

// export function CustomerProductsPage() {
//   const [products, setProducts] = useState([]);
//   const navigate = useNavigate();
//   const [loading, setLoading] = useState(true);
//   const [searchQuery, setSearchQuery] = useState('');
//   const [selectedProduct, setSelectedProduct] = useState(null);
//   const [quantity, setQuantity] = useState(1);
//   const [deliveryDate, setDeliveryDate] = useState('');
  
//   // Location states
//   const [showLocationModal, setShowLocationModal] = useState(
//     !localStorage.getItem('selectedLocation')
//   );
//   const [selectedLocation, setSelectedLocation] = useState(
//     localStorage.getItem('selectedLocation') || ''
//   );

//   useEffect(() => {
//     loadProducts();
//   }, []);

//   const loadProducts = async () => {
//     try {
//       setLoading(true);
//       const response = await productAPI.list();
//       setProducts(response.data);
//     } catch (error) {
//       toast.error('Failed to load products');
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleSearch = async (e) => {
//     e.preventDefault();
//     if (!searchQuery.trim()) {
//       loadProducts();
//       return;
//     }

//     try {
//       const response = await productAPI.search(searchQuery);
//       setProducts(response.data);
//     } catch (error) {
//       toast.error('Search failed');
//     }
//   };

//   // Location handler
//   const handleLocationSelect = (city) => {
//     setSelectedLocation(city);
//     localStorage.setItem('selectedLocation', city);
//     setShowLocationModal(false);
//     toast.success(`Location set to ${city}`);
//   };

//   const handlePlaceOrder = async () => {
//     if (!selectedProduct || !quantity || !deliveryDate) {
//       toast.error('Please fill all fields');
//       return;
//     }
//     const deliveryAddress = localStorage.getItem('selectedLocation');
  
//     if (!deliveryAddress) {
//       toast.error('Please select a delivery location');
//       return;
//     }

//     try {
//       await orderAPI.create({
//         product_id: selectedProduct.id,
//         quantity: parseFloat(quantity),
//         delivery_date: new Date(deliveryDate).toISOString(),
//         delivery_address: deliveryAddress,
//       });
//       toast.success('Order placed successfully!');
//       setSelectedProduct(null);
//       setQuantity(1);
//       setDeliveryDate('');
//     } catch (error) {
//       toast.error(error.response?.data?.detail || 'Failed to place order');
//     }
//   };

//   if (loading) {
//     return (
//       <CustomerLayout>
//         <div className="flex justify-center items-center h-64">Loading...</div>
//       </CustomerLayout>
//     );
//   }

//   return (
//     <CustomerLayout>
//       <div className="space-y-6">
//         {/* Location Display Banner */}
//         <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
//           <div className="flex justify-between items-center">
//             <div>
//               <p className="text-sm text-gray-600">Delivery Location:</p>
//               <p className="text-lg font-bold text-blue-600">
//                 {selectedLocation || 'Not Selected'}
//               </p>
//             </div>
//             <button
//               onClick={() => setShowLocationModal(true)}
//               className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium"
//             >
//               Change Location
//             </button>
//           </div>
//         </div>

//         {/* Search Bar */}
//         <form onSubmit={handleSearch} className="flex gap-2">
//           <input
//             type="text"
//             placeholder="Search milk products..."
//             value={searchQuery}
//             onChange={(e) => setSearchQuery(e.target.value)}
//             className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
//           />
//           <button
//             type="submit"
//             className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//           >
//             Search
//           </button>
//         </form>

//         {/* Products Grid */}
//         <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
//           {products.map((product) => (
//             <div
//               key={product.id}
//               className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
//             >
//               {product.image_url && (
//                 <img
//                   src={`http://localhost:8000${product.image_url}`}
//                   alt={product.name}
//                   className="w-full h-40 object-cover rounded mb-4"
//                 />
//               )}
//               <h3 className="text-lg font-semibold text-gray-800">{product.name}</h3>
//               <p className="text-gray-600 text-sm mb-2">{product.description}</p>
//               <p className="text-green-600 font-bold text-lg mb-4">
//                 ₹{product.unit_price}/{product.unit}
//               </p>
//               <p className="text-sm text-gray-600 mb-4">
//                 Stock: {product.available_quantity} {product.unit}
//               </p>
//               <div className="flex gap-2">
//                 <button
//                   onClick={() => navigate(`/customer/products/${product.id}`)}
//                   disabled={product.available_quantity === 0}
//                   className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm"
//                 >
//                   View Details
//                 </button>
//                 <button
//                   onClick={() => setSelectedProduct(product)}
//                   disabled={product.available_quantity === 0}
//                   className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-gray-400 text-white rounded-lg font-medium text-sm"
//                 >
//                   Order Now
//                 </button>
//               </div>
//             </div>
//           ))}
//         </div>

//         {/* Order Modal */}
//         {selectedProduct && (
//           <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
//             <div className="bg-white rounded-lg p-8 max-w-md w-full">
//               <h2 className="text-2xl font-bold text-gray-800 mb-4">
//                 Order {selectedProduct.name}
//               </h2>

//               <div className="space-y-4">
//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Quantity ({selectedProduct.unit})
//                   </label>
//                   <input
//                     type="number"
//                     min="0.5"
//                     step="0.5"
//                     value={quantity}
//                     onChange={(e) => setQuantity(e.target.value)}
//                     className="w-full px-4 py-2 border border-gray-300 rounded-lg"
//                   />
//                 </div>

//                 <div>
//                   <label className="block text-sm font-medium text-gray-700 mb-2">
//                     Delivery Date
//                   </label>
//                   <input
//                     type="datetime-local"
//                     value={deliveryDate}
//                     onChange={(e) => setDeliveryDate(e.target.value)}
//                     className="w-full px-4 py-2 border border-gray-300 rounded-lg"
//                   />
//                 </div>

//                 <div className="bg-gray-100 p-4 rounded">
//                   <p className="text-gray-600">
//                     Total: ₹
//                     {(selectedProduct.unit_price * quantity).toFixed(2)}
//                   </p>
//                 </div>

//                 <div className="flex gap-2">
//                   <button
//                     onClick={handlePlaceOrder}
//                     className="flex-1 px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium"
//                   >
//                     Place Order
//                   </button>
//                   <button
//                     onClick={() => setSelectedProduct(null)}
//                     className="flex-1 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
//                   >
//                     Cancel
//                   </button>
//                 </div>
//               </div>
//             </div>
//           </div>
//         )}

//         {/* Location Selector Modal */}
//         {showLocationModal && (
//           <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
//             <div className="bg-white rounded-lg p-8 max-w-md w-full max-h-96 overflow-y-auto">
//               <h2 className="text-2xl font-bold text-gray-800 mb-6">Select Delivery Location</h2>
              
//               {/* Popular Cities */}
//               <div className="mb-6">
//                 <h3 className="font-semibold text-gray-700 mb-3">Popular Cities</h3>
//                 <div className="grid grid-cols-2 gap-2">
//                   {['Bangalore', 'Chandigarh', 'Chennai', 'Delhi NCR', 'Hyderabad', 'Jaipur', 'Mumbai', 'Pune'].map((city) => (
//                     <button
//                       key={city}
//                       onClick={() => handleLocationSelect(city)}
//                       className="px-4 py-2 border border-gray-300 hover:bg-blue-50 hover:border-blue-500 rounded-lg text-sm font-medium text-gray-700"
//                     >
//                       {city}
//                     </button>
//                   ))}
//                 </div>
//               </div>

//               {/* Other Cities */}
//               <div>
//                 <h3 className="font-semibold text-gray-700 mb-3">Other Cities</h3>
//                 <div className="grid grid-cols-2 gap-2">
//                   {['Coimbatore', 'Guntur', 'Kolkata', 'Lucknow', 'Mysore', 'Nashik', 'Surat', 'Vijayawada', 'Warangal'].map((city) => (
//                     <button
//                       key={city}
//                       onClick={() => handleLocationSelect(city)}
//                       className="px-4 py-2 border border-gray-300 hover:bg-blue-50 hover:border-blue-500 rounded-lg text-sm font-medium text-gray-700"
//                     >
//                       {city}
//                     </button>
//                   ))}
//                 </div>
//               </div>

//               <button
//                 onClick={() => setShowLocationModal(false)}
//                 className="w-full mt-6 px-4 py-2 bg-gray-300 hover:bg-gray-400 rounded-lg font-medium"
//               >
//                 Close
//               </button>
//             </div>
//           </div>
//         )}
//       </div>
//     </CustomerLayout>
//   );
// }