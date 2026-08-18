import { Link } from 'react-router-dom'
import { Shield, Home } from 'lucide-react'

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center" style={{background:'#050812'}}>
      <div className="text-center">
        <div className="text-8xl font-black mb-4 gradient-text">404</div>
        <h1 className="text-2xl font-bold mb-2" style={{color:'#f0f4ff'}}>Page Not Found</h1>
        <p className="mb-8" style={{color:'#64748b'}}>The page you're looking for doesn't exist.</p>
        <Link to="/dashboard" className="btn btn-primary">
          <Home className="w-4 h-4" /> Back to Dashboard
        </Link>
      </div>
    </div>
  )
}
