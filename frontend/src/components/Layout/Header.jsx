import { useState } from 'react'
import { Link } from 'react-router-dom'
import { useNotificationStore } from '../../store/notificationStore'
import { useAuthStore } from '../../store/authStore'
import { Bell, Search, Menu, Zap } from 'lucide-react'

export default function Header({ onMenuToggle }) {
  const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotificationStore()
  const { user } = useAuthStore()
  const [showNotifications, setShowNotifications] = useState(false)
  const [searchQuery, setSearchQuery] = useState('')

  const unread = notifications.filter(n => !n.read).length

  const severityColor = (s) => ({
    critical: '#ef4444', warning: '#f59e0b', info: '#6366f1'
  }[s] || '#6366f1')

  return (
    <header className="flex items-center gap-4 px-6" style={{
      height: '65px',
      background: 'rgba(7,13,26,0.95)',
      borderBottom: '1px solid #1e2d45',
      backdropFilter: 'blur(20px)',
      flexShrink: 0,
    }}>
      {/* Menu toggle */}
      <button onClick={onMenuToggle} className="p-2 rounded-lg hover:bg-white/5 transition-colors">
        <Menu className="w-5 h-5" style={{color:'#64748b'}} />
      </button>

      {/* Search */}
      <div className="flex-1 max-w-md relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4" style={{color:'#475569'}} />
        <input
          type="text"
          placeholder="Search wallet address, tx hash..."
          className="input-field pl-9 text-sm"
          style={{height:'38px'}}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      <div className="flex items-center gap-2 ml-auto">
        {/* Live indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full text-xs"
          style={{background:'rgba(16,185,129,0.08)', border:'1px solid rgba(16,185,129,0.2)', color:'#10b981'}}>
          <Zap className="w-3 h-3" />
          Live
        </div>

        {/* Notifications */}
        <div className="relative">
          <button
            onClick={() => setShowNotifications(!showNotifications)}
            className="relative p-2 rounded-lg hover:bg-white/5 transition-colors"
          >
            <Bell className="w-5 h-5" style={{color:'#64748b'}} />
            {unread > 0 && (
              <span className="absolute top-1 right-1 w-4 h-4 rounded-full text-xs flex items-center justify-center font-bold"
                style={{background:'#ef4444', color:'white', fontSize:'9px'}}>
                {unread}
              </span>
            )}
          </button>

          {showNotifications && (
            <div className="absolute right-0 top-12 w-80 rounded-xl shadow-2xl z-50"
              style={{background:'#0d1424', border:'1px solid #1e2d45'}}>
              <div className="flex items-center justify-between p-4" style={{borderBottom:'1px solid #1e2d45'}}>
                <div className="font-semibold text-sm" style={{color:'#f0f4ff'}}>Notifications</div>
                <button onClick={markAllAsRead} className="text-xs" style={{color:'#6366f1'}}>Mark all read</button>
              </div>
              <div className="max-h-80 overflow-y-auto">
                {notifications.map(n => (
                  <div
                    key={n.id}
                    onClick={() => markAsRead(n.id)}
                    className="p-4 cursor-pointer hover:bg-white/3 transition-colors"
                    style={{borderBottom:'1px solid rgba(30,45,69,0.5)', opacity: n.read ? 0.6 : 1}}
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-2 h-2 rounded-full mt-1.5 flex-shrink-0" style={{background: severityColor(n.severity)}} />
                      <div className="flex-1">
                        <div className="text-sm font-medium" style={{color:'#f0f4ff'}}>{n.title}</div>
                        <div className="text-xs mt-0.5" style={{color:'#64748b'}}>{n.message}</div>
                        <div className="text-xs mt-1" style={{color:'#3d5478'}}>{n.time}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Profile */}
        <Link to="/profile" className="flex items-center gap-2 px-3 py-1.5 rounded-lg hover:bg-white/5 transition-colors">
          <div className="w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
            style={{background:'linear-gradient(135deg, #6366f1, #0ea5e9)', color:'white'}}>
            {user?.name?.charAt(0) || 'U'}
          </div>
          <span className="text-sm hidden sm:block" style={{color:'#94a3b8'}}>{user?.name || 'User'}</span>
        </Link>
      </div>
    </header>
  )
}
