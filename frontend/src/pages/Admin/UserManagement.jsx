import React, { useState, useEffect } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { usersAPI } from '../../services/api'
import { Search, Plus, UserPlus, Shield, User, Edit2, Trash2 } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import Modal from '../../components/UI/Modal'
import Pagination from '../../components/UI/Pagination'
import { formatDateTime } from '../../utils/formatters'
import toast from 'react-hot-toast'
import StatCard from '../../components/UI/StatCard'

const MOCK_USERS = Array.from({ length: 10 }, (_, i) => ({
  id: `usr-${i}`,
  username: `user_${i}`,
  email: `user${i}@cryptoshield.ai`,
  full_name: ['John Doe', 'Jane Smith', 'Alice Jones', 'Bob Brown'][i % 4],
  role: i % 4 === 0 ? 'admin' : 'investigator',
  department: ['Compliance', 'Fraud', 'Security'][i % 3],
  is_active: i !== 8,
  last_login: new Date(Date.now() - Math.random() * 100000000).toISOString()
}))

export default function UserManagement() {
  const [users, setUsers] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('all')
  const [showModal, setShowModal] = useState(false)
  const [editUser, setEditUser] = useState(null)
  
  const initialForm = { email: '', username: '', full_name: '', password: '', role: 'investigator', department: '' }
  const [formData, setFormData] = useState(initialForm)

  useEffect(() => {
    loadUsers()
  }, [page, roleFilter])

  const loadUsers = async () => {
    setLoading(true)
    try {
      if (usersAPI && usersAPI.getAll) {
        const res = await usersAPI.getAll({ page, role: roleFilter !== 'all' ? roleFilter : undefined })
        setUsers(res.data.items || res.data)
        setTotal(res.data.total || 100)
      } else throw new Error('API missing')
    } catch {
      let filtered = MOCK_USERS
      if (roleFilter !== 'all') filtered = filtered.filter(u => u.role === roleFilter)
      setUsers(filtered)
      setTotal(10)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      if (editUser) {
        // update API
      } else {
        // create API
      }
      toast.success(editUser ? 'User updated' : 'User created')
      setShowModal(false)
      loadUsers()
    } catch {
      toast.error('Failed to save user')
    }
  }

  const openEdit = (u) => {
    setEditUser(u)
    setFormData({ email: u.email, username: u.username, full_name: u.full_name, password: '', role: u.role, department: u.department })
    setShowModal(true)
  }

  const toggleStatus = async (id, currentStatus) => {
    toast.success(`User ${currentStatus ? 'deactivated' : 'activated'} (Mock)`)
    setUsers(users.map(u => u.id === id ? { ...u, is_active: !currentStatus } : u))
  }

  return (
    <PageWrapper title="User Management">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <StatCard title="Total Users" value={total} icon={UserPlus} color="primary" />
        <StatCard title="Active Users" value={users.filter(u => u.is_active).length} icon={User} color="green" />
        <StatCard title="Admins" value={users.filter(u => u.role === 'admin').length} icon={Shield} color="orange" />
      </div>

      <div className="bg-dark-300 border border-white/10 rounded-xl flex flex-col">
        <div className="p-4 border-b border-white/10 flex justify-between items-center flex-wrap gap-4">
          <div className="flex gap-2 bg-dark-400 p-1 rounded-lg">
            {['all', 'admin', 'investigator'].map(role => (
              <button key={role} onClick={() => { setRoleFilter(role); setPage(1); }} className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${roleFilter === role ? 'bg-primary-600 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}>
                {role}
              </button>
            ))}
          </div>
          
          <div className="flex gap-4">
            <div className="relative w-64">
              <Search size={18} className="absolute left-3 top-2.5 text-white/40" />
              <input type="text" placeholder="Search users..." value={search} onChange={e => setSearch(e.target.value)} className="w-full bg-dark-400 border border-white/10 rounded-lg pl-10 pr-3 py-2 text-white focus:border-primary-500 outline-none" />
            </div>
            <button onClick={() => { setEditUser(null); setFormData(initialForm); setShowModal(true); }} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors">
              <Plus size={18} /> Add User
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 flex justify-center"><Spinner /></div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="bg-dark-400/50 border-b border-white/10 text-white/60 text-sm">
                  <th className="p-4 font-medium">User</th>
                  <th className="p-4 font-medium">Role</th>
                  <th className="p-4 font-medium">Department</th>
                  <th className="p-4 font-medium">Status</th>
                  <th className="p-4 font-medium">Last Login</th>
                  <th className="p-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.filter(u => u.full_name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase())).map(user => (
                  <tr key={user.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary-500/20 text-primary-400 flex items-center justify-center font-bold">
                          {user.full_name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <p className="text-white font-medium">{user.full_name}</p>
                          <p className="text-xs text-white/50">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-md text-xs capitalize ${user.role === 'admin' ? 'bg-purple-500/10 text-purple-400' : 'bg-blue-500/10 text-blue-400'}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-white/80">{user.department}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${user.is_active ? 'bg-emerald-500/10 text-emerald-400' : 'bg-gray-500/10 text-gray-400'}`}>
                        {user.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                    <td className="p-4 text-sm text-white/60">{formatDateTime(user.last_login)}</td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-2 text-white/40">
                        <button onClick={() => toggleStatus(user.id, user.is_active)} className="hover:text-white px-2 text-xs">{user.is_active ? 'Deactivate' : 'Activate'}</button>
                        <button onClick={() => openEdit(user)} className="hover:text-white p-1"><Edit2 size={16} /></button>
                        <button className="hover:text-red-400 p-1"><Trash2 size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <Pagination page={page} pages={Math.ceil(total / 10)} total={total} pageSize={10} onPageChange={setPage} />
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title={editUser ? "Edit User" : "Add New User"}>
        <form onSubmit={handleSave} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/60 mb-1">Full Name</label>
              <input required type="text" value={formData.full_name} onChange={e => setFormData({...formData, full_name: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Username</label>
              <input required type="text" value={formData.username} onChange={e => setFormData({...formData, username: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            </div>
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Email</label>
            <input required type="email" value={formData.email} onChange={e => setFormData({...formData, email: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
          </div>
          {!editUser && (
            <div>
              <label className="block text-sm text-white/60 mb-1">Password</label>
              <input required type="password" value={formData.password} onChange={e => setFormData({...formData, password: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            </div>
          )}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/60 mb-1">Role</label>
              <select value={formData.role} onChange={e => setFormData({...formData, role: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none">
                <option value="investigator">Investigator</option>
                <option value="admin">Admin</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Department</label>
              <input type="text" value={formData.department} onChange={e => setFormData({...formData, department: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            </div>
          </div>
          <div className="pt-4 flex justify-end gap-3">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-white/60 hover:text-white">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg">Save User</button>
          </div>
        </form>
      </Modal>
    </PageWrapper>
  )
}
