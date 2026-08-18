import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Mail, ArrowLeft, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function ForgotPassword() {
  const [email, setEmail] = useState('')
  const [sent, setSent] = useState(false)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    setSent(true)
    toast.success('Reset link sent!')
    setLoading(false)
  }

  if (sent) return (
    <div className="glass rounded-2xl p-8 text-center" style={{border:'1px solid rgba(99,102,241,0.15)'}}>
      <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto mb-4"
        style={{background:'rgba(16,185,129,0.1)', border:'1px solid rgba(16,185,129,0.2)'}}>
        <CheckCircle className="w-7 h-7" style={{color:'#10b981'}} />
      </div>
      <h2 className="text-xl font-bold mb-2" style={{color:'#f0f4ff'}}>Check your email</h2>
      <p className="text-sm mb-6" style={{color:'#64748b'}}>We sent a reset link to <span style={{color:'#a5b4fc'}}>{email}</span></p>
      <Link to="/login" className="btn btn-primary w-full justify-center">Back to Login</Link>
    </div>
  )

  return (
    <div className="glass rounded-2xl p-8" style={{border:'1px solid rgba(99,102,241,0.15)'}}>
      <h2 className="text-xl font-bold mb-1" style={{color:'#f0f4ff'}}>Reset Password</h2>
      <p className="text-sm mb-6" style={{color:'#64748b'}}>Enter your email to receive a reset link</p>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{color:'#94a3b8'}}>Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{color:'#475569'}} />
            <input type="email" className="input-field pl-10" placeholder="you@example.com"
              value={email} onChange={e => setEmail(e.target.value)} required />
          </div>
        </div>
        <button type="submit" className="btn btn-primary w-full justify-center" disabled={loading}>
          {loading ? <><span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />Sending...</> : 'Send Reset Link'}
        </button>
      </form>
      <Link to="/login" className="flex items-center gap-2 justify-center mt-4 text-sm" style={{color:'#64748b'}}>
        <ArrowLeft className="w-4 h-4" /> Back to login
      </Link>
    </div>
  )
}
