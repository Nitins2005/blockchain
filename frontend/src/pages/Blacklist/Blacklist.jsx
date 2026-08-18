import React, { useState, useEffect } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { blacklistAPI } from '../../services/api'
import { Search, Plus, Upload, Download, Edit2, Trash2 } from 'lucide-react'
import Pagination from '../../components/UI/Pagination'
import Spinner from '../../components/UI/Spinner'
import Modal from '../../components/UI/Modal'
import { formatAddress, formatDateTime } from '../../utils/formatters'
import toast from 'react-hot-toast'

const MOCK_BLACKLIST = Array.from({ length: 20 }, (_, i) => ({
  id: `bl-${i}`,
  address: `0x${Math.random().toString(16).slice(2, 42)}`,
  blockchain: ['ethereum', 'bitcoin', 'polygon'][i % 3],
  category: ['scam', 'mixer', 'darknet', 'exchange'][i % 4],
  reason: 'Involved in Phishing campaign ' + i,
  source: 'Manual Entry',
  confidence: 0.8 + Math.random() * 0.2,
  status: i % 10 === 0 ? 'inactive' : 'active',
  created_at: new Date(Date.now() - Math.random() * 100000000).toISOString()
}))

export default function Blacklist() {
  const [entries, setEntries] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [categoryFilter, setCategoryFilter] = useState('all')
  
  const [showModal, setShowModal] = useState(false)
  const [formData, setFormData] = useState({ address: '', blockchain: 'ethereum', category: 'scam', reason: '', source: 'Manual', confidence: 1.0 })

  useEffect(() => {
    loadData()
  }, [page, categoryFilter])

  const loadData = async () => {
    setLoading(true)
    try {
      if (blacklistAPI && blacklistAPI.getAll) {
        const res = await blacklistAPI.getAll({ page, category: categoryFilter !== 'all' ? categoryFilter : undefined })
        setEntries(res.data.items || res.data)
        setTotal(res.data.total || 100)
      } else {
        throw new Error('API not available')
      }
    } catch {
      let filtered = MOCK_BLACKLIST
      if (categoryFilter !== 'all') filtered = filtered.filter(e => e.category === categoryFilter)
      setEntries(filtered)
      setTotal(100)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async (e) => {
    e.preventDefault()
    try {
      if (blacklistAPI && blacklistAPI.add) {
        await blacklistAPI.add(formData)
      }
      toast.success('Address added to blacklist')
      setShowModal(false)
      loadData()
    } catch {
      toast.error('Failed to add to blacklist')
    }
  }

  const tabs = ['all', 'scam', 'mixer', 'darknet', 'exchange']

  return (
    <PageWrapper title="Blacklist Management">
      <div className="bg-dark-300 border border-white/10 rounded-xl flex flex-col">
        
        {/* Header/Controls */}
        <div className="p-4 border-b border-white/10">
          <div className="flex flex-wrap gap-4 justify-between items-center mb-4">
            <div className="flex gap-2 bg-dark-400 p-1 rounded-lg">
              {tabs.map(tab => (
                <button 
                  key={tab} 
                  onClick={() => { setCategoryFilter(tab); setPage(1); }}
                  className={`px-4 py-1.5 rounded-md text-sm font-medium capitalize transition-colors ${categoryFilter === tab ? 'bg-primary-600 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'}`}
                >
                  {tab}
                </button>
              ))}
            </div>
            
            <div className="flex gap-2">
              <button className="flex items-center gap-2 px-3 py-2 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white rounded-lg transition-colors text-sm">
                <Upload size={16} /> Import
              </button>
              <button className="flex items-center gap-2 px-3 py-2 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white rounded-lg transition-colors text-sm">
                <Download size={16} /> Export
              </button>
              <button onClick={() => setShowModal(true)} className="flex items-center gap-2 px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors text-sm">
                <Plus size={16} /> Add Address
              </button>
            </div>
          </div>
          
          <div className="relative max-w-md">
            <Search size={18} className="absolute left-3 top-2.5 text-white/40" />
            <input 
              type="text" 
              placeholder="Search address..." 
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full bg-dark-400 border border-white/10 rounded-lg pl-10 pr-3 py-2 text-white focus:border-primary-500 outline-none"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 flex justify-center"><Spinner /></div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="bg-dark-400/50 border-b border-white/10 text-white/60 text-sm">
                  <th className="p-4 font-medium">Address</th>
                  <th className="p-4 font-medium">Chain</th>
                  <th className="p-4 font-medium">Category</th>
                  <th className="p-4 font-medium">Reason</th>
                  <th className="p-4 font-medium">Status</th>
                  <th className="p-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {entries.filter(e => e.address.toLowerCase().includes(search.toLowerCase())).map(entry => (
                  <tr key={entry.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4 font-mono text-sm text-primary-400">{formatAddress(entry.address)}</td>
                    <td className="p-4 text-sm text-white/80 capitalize">{entry.blockchain}</td>
                    <td className="p-4">
                      <span className="px-2 py-1 bg-dark-400 rounded-md text-xs text-white/70 capitalize">{entry.category}</span>
                    </td>
                    <td className="p-4 text-sm text-white/60 truncate max-w-[200px]">{entry.reason}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${entry.status === 'active' ? 'bg-red-500/10 text-red-400' : 'bg-gray-500/10 text-gray-400'}`}>
                        {entry.status}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <div className="flex justify-end gap-2 text-white/40">
                        <button className="hover:text-white p-1"><Edit2 size={16} /></button>
                        <button className="hover:text-red-400 p-1"><Trash2 size={16} /></button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <Pagination page={page} pages={Math.ceil(total / 20)} total={total} pageSize={20} onPageChange={setPage} />
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Add to Blacklist">
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-1">Address</label>
            <input required type="text" value={formData.address} onChange={e => setFormData({...formData, address: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-primary-500 outline-none" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm text-white/60 mb-1">Blockchain</label>
              <select value={formData.blockchain} onChange={e => setFormData({...formData, blockchain: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none">
                <option value="ethereum">Ethereum</option>
                <option value="bitcoin">Bitcoin</option>
                <option value="polygon">Polygon</option>
              </select>
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Category</label>
              <select value={formData.category} onChange={e => setFormData({...formData, category: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none">
                <option value="scam">Scam</option>
                <option value="mixer">Mixer</option>
                <option value="darknet">Darknet</option>
              </select>
            </div>
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Reason</label>
            <textarea required rows="3" value={formData.reason} onChange={e => setFormData({...formData, reason: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-primary-500 outline-none" />
          </div>
          <div className="pt-4 flex justify-end gap-3">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-white/60 hover:text-white transition-colors">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors">Save Entry</button>
          </div>
        </form>
      </Modal>
    </PageWrapper>
  )
}
