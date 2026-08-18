import { create } from 'zustand'

export const useNotificationStore = create((set, get) => ({
  notifications: [
    {
      id: 1,
      type: 'fraud',
      title: 'High-Risk Wallet Detected',
      message: 'Wallet 0x742d...B3f2 scored 94/100 fraud score',
      time: '2 min ago',
      read: false,
      severity: 'critical',
    },
    {
      id: 2,
      type: 'model',
      title: 'Model Training Complete',
      message: 'Temporal GNN reached 97.3% accuracy on validation set',
      time: '15 min ago',
      read: false,
      severity: 'info',
    },
    {
      id: 3,
      type: 'blacklist',
      title: 'Wallet Blacklisted',
      message: 'Address bc1q...xkp9 added to blacklist',
      time: '1 hr ago',
      read: true,
      severity: 'warning',
    },
    {
      id: 4,
      type: 'investigation',
      title: 'New Investigation Assigned',
      message: 'Case #INV-2024-089 assigned to you',
      time: '3 hr ago',
      read: true,
      severity: 'info',
    },
  ],

  unreadCount: () => get().notifications.filter(n => !n.read).length,

  markAsRead: (id) => {
    set(state => ({
      notifications: state.notifications.map(n =>
        n.id === id ? { ...n, read: true } : n
      ),
    }))
  },

  markAllAsRead: () => {
    set(state => ({
      notifications: state.notifications.map(n => ({ ...n, read: true })),
    }))
  },

  addNotification: (notification) => {
    set(state => ({
      notifications: [{ ...notification, id: Date.now(), read: false }, ...state.notifications],
    }))
  },
}))
