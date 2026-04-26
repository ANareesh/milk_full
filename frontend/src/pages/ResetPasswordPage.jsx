// /**
//  * Reset Password Page Component
//  */

// import React, { useState, useEffect } from 'react';
// import { useSearchParams, useNavigate } from 'react-router-dom';
// import toast from 'react-hot-toast';
// import { Lock } from 'lucide-react';
// import { authAPI } from '../services/api';

// export function ResetPasswordPage() {
//   const [searchParams] = useSearchParams();
//   const navigateRouter = useNavigate();
//   const [newPassword, setNewPassword] = useState('');
//   const [confirmPassword, setConfirmPassword] = useState('');
//   const [loading, setLoading] = useState(false);
//   const [tokenValid, setTokenValid] = useState(null);
  
//   const token = searchParams.get('token');

//   useEffect(() => {
//     // Verify token on page load
//     if (!token) {
//       toast.error('No reset token provided');
//       navigateRouter('/login');
//       return;
//     }

//     const verifyToken = async () => {
//       try {
//         const response = await authAPI.verifyResetToken(token);
//         setTokenValid(response.valid);
//         if (!response.valid) {
//           toast.error('Reset link is invalid or expired');
//           setTimeout(() => navigateRouter('/login'), 2000);
//         }
//       } catch (error) {
//         toast.error('Failed to verify reset token');
//         navigateRouter('/login');
//       }
//     };

//     verifyToken();
//   }, [token, navigateRouter]);

//   const handleSubmit = async (e) => {
//     e.preventDefault();

//     if (newPassword !== confirmPassword) {
//       toast.error('Passwords do not match');
//       return;
//     }

//     if (newPassword.length < 8) {
//       toast.error('Password must be at least 8 characters');
//       return;
//     }

//     setLoading(true);

//     try {
//       await authAPI.resetPassword({
//         token,
//         new_password: newPassword,
//         confirm_password: confirmPassword
//       });
      
//       toast.success('Password reset successfully!');
//       navigateRouter('/login');
//     } catch (error) {
//       toast.error(error.detail || 'Failed to reset password');
//     } finally {
//       setLoading(false);
//     }
//   };

//   if (tokenValid === false) {
//     return null;
//   }

//   return (
//     <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
//       <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
//         <div className="text-center mb-8">
//           <Lock className="w-12 h-12 text-green-600 mx-auto mb-4" />
//           <h1 className="text-3xl font-bold text-gray-800">Create New Password</h1>
//           <p className="text-gray-600 mt-2">Enter your new password below</p>
//         </div>

//         {tokenValid && (
//           <form onSubmit={handleSubmit} className="space-y-4">
//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-2">
//                 New Password
//               </label>
//               <input
//                 type="password"
//                 value={newPassword}
//                 onChange={(e) => setNewPassword(e.target.value)}
//                 required
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
//                 placeholder="Enter new password"
//               />
//               <p className="text-xs text-gray-500 mt-1">
//                 Minimum 8 characters required
//               </p>
//             </div>

//             <div>
//               <label className="block text-sm font-medium text-gray-700 mb-2">
//                 Confirm Password
//               </label>
//               <input
//                 type="password"
//                 value={confirmPassword}
//                 onChange={(e) => setConfirmPassword(e.target.value)}
//                 required
//                 className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
//                 placeholder="Confirm password"
//               />
//             </div>

//             <button
//               type="submit"
//               disabled={loading}
//               className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
//             >
//               {loading ? 'Resetting...' : 'Reset Password'}
//             </button>
//           </form>
//         )}

//         <div className="text-center mt-6">
//           <p className="text-gray-600">
//             Remember your password?{' '}
//             <a href="/login" className="text-green-600 hover:text-green-700 font-medium">
//               Login here
//             </a>
//           </p>
//         </div>
//       </div>
//     </div>
//   );
// }






/**
 * Reset Password Page Component
 */

import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Lock, ArrowLeft } from 'lucide-react';
import { authAPI } from '../services/api';

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [tokenValid, setTokenValid] = useState(null);
  const [verifying, setVerifying] = useState(true);
  
  const token = searchParams.get('token');

  useEffect(() => {
    // Verify token on page load
    if (!token) {
      toast.error('No reset token provided');
      navigate('/login');
      return;
    }

    const verifyToken = async () => {
      try {
        console.log('Verifying token:', token);
        const response = await authAPI.verifyResetToken(token);
        console.log('Token verification response:', response);
        
        if (response.data?.valid || response.valid) {
          setTokenValid(true);
          toast.success('Token verified! Enter your new password.');
        } else {
          setTokenValid(false);
          toast.error('Reset link is invalid or expired');
          setTimeout(() => navigate('/login'), 2000);
        }
      } catch (error) {
        console.error('Token verification error:', error);
        setTokenValid(false);
        toast.error('Failed to verify reset token');
        setTimeout(() => navigate('/login'), 2000);
      } finally {
        setVerifying(false);
      }
    };

    verifyToken();
  }, [token, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!newPassword || !confirmPassword) {
      toast.error('Please fill in all fields');
      return;
    }

    if (newPassword !== confirmPassword) {
      toast.error('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      console.log('Submitting reset password with token:', token);
      const response = await authAPI.resetPassword({
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      
      console.log('Reset password response:', response);
      toast.success('Password reset successfully!');
      
      // Clear form
      setNewPassword('');
      setConfirmPassword('');
      
      // Redirect after a short delay
      setTimeout(() => navigate('/login'), 1500);
    } catch (error) {
      console.error('Reset password error:', error);
      const errorMessage = error.response?.data?.detail || 
                          error.message || 
                          'Failed to reset password';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (verifying) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md text-center">
          <div className="animate-spin inline-block w-12 h-12 border-4 border-gray-300 border-t-green-600 rounded-full mb-4"></div>
          <p className="text-gray-600">Verifying reset token...</p>
        </div>
      </div>
    );
  }

  if (tokenValid === false) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md text-center">
          <div className="text-red-600 text-5xl mb-4">✗</div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Invalid Token</h2>
          <p className="text-gray-600 mb-6">This password reset link is invalid or has expired.</p>
          <a 
            href="/forgot-password" 
            className="inline-block bg-green-600 hover:bg-green-700 text-white font-semibold py-2 px-6 rounded-lg"
          >
            Request New Link
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <div className="flex items-center mb-6">
          <button
            onClick={() => navigate('/login')}
            className="flex items-center text-green-600 hover:text-green-700"
          >
            <ArrowLeft className="w-5 h-5 mr-2" />
            Back to Login
          </button>
        </div>

        <div className="text-center mb-8">
          <Lock className="w-12 h-12 text-green-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-800">Create New Password</h1>
          <p className="text-gray-600 mt-2">Enter your new password below</p>
        </div>

        {tokenValid && (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                New Password
              </label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter new password"
                disabled={loading}
              />
              <p className="text-xs text-gray-500 mt-1">
                Minimum 8 characters required
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Confirm Password
              </label>
              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Confirm password"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Resetting...' : 'Reset Password'}
            </button>
          </form>
        )}

        <div className="text-center mt-6">
          <p className="text-gray-600">
            Remember your password?{' '}
            <a href="/login" className="text-green-600 hover:text-green-700 font-medium">
              Login here
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}