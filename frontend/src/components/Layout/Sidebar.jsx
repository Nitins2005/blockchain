import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../../store/authStore'
import {
  Shield, LayoutDashboard, ArrowLeftRight, AlertTriangle,
  Network, Brain, Eye, Cpu, Settings, ListX, FileSearch,
  BarChart3, FileText, ChevronLeft, ChevronRight, Users,
  Activity, Zap, LogOut
} from 'lucide-react'

const navItems = [
  { group: 'Overview', items: [
    { path: '/dashboard', icon: LayoutDashboard, label: 'Dashboard' },
    { path: '/analytics', icon: BarChart3, label: 'Analytics' },
  ]},
  { group: 'Blockchain', items: [
    { path: '/transactions', icon: ArrowLeftRight, label: 'Transactions' },
    { path: '/blockchain-config', icon: Settings, label: 'Blockchain Config' },
    { path: '/graph', icon: Network, label: 'Graph Visualization' },
  ]},
  { group: 'AI Detection', items: [
    { path: '/fraud-detection', icon: AlertTriangle, label: 'Fraud Detection' },
    { path: '/wallet-attribution', icon: Cpu, label: 'Wallet Attribution' },
    { path: '/explainable-ai', icon: Brain, label: 'Explainable AI' },
  ]},
  { group: 'Operations', items: [
    { path: '/investigations', icon: FileSearch, label: 'Investigations' },
    { path: '/blacklist', icon: ListX, label: 'Blacklist' },
    { path: '/reports', icon: FileText, label: 'Reports' },
  ]},
]

export default function Sidebar({ isOpen, onToggle }) {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <aside
      className="flex flex-col transition-all duration-300 relative"
      style={{
        width: isOpen ? '260px' : '72px',
        background: 'rgba(7, 13, 26, 0.95)',
        borderRight: '1px solid #1e2d45',
        backdropFilter: 'blur(20px)',
        flexShrink: 0,
      }}
    >
      {/* Logo */}
      <div className="flex items-center gap-3 p-4" style={{borderBottom: '1px solid #1e2d45', height: '65px'}}>
        <div className="flex-shrink-0 w-9 h-9 rounded-xl flex items-center justify-center" style={{background:'linear-gradient(135deg, #6366f1, #4f46e5)'}}>
          <Shield className="w-5 h-5 text-white" />
        </div>
        {isOpen && (
          <div className="overflow-hidden">
            <div className="font-bold text-sm leading-tight gradient-text whitespace-nowrap">CryptoShield</div>
            <div className="text-xs" style={{color:'#475569'}}>AI Platform</div>
          </div>
        )}
      </div>

      {/* Toggle button */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-14 w-6 h-6 rounded-full flex items-center justify-center z-10"
        style={{background:'#1e2d45', border:'1px solid #2d3f5e'}}
      >
        {isOpen ? <ChevronLeft className="w-3 h-3" style={{color:'#94a3b8'}} /> : <ChevronRight className="w-3 h-3" style={{color:'#94a3b8'}} />}
      </button>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4 px-2">
        {navItems.map((group) => (
          <div key={group.group} className="mb-4">
            {isOpen && (
              <div className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider" style={{color:'#3d5478'}}>
                {group.group}
              </div>
            )}
            {group.items.map((item) => (
              <NavLink
                key={item.path}
                to={item.path}
                className={({ isActive }) =>
                  `sidebar-item flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 text-sm transition-all ${
                    isActive ? 'active' : ''
                  }`
                }
                style={({ isActive }) => ({
                  color: isActive ? '#a5b4fc' : '#64748b',
                  background: isActive ? 'rgba(99,102,241,0.1)' : 'transparent',
                  borderLeft: isActive ? '2px solid #6366f1' : '2px solid transparent',
                })}
                title={!isOpen ? item.label : ''}
              >
                <item.icon className="w-4 h-4 flex-shrink-0" />
                {isOpen && <span className="whitespace-nowrap font-medium">{item.label}</span>}
              </NavLink>
            ))}
          </div>
        ))}

        {/* Admin section */}
        {user?.role === 'admin' && (
          <div className="mb-4">
            {isOpen && (
              <div className="px-3 mb-2 text-xs font-semibold uppercase tracking-wider" style={{color:'#3d5478'}}>
                Admin
              </div>
            )}
            <NavLink
              to="/admin/users"
              className="sidebar-item flex items-center gap-3 px-3 py-2.5 rounded-lg mb-1 text-sm"
              style={({ isActive }) => ({
                color: isActive ? '#a5b4fc' : '#64748b',
                background: isActive ? 'rgba(99,102,241,0.1)' : 'transparent',
                borderLeft: isActive ? '2px solid #6366f1' : '2px solid transparent',
              })}
            >
              <Users className="w-4 h-4 flex-shrink-0" />
              {isOpen && <span className="font-medium">User Management</span>}
            </NavLink>
          </div>
        )}
      </nav>

      {/* Model status indicator */}
      {isOpen && (
        <div className="mx-3 mb-3 p-3 rounded-xl" style={{background:'rgba(16,185,129,0.08)', border:'1px solid rgba(16,185,129,0.2)'}}>
          <div className="flex items-center gap-2 mb-1">
            <div className="w-2 h-2 rounded-full" style={{background:'#10b981', boxShadow:'0 0 6px rgba(16,185,129,0.6)'}} />
            <span className="text-xs font-semibold" style={{color:'#10b981'}}>AI Model Online</span>
          </div>
          <div className="text-xs" style={{color:'#475569'}}>v2.1.4 · Accuracy 97.3%</div>
        </div>
      )}

      {/* User profile */}
      <div className="p-3" style={{borderTop:'1px solid #1e2d45'}}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 text-sm font-bold"
            style={{background:'linear-gradient(135deg, #6366f1, #0ea5e9)', color:'white'}}>
            {user?.name?.charAt(0) || 'U'}
          </div>
          {isOpen && (
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium truncate" style={{color:'#f0f4ff'}}>{user?.name || 'User'}</div>
              <div className="text-xs capitalize" style={{color:'#475569'}}>{user?.role || 'investigator'}</div>
            </div>
          )}
          {isOpen && (
            <button onClick={handleLogout} className="p-1.5 rounded-lg hover:bg-red-500/10 transition-colors" title="Logout">
              <LogOut className="w-4 h-4" style={{color:'#64748b'}} />
            </button>
          )}
        </div>
      </div>
    </aside>
  )
}
