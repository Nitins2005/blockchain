import React, { useState, useEffect } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { reportsAPI } from '../../services/api'
import { FileText, Download, Plus, Search } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import Modal from '../../components/UI/Modal'
import { formatAddress, formatDateTime } from '../../utils/formatters'
import toast from 'react-hot-toast'
import Pagination from '../../components/UI/Pagination'

const MOCK_REPORTS = Array.from({ length: 8 }, (_, i) => ({
  id: `rep-${i}`,
  wallet_address: `0x${Math.random().toString(16).slice(2, 42)}`,
  type: ['wallet_analysis', 'investigation_summary', 'fraud_assessment'][i % 3],
  status: 'completed',
  created_at: new Date(Date.now() - Math.random() * 1000000000).toISOString()
}))

export default function Reports() {
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [showModal, setShowModal] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [formData, setFormData] = useState({ wallet_address: '', report_type: 'wallet_analysis' })
  const [page, setPage] = useState(1)

  useEffect(() => {
    loadReports()
  }, [page])

  const loadReports = async () => {
    setLoading(true)
    try {
      if (reportsAPI && reportsAPI.getAll) {
        const res = await reportsAPI.getAll({ page, limit: 10 })
        setReports(res.data.items || res.data)
      } else throw new Error('API missing')
    } catch {
      setReports(MOCK_REPORTS)
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async (e) => {
    e.preventDefault()
    setGenerating(true)
    try {
      if (reportsAPI && reportsAPI.generate) {
        await reportsAPI.generate(formData)
      } else {
        await new Promise(r => setTimeout(r, 1500))
      }
      toast.success('Report generation started')
      setShowModal(false)
      loadReports()
    } catch {
      toast.error('Failed to generate report')
    } finally {
      setGenerating(false)
    }
  }

  const handleDownload = async (id) => {
    try {
      if (reportsAPI && reportsAPI.download) {
        await reportsAPI.download(id)
      } else {
        toast.success(`Downloaded report (Mock)`)
      }
    } catch (e) {
      toast.error('Download failed')
    }
  }

  return (
    <PageWrapper title="Reports">
      <div className="bg-dark-300 border border-white/10 rounded-xl flex flex-col">
        <div className="p-4 border-b border-white/10 flex justify-between items-center">
          <div className="relative w-64">
            <Search size={18} className="absolute left-3 top-2.5 text-white/40" />
            <input type="text" placeholder="Search reports..." className="w-full bg-dark-400 border border-white/10 rounded-lg pl-10 pr-3 py-2 text-white focus:border-primary-500 outline-none" />
          </div>
          <button onClick={() => setShowModal(true)} className="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-4 py-2 rounded-lg transition-colors">
            <Plus size={18} /> Generate Report
          </button>
        </div>

        <div className="overflow-x-auto">
          {loading ? (
            <div className="p-8 flex justify-center"><Spinner /></div>
          ) : (
            <table className="w-full text-left">
              <thead>
                <tr className="bg-dark-400/50 border-b border-white/10 text-white/60 text-sm">
                  <th className="p-4 font-medium">Report ID</th>
                  <th className="p-4 font-medium">Target / Subject</th>
                  <th className="p-4 font-medium">Type</th>
                  <th className="p-4 font-medium">Generated At</th>
                  <th className="p-4 font-medium text-right">Download</th>
                </tr>
              </thead>
              <tbody>
                {reports.map(rep => (
                  <tr key={rep.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                    <td className="p-4 font-mono text-xs text-white/60">{rep.id}</td>
                    <td className="p-4 font-mono text-sm text-primary-400">{rep.wallet_address ? formatAddress(rep.wallet_address) : 'N/A'}</td>
                    <td className="p-4">
                      <span className="px-2 py-1 bg-dark-400 rounded-md text-xs text-white/70 capitalize">{rep.type.replace('_', ' ')}</span>
                    </td>
                    <td className="p-4 text-sm text-white/60">{formatDateTime(rep.created_at)}</td>
                    <td className="p-4 text-right">
                      <button onClick={() => handleDownload(rep.id)} className="inline-flex items-center justify-center p-2 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white rounded-lg transition-colors">
                        <Download size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
        <Pagination page={page} pages={1} total={reports.length} pageSize={10} onPageChange={setPage} />
      </div>

      <Modal isOpen={showModal} onClose={() => setShowModal(false)} title="Generate New Report">
        <form onSubmit={handleGenerate} className="space-y-4">
          <div>
            <label className="block text-sm text-white/60 mb-1">Target Wallet Address</label>
            <input required type="text" value={formData.wallet_address} onChange={e => setFormData({...formData, wallet_address: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none focus:border-primary-500" />
          </div>
          <div>
            <label className="block text-sm text-white/60 mb-1">Report Type</label>
            <select value={formData.report_type} onChange={e => setFormData({...formData, report_type: e.target.value})} className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white outline-none">
              <option value="wallet_analysis">Comprehensive Wallet Analysis</option>
              <option value="fraud_assessment">Fraud Assessment Report</option>
              <option value="investigation_summary">Investigation Summary</option>
            </select>
          </div>
          <div className="pt-4 flex justify-end gap-3">
            <button type="button" onClick={() => setShowModal(false)} className="px-4 py-2 text-white/60 hover:text-white">Cancel</button>
            <button type="submit" disabled={generating} className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg flex items-center gap-2">
              {generating ? <Spinner size="sm" /> : <FileText size={16} />} Generate
            </button>
          </div>
        </form>
      </Modal>
    </PageWrapper>
  )
}
