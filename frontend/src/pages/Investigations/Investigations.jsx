import React, { useState } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { investigationsAPI } from '../../services/api'
import { FolderOpen, Plus, Search, Calendar, User, ArrowLeft, Paperclip, MessageSquare } from 'lucide-react'
import Modal from '../../components/UI/Modal'
import { formatAddress, formatDate } from '../../utils/formatters'

const MOCK_INVESTIGATIONS = Array.from({ length: 8 }, (_, i) => ({
  id: `INV-2023-${1000+i}`,
  title: `Suspicious Exchange Activity #${i+1}`,
  status: ['open', 'in_progress', 'closed'][i % 3],
  priority: ['critical', 'high', 'medium', 'low'][i % 4],
  assigned_to: 'John Doe',
  wallet_count: Math.floor(Math.random() * 15) + 1,
  created_at: new Date(Date.now() - Math.random() * 10000000000).toISOString()
}))

export default function Investigations() {
  const [selectedInv, setSelectedInv] = useState(null)
  const [showCreateModal, setShowCreateModal] = useState(false)
  
  // List View
  if (!selectedInv) {
    return (
      <PageWrapper title="Investigations">
        <div className="flex justify-between items-center mb-6">
          <div className="relative w-64">
            <Search size={18} className="absolute left-3 top-2.5 text-white/40" />
            <input type="text" placeholder="Search cases..." className="w-full bg-dark-300 border border-white/10 rounded-lg pl-10 pr-3 py-2 text-white focus:border-primary-500 outline-none" />
          </div>
          <button onClick={() => setShowCreateModal(true)} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Plus size={18} /> Create Case
          </button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          {MOCK_INVESTIGATIONS.map(inv => (
            <div key={inv.id} onClick={() => setSelectedInv(inv)} className="bg-dark-300 border border-white/10 rounded-xl p-5 hover:border-primary-500/50 cursor-pointer transition-all">
              <div className="flex justify-between items-start mb-3">
                <span className="text-xs font-mono text-white/40">{inv.id}</span>
                <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${inv.status === 'open' ? 'bg-blue-500/10 text-blue-400' : inv.status === 'in_progress' ? 'bg-yellow-500/10 text-yellow-400' : 'bg-emerald-500/10 text-emerald-400'}`}>
                  {inv.status.replace('_', ' ').toUpperCase()}
                </span>
              </div>
              <h3 className="text-lg font-semibold text-white mb-4 line-clamp-1">{inv.title}</h3>
              <div className="space-y-2 text-sm text-white/60">
                <div className="flex items-center gap-2"><User size={14} /> {inv.assigned_to}</div>
                <div className="flex items-center gap-2"><FolderOpen size={14} /> {inv.wallet_count} Wallets attached</div>
                <div className="flex items-center gap-2"><Calendar size={14} /> {formatDate(inv.created_at)}</div>
              </div>
            </div>
          ))}
        </div>

        <Modal isOpen={showCreateModal} onClose={() => setShowCreateModal(false)} title="Create New Investigation Case">
          <form className="space-y-4">
            <div>
              <label className="block text-sm text-white/60 mb-1">Case Title</label>
              <input type="text" className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            </div>
            <div>
              <label className="block text-sm text-white/60 mb-1">Description</label>
              <textarea rows="3" className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            </div>
            <div className="pt-4 flex justify-end gap-3">
              <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 text-white/60 hover:text-white">Cancel</button>
              <button type="button" onClick={() => setShowCreateModal(false)} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg">Create Case</button>
            </div>
          </form>
        </Modal>
      </PageWrapper>
    )
  }

  // Detail View
  return (
    <PageWrapper title={`Case: ${selectedInv.id}`}>
      <div className="mb-4">
        <button onClick={() => setSelectedInv(null)} className="flex items-center gap-2 text-white/60 hover:text-white transition-colors">
          <ArrowLeft size={18} /> Back to Cases
        </button>
      </div>

      <div className="bg-dark-300 border border-white/10 rounded-xl p-6 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h2 className="text-2xl font-bold text-white mb-2">{selectedInv.title}</h2>
            <p className="text-white/60 text-sm">Created {formatDate(selectedInv.created_at)} by {selectedInv.assigned_to}</p>
          </div>
          <div className="flex gap-2">
            <button className="bg-dark-400 border border-white/10 text-white px-3 py-1.5 rounded-lg text-sm">Generate Report</button>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-dark-300 border border-white/10 rounded-xl p-5">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-white flex items-center gap-2"><Paperclip size={18} /> Attached Wallets</h3>
            <button className="text-primary-400 text-sm hover:text-primary-300">+ Add</button>
          </div>
          <div className="space-y-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="flex justify-between items-center p-3 bg-dark-400 rounded-lg border border-white/5">
                <span className="font-mono text-sm text-white/80">{formatAddress(`0x${Math.random().toString(16).slice(2, 42)}`)}</span>
                <span className="text-xs px-2 py-1 bg-red-500/10 text-red-400 rounded-full">High Risk</span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-dark-300 border border-white/10 rounded-xl p-5 flex flex-col h-[500px]">
          <h3 className="font-semibold text-white flex items-center gap-2 mb-4"><MessageSquare size={18} /> Case Notes</h3>
          <div className="flex-1 overflow-y-auto space-y-4 mb-4">
            <div className="bg-dark-400 p-3 rounded-lg border border-white/5">
              <p className="text-xs text-white/40 mb-1">John Doe - 2 hours ago</p>
              <p className="text-sm text-white/80">Identified connection to known Tornado Cash router.</p>
            </div>
          </div>
          <div className="flex gap-2">
            <input type="text" placeholder="Add a note..." className="flex-1 bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
            <button className="bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg">Post</button>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
