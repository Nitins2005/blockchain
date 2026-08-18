import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import toast from 'react-hot-toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(email, password);
      toast.success('Logged in successfully');
      navigate('/dashboard');
    } catch (err) {
      toast.error('Failed to login');
    }
  };

  const handleDemoClick = () => {
    setEmail('admin@cryptoshield.ai');
    setPassword('admin123');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-dark-400 p-4">
      <div className="glass-dark max-w-md w-full p-8">
        <h1 className="text-3xl font-bold gradient-text mb-2 text-center">CryptoShield AI</h1>
        <p className="text-white/60 text-center mb-8">Sign in to the platform</p>
        
        <div className="bg-primary-500/10 border border-primary-500/30 rounded-lg p-4 mb-6 cursor-pointer hover:bg-primary-500/20 transition-colors" onClick={handleDemoClick}>
          <p className="text-sm text-primary-300 font-medium text-center">Click here for demo credentials</p>
          <p className="text-xs text-primary-400/70 text-center mt-1">admin@cryptoshield.ai / admin123</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-white/80 mb-1">Email Address</label>
            <input 
              type="email" 
              className="input-field" 
              value={email} 
              onChange={e => setEmail(e.target.value)} 
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-white/80 mb-1">Password</label>
            <input 
              type="password" 
              className="input-field" 
              value={password} 
              onChange={e => setPassword(e.target.value)} 
              required
            />
          </div>
          <button type="submit" className="btn-primary w-full justify-center mt-6">
            Sign In
          </button>
        </form>
      </div>
    </div>
  );
}
