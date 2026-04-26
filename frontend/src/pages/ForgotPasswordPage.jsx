/**
 * Forgot Password Page Component
 */

import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { Mail, ArrowLeft } from 'lucide-react';
import { authAPI } from '../services/api';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);

    try {
      const response = await authAPI.forgotPassword({ email });
      toast.success('Password reset link sent to your email!');
      setSubmitted(true);
      
      // Redirect to login after 3 seconds
      setTimeout(() => navigate('/login'), 3000);
    } catch (error) {
      toast.error('Failed to send reset link. Please try again.');
    } finally {
      setLoading(false);
    }
  };

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
          <Mail className="w-12 h-12 text-green-600 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-800">Reset Password</h1>
          <p className="text-gray-600 mt-2">
            Enter your email to receive a password reset link
          </p>
        </div>

        {!submitted ? (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="Enter your email"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-2 rounded-lg transition disabled:opacity-50"
            >
              {loading ? 'Sending...' : 'Send Reset Link'}
            </button>
          </form>
        ) : (
          <div className="text-center p-6 bg-green-50 rounded-lg">
            <div className="text-green-600 text-5xl mb-4">✓</div>
            <h2 className="text-xl font-semibold text-gray-800 mb-2">
              Check Your Email
            </h2>
            <p className="text-gray-600 mb-4">
              We've sent a password reset link to <strong>{email}</strong>
            </p>
            <p className="text-sm text-gray-500">
              The link will expire in 30 minutes. Redirecting to login...
            </p>
          </div>
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