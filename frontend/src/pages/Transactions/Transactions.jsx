import React, { useState, useEffect } from 'react'
import { transactionsAPI } from '../../services/api'
import { formatAddress, formatAmount, formatDateTime } from '../../utils/formatters'
import { Search, Download, Upload, Filter, AlertTriangle, X } from 'lucide-react'
import PageWrapper from '../../components/Layout/PageWrapper'
import Pagination from '../../components/UI/Pagination'
import Spinner from '../../components/UI/Spinner'

const MOCK_TRANSACTIONS = Array.from({ length: 20 }, (_, i) => ({
  id: `tx-${i}`,
  hash: `0x${Math.random().toString(16).slice(2, 42)}`,
  from: `0x${Math.random().toString(16).slice(2, 42)}`,
  to: `0x${Math.random().toString(16).slice(2, 42)}`,
  blockchain: ['ethereum', 'bitcoin', 'polygon'][i % 3],
  amount: Math.random() * 10,
  usdValue: Math.random() * 20000,
  gas: Math.random() * 0.05,
  token: ['ETH', 'BTC', 'MATIC'][i % 3],
  timestamp: new Date(Date.now() - Math.random() * 10000000000).toISOString(),
  status: i % 5 === 0 ? 'failed' : 'success',
  flagged: i % 7 === 0
}))

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(20)
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState({ search: '', blockchain: '', status: '', token: '' })
  
  useEffect(() => {
    loadData()
  }, [page, filters])

  const loadData = async () => {
    setLoading(true)
    try {
      if (transactionsAPI && transactionsAPI.getAll) {
        const res = await transactionsAPI.getAll({ page, limit: pageSize, ...filters })
        setTransactions(res.data.items || res.data)
        setTotal(res.data.total || 100)
      } else {
        throw new Error('API not found')
      }
    } catch {
      setTransactions(MOCK_TRANSACTIONS)
      setTotal(100)
    } finally {
      setLoading(false)
    }
  }

  const handleExport = async () => {
    try {
      if (transactionsAPI && transactionsAPI.export) {
        await transactionsAPI.export()
      } else {
        const blob = new Blob(['mock csv content'], { type: 'text/csv' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        a.download = 'transactions.csv'
        a.click()
      }
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <PageWrapper title="Transactions">
      <div className="bg-dark-300 border border-white/10 rounded-xl flex flex-col">
        {/* Filters */}
        <div className="p-4 border-b border-white/10 flex flex-wrap gap-4 items-center">
          <div className="relative flex-1 min-w-[200px]">
            <Search size={18} className="absolute left-3 top-2.5 text-white/40" />
            <input 
              type="text" 
              placeholder="Search hash or address..." 
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
              className="w-full bg-dark-400 border border-white/10 rounded-lg pl-10 pr-3 py-2 text-white focus:border-primary-500 outline-none"
            />
          </div>
          
          <select 
            value={filters.blockchain}
            onChange={(e) => setFilters(prev => ({ ...prev, blockchain: e.target.value }))}
            className="bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none"
          >
            <option value="">All Chains</option>
            <option value="ethereum">Ethereum</option>
            <option value="bitcoin">Bitcoin</option>
          </select>

          <select 
            value={filters.status}
            onChange={(e) => setFilters(prev => ({ ...prev, status: e.target.value }))}
            className="bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none"
          >
            <option value="">All Statuses</option>
            <option value="success">Success</option>
            <option value="failed">Failed</option>
          </select>

          <button 
            onClick={() => setFilters({ search: '', blockchain: '', status: '', token: '' })}
            className="p-2 text-white/40 hover:text-white bg-dark-400 border border-white/10 rounded-lg"
            title="Clear Filters"
          >
            <X size={18} />
          </button>

          <div className="ml-auto flex gap-2">
            <button className="flex items-center gap-2 px-3 py-2 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white rounded-lg transition-colors">
              <Upload size={16} /> Upload
            </button>
            <button onClick={handleExport} className="flex items-center gap-2 px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors">
              <Download size={16} /> Export
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 flex justify-center"><Spinner /></div>
          ) : (
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-dark-400/50 border-b border-white/10 text-white/60 text-sm">
                  <th className="p-4 font-medium">Hash</th>
                  <th className="p-4 font-medium">From</th>
                  <th className="p-4 font-medium">To</th>
                  <th className="p-4 font-medium">Chain</th>
                  <th className="p-4 font-medium">Amount</th>
                  <th className="p-4 font-medium">Time</th>
                  <th className="p-4 font-medium">Status</th>
                </tr>
              </thead>
              <tbody>
                {transactions.map(tx => (
                  <tr key={tx.id} className={`border-b border-white/5 hover:bg-white/5 cursor-pointer ${tx.flagged ? 'border-l-2 border-l-red-500' : ''}`}>
                    <td className="p-4">
                      <div className="flex items-center gap-2">
                        {tx.flagged && <AlertTriangle size={14} className="text-red-500" />}
                        <span className="font-mono text-sm text-primary-400">{formatAddress(tx.hash)}</span>
                      </div>
                    </td>
                    <td className="p-4 font-mono text-sm text-white/80">{formatAddress(tx.from)}</td>
                    <td className="p-4 font-mono text-sm text-white/80">{formatAddress(tx.to)}</td>
                    <td className="p-4">
                      <span className="px-2 py-1 bg-dark-400 rounded-md text-xs text-white/70 capitalize">{tx.blockchain}</span>
                    </td>
                    <td className="p-4">
                      <p className="text-sm text-white">{formatAmount(tx.amount)} {tx.token}</p>
                      <p className="text-xs text-white/40">${formatAmount(tx.usdValue)}</p>
                    </td>
                    <td className="p-4 text-sm text-white/60">{formatDateTime(tx.timestamp)}</td>
                    <td className="p-4">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${tx.status === 'success' ? 'bg-emerald-500/10 text-emerald-400' : 'bg-red-500/10 text-red-400'}`}>
                        {tx.status}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        <Pagination 
          page={page} 
          pages={Math.ceil(total / pageSize)} 
          total={total} 
          pageSize={pageSize} 
          onPageChange={setPage} 
        />
      </div>
    </PageWrapper>
  )
}
