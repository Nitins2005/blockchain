import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import { Eye, EyeOff, Lock, Mail, User, AlertCircle } from 'lucide-react'
import toast from 'react-hot-toast'

export default function Register() {
  const [form, setForm] = useState({ name: '', email: '', password: '', confirm: '', role: 'investigator' })
  const [showPwd, setShowPwd] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const { login } = useAuthStore()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (form.password !== form.confirm) return setError('Passwords do not match')
    setLoading(true)
    await new Promise(r => setTimeout(r, 1000))
    login({ name: form.name, email: form.email, role: form.role }, 'mock-token-' + Date.now())
    toast.success('Account created successfully!')
    navigate('/dashboard')
    setLoading(false)
  }

  return (
    <div className="glass rounded-2xl p-8" style={{border:'1px solid rgba(99,102,241,0.15)'}}>
      <h2 className="text-xl font-bold mb-1" style={{color:'#f0f4ff'}}>Create Account</h2>
      <p className="text-sm mb-6" style={{color:'#64748b'}}>Join the CryptoShield platform</p>
      {error && (
        <div className="flex items-center gap-2 p-3 rounded-lg mb-4 text-sm"
          style={{background:'rgba(239,68,68,0.1)', border:'1px solid rgba(239,68,68,0.2)', color:'#fca5a5'}}>
          <AlertCircle className="w-4 h-4" />{error}
        </div>
      )}
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{color:'#94a3b8'}}>Full Name</label>
          <div className="relative">
            <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{color:'#475569'}} />
            <input type="text" className="input-field pl-10" placeholder="John Doe"
              value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{color:'#94a3b8'}}>Email</label>
          <div className="relative">
            <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{color:'#475569'}} />
            <input type="email" className="input-field pl-10" placeholder="you@example.com"
              value={form.email} onChange={e => setForm({...form, email: e.target.value})} required />
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{color:'#94a3b8'}}>Role</label>
          <select className="input-field custom-select"
            value={form.role} onChange={e => setForm({...form, role: e.target.value})}>
            <option value="investigator">Investigator</option>
            <option value="admin">Administrator</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{color:'#94a3b8'}}>Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{color:'#475569'}} />
            <input type={showPwd ? 'text':'password'} className="input-field pl-10 pr-10" placeholder="••••••••"
              value={form.password} onChange={e => setForm({...form, password: e.target.value})} required />
            <button type="button" onClick={() => setShowPwd(!showPwd)}
              className="absolute right-3 top-1/2 -translate-y-1/2">
              {showPwd ? <EyeOff className="w-4 h-4" style={{color:'#475569'}} /> : <Eye className="w-4 h-4" style={{color:'#475569'}} />}
            </button>
          </div>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1.5" style={{color:'#94a3b8'}}>Confirm Password</label>
          <div className="relative">
            <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{color:'#475569'}} />
            <input type="password" className="input-field pl-10" placeholder="••••••••"
              value={form.confirm} onChange={e => setForm({...form, confirm: e.target.value})} required />
          </div>
        </div>
        <button type="submit" className="btn btn-primary w-full justify-center" disabled={loading}>
          {loading ? <><span className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full" />Creating...</> : 'Create Account'}
        </button>
      </form>
      <p className="text-center mt-6 text-sm" style={{color:'#64748b'}}>
        Already have an account?{' '}<Link to="/login" style={{color:'#6366f1'}}>Sign in</Link>
      </p>
    </div>
  )
}
