import React, { useState, useEffect } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { notificationsAPI } from '../../services/api'
import { ShieldAlert, Cpu, FolderOpen, Ban, AlertOctagon, X, Check } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import { formatDateTime } from '../../utils/formatters'
import toast from 'react-hot-toast'

const MOCK_NOTIFICATIONS = Array.from({ length: 8 }, (_, i) => ({
  id: `notif-${i}`,
  type: ['fraud_detected', 'model_trained', 'new_investigation', 'wallet_blacklisted', 'high_risk_found'][i % 5],
  title: [
    'Critical Fraud Detected',
    'AI Model Retrained',
    'New Investigation Assigned',
    'Wallet Added to Blacklist',
    'High Risk Connection Found'
  ][i % 5],
  message: 'System generated notification regarding recent activities.',
  is_read: i % 3 === 0,
  created_at: new Date(Date.now() - Math.random() * 100000000).toISOString()
}))

const TYPE_ICONS = {
  fraud_detected: { icon: ShieldAlert, color: 'text-red-400', bg: 'bg-red-500/10' },
  model_trained: { icon: Cpu, color: 'text-emerald-400', bg: 'bg-emerald-500/10' },
  new_investigation: { icon: FolderOpen, color: 'text-blue-400', bg: 'bg-blue-500/10' },
  wallet_blacklisted: { icon: Ban, color: 'text-orange-400', bg: 'bg-orange-500/10' },
  high_risk_found: { icon: AlertOctagon, color: 'text-red-400', bg: 'bg-red-500/10' }
}

export default function NotificationsPage() {
  const [notifications, setNotifications] = useState([])
  const [loading, setLoading] = useState(true)
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      if (notificationsAPI && notificationsAPI.getAll) {
        const res = await notificationsAPI.getAll()
        setNotifications(res.data)
      } else throw new Error('API missing')
    } catch {
      setNotifications(MOCK_NOTIFICATIONS)
    } finally {
      setLoading(false)
    }
  }

  const handleMarkAsRead = async (id) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, is_read: true } : n))
  }

  const handleMarkAllRead = async () => {
    setNotifications(prev => prev.map(n => ({ ...n, is_read: true })))
    toast.success('All notifications marked as read')
  }

  const handleDelete = async (id) => {
    setNotifications(prev => prev.filter(n => n.id !== id))
  }

  const filtered = notifications.filter(n => filter === 'all' || !n.is_read)

  return (
    <PageWrapper title="Notifications">
      <div className="max-w-4xl mx-auto">
        <div className="bg-dark-300 border border-white/10 rounded-xl flex flex-col min-h-[600px]">
          
          <div className="p-4 border-b border-white/10 flex justify-between items-center">
            <div className="flex gap-2 bg-dark-400 p-1 rounded-lg">
              <button onClick={() => setFilter('all')} className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${filter === 'all' ? 'bg-primary-600 text-white' : 'text-white/60 hover:text-white'}`}>All</button>
              <button onClick={() => setFilter('unread')} className={`px-4 py-1.5 rounded-md text-sm font-medium transition-colors ${filter === 'unread' ? 'bg-primary-600 text-white' : 'text-white/60 hover:text-white'}`}>
                Unread <span className="ml-1 bg-white/20 px-1.5 py-0.5 rounded-full text-xs">{notifications.filter(n => !n.is_read).length}</span>
              </button>
            </div>
            
            <button onClick={handleMarkAllRead} className="flex items-center gap-2 text-sm text-primary-400 hover:text-primary-300">
              <Check size={16} /> Mark all as read
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {loading ? (
              <div className="py-12 flex justify-center"><Spinner /></div>
            ) : filtered.length === 0 ? (
              <div className="py-16 text-center">
                <div className="w-16 h-16 bg-dark-400 rounded-full flex items-center justify-center mx-auto mb-4 text-white/20"><Check size={32} /></div>
                <p className="text-white/60">You're all caught up!</p>
              </div>
            ) : (
              filtered.map(notif => {
                const IconConfig = TYPE_ICONS[notif.type] || { icon: ShieldAlert, color: 'text-white/60', bg: 'bg-white/10' }
                return (
                  <div 
                    key={notif.id} 
                    onClick={() => handleMarkAsRead(notif.id)}
                    className={`relative group p-4 rounded-xl border transition-all cursor-pointer ${notif.is_read ? 'bg-dark-400/50 border-white/5' : 'bg-dark-400 border-primary-500/30 shadow-[0_0_15px_rgba(99,102,241,0.05)]'}`}
                  >
                    {!notif.is_read && <div className="absolute top-4 right-4 w-2 h-2 rounded-full bg-primary-500"></div>}
                    
                    <div className="flex gap-4">
                      <div className={`mt-1 flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${IconConfig.bg} ${IconConfig.color}`}>
                        <IconConfig.icon size={20} />
                      </div>
                      <div className="flex-1 pr-8">
                        <div className="flex justify-between items-start mb-1">
                          <h4 className={`font-medium ${notif.is_read ? 'text-white/80' : 'text-white'}`}>{notif.title}</h4>
                          <span className="text-xs text-white/40">{formatDateTime(notif.created_at)}</span>
                        </div>
                        <p className="text-sm text-white/60">{notif.message}</p>
                      </div>
                    </div>
                    
                    <button 
                      onClick={(e) => { e.stopPropagation(); handleDelete(notif.id); }}
                      className="absolute bottom-4 right-4 p-2 text-white/20 hover:text-red-400 hover:bg-white/5 rounded-lg opacity-0 group-hover:opacity-100 transition-all"
                    >
                      <X size={16} />
                    </button>
                  </div>
                )
              })
            )}
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
