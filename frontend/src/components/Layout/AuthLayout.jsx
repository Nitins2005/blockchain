import { Outlet } from 'react-router-dom'
import { Shield } from 'lucide-react'

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-mesh network-bg flex items-center justify-center p-4" style={{background:'#050812'}}>
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 rounded-full" style={{background:'radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%)'}} />
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 rounded-full" style={{background:'radial-gradient(circle, rgba(14,165,233,0.06) 0%, transparent 70%)'}} />
        <div className="absolute top-1/2 left-1/2 w-64 h-64 rounded-full" style={{background:'radial-gradient(circle, rgba(16,185,129,0.04) 0%, transparent 70%)', transform:'translate(-50%,-50%)'}} />
      </div>

      {/* Grid lines */}
      <div className="absolute inset-0 network-bg opacity-50" />

      <div className="relative z-10 w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl mb-4 gradient-border" style={{background:'linear-gradient(135deg, rgba(99,102,241,0.2), rgba(14,165,233,0.2))'}}>
            <Shield className="w-8 h-8" style={{color:'#6366f1'}} />
          </div>
          <h1 className="text-3xl font-bold gradient-text">CryptoShield AI</h1>
          <p className="text-sm mt-1" style={{color:'#64748b'}}>Cryptocurrency Fraud Detection Platform</p>
        </div>

        <Outlet />

        <p className="text-center mt-6 text-xs" style={{color:'#475569'}}>
          © 2024 CryptoShield AI. All rights reserved.
        </p>
      </div>
    </div>
  )
}
