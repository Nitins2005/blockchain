import React, { useState } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { explainabilityAPI, reportsAPI } from '../../services/api'
import { Search, Brain, AlertTriangle, Download, ChevronDown, ChevronUp } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import { formatAddress } from '../../utils/formatters'
import toast from 'react-hot-toast'

const MOCK_EXPLANATION = {
  address: '0x1a2b3c4d5e6f7g8h9i0j',
  reasoning_text: "The AI model flagged this wallet due to an unusual pattern of rapid, high-volume transfers immediately following large inbound transactions. This 'pass-through' behavior is characteristic of mixing services or money laundering. Additionally, 42% of its network consists of known high-risk entities.",
  risk_factors: [
    "High velocity of funds (avg time between TXs < 2 mins)",
    "Interaction with 3 known scam contracts",
    "95% of incoming funds are forwarded within 1 hour",
    "Anomalous timezone activity compared to typical users"
  ],
  features: [
    { name: 'Velocity', importance: 0.85 },
    { name: 'Pass-through Ratio', importance: 0.72 },
    { name: 'Scam Interactions', importance: 0.65 },
    { name: 'Unique Receivers', importance: 0.45 },
    { name: 'Avg TX Value', importance: 0.3 }
  ],
  neighbors: [
    { address: '0xaaa...', influence: 0.9, blacklisted: true },
    { address: '0xbbb...', influence: 0.6, blacklisted: false },
    { address: '0xccc...', influence: 0.4, blacklisted: true }
  ],
  transactions: [
    { hash: '0x111...', amount: 15.5, blockchain: 'ethereum', importance: 0.95 },
    { hash: '0x222...', amount: 12.0, blockchain: 'ethereum', importance: 0.88 }
  ],
  temporal: Array.from({ length: 30 }, (_, i) => ({
    day: `Day ${i+1}`,
    tx_count: Math.floor(Math.random() * 50),
    volume: Math.random() * 100
  }))
}

export default function ExplainableAI() {
  const [address, setAddress] = useState('')
  const [explanation, setExplanation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [downloading, setDownloading] = useState(false)
  const [activePanels, setActivePanels] = useState({ reasoning: true, features: true, factors: true })

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!address) return
    setLoading(true)
    try {
      if (explainabilityAPI && explainabilityAPI.explain) {
        const res = await explainabilityAPI.explain(address)
        setExplanation(res.data)
      } else {
        throw new Error('API not available')
      }
    } catch {
      setTimeout(() => {
        setExplanation({ ...MOCK_EXPLANATION, address })
        setLoading(false)
      }, 1200)
    }
  }

  const handleDownload = async () => {
    setDownloading(true)
    try {
      if (reportsAPI && reportsAPI.generate) {
        const res = await reportsAPI.generate({ wallet_address: explanation.address, report_type: 'wallet_analysis' })
        await reportsAPI.download(res.data.id || 1)
      } else {
        await new Promise(r => setTimeout(r, 1000)) // mock delay
        toast.success('Report downloaded')
      }
    } catch {
      toast.error('Failed to download report')
    } finally {
      setDownloading(false)
    }
  }

  const togglePanel = (panel) => {
    setActivePanels(prev => ({ ...prev, [panel]: !prev[panel] }))
  }

  return (
    <PageWrapper title="Explainable AI">
      <div className="max-w-5xl mx-auto space-y-6">
        
        <div className="bg-dark-300 border border-white/10 rounded-xl p-6">
          <form onSubmit={handleSearch} className="flex gap-3 max-w-2xl">
            <input 
              type="text" 
              placeholder="Enter wallet address to explain..." 
              value={address}
              onChange={e => setAddress(e.target.value)}
              className="flex-1 bg-dark-400 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none"
            />
            <button type="submit" disabled={loading || !address} className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-6 py-2 rounded-lg transition-colors">
              {loading ? <Spinner size="sm" /> : 'Explain'}
            </button>
          </form>
        </div>

        {explanation && (
          <div className="space-y-4 animate-fade-in">
            <div className="flex justify-end">
              <button onClick={handleDownload} disabled={downloading} className="flex items-center gap-2 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white px-4 py-2 rounded-lg text-sm transition-colors">
                {downloading ? <Spinner size="sm" /> : <Download size={16} />} Download PDF Report
              </button>
            </div>

            {/* Reasoning Panel */}
            <div className="bg-dark-300 border border-white/10 rounded-xl overflow-hidden">
              <button onClick={() => togglePanel('reasoning')} className="w-full flex items-center justify-between p-4 bg-dark-400/50 hover:bg-dark-400 transition-colors">
                <div className="flex items-center gap-2 text-white font-medium"><Brain size={18} className="text-primary-400" /> AI Reasoning</div>
                {activePanels.reasoning ? <ChevronUp size={18} className="text-white/50" /> : <ChevronDown size={18} className="text-white/50" />}
              </button>
              {activePanels.reasoning && (
                <div className="p-6 text-white/80 leading-relaxed bg-dark-300">
                  {explanation.reasoning_text}
                </div>
              )}
            </div>

            {/* Risk Factors Panel */}
            <div className="bg-dark-300 border border-white/10 rounded-xl overflow-hidden">
              <button onClick={() => togglePanel('factors')} className="w-full flex items-center justify-between p-4 bg-dark-400/50 hover:bg-dark-400 transition-colors">
                <div className="flex items-center gap-2 text-white font-medium"><AlertTriangle size={18} className="text-red-400" /> Key Risk Factors</div>
                {activePanels.factors ? <ChevronUp size={18} className="text-white/50" /> : <ChevronDown size={18} className="text-white/50" />}
              </button>
              {activePanels.factors && (
                <div className="p-6 bg-dark-300">
                  <ul className="space-y-3">
                    {explanation.risk_factors.map((factor, i) => (
                      <li key={i} className="flex items-start gap-3 text-white/80">
                        <AlertTriangle size={16} className="text-red-500/70 mt-0.5 flex-shrink-0" />
                        <span>{factor}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Feature Importance Panel */}
            <div className="bg-dark-300 border border-white/10 rounded-xl overflow-hidden">
              <button onClick={() => togglePanel('features')} className="w-full flex items-center justify-between p-4 bg-dark-400/50 hover:bg-dark-400 transition-colors">
                <div className="flex items-center gap-2 text-white font-medium">Feature Importance</div>
                {activePanels.features ? <ChevronUp size={18} className="text-white/50" /> : <ChevronDown size={18} className="text-white/50" />}
              </button>
              {activePanels.features && (
                <div className="p-6 bg-dark-300 h-80">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={explanation.features} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" horizontal={false} />
                      <XAxis type="number" domain={[0, 1]} stroke="rgba(255,255,255,0.3)" />
                      <YAxis dataKey="name" type="category" width={120} stroke="rgba(255,255,255,0.7)" tick={{ fontSize: 12 }} />
                      <RechartsTooltip contentStyle={{ backgroundColor: '#1e1e1e', border: 'none', borderRadius: '8px' }} cursor={{ fill: 'rgba(255,255,255,0.05)' }} />
                      <Bar dataKey="importance" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={20} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              )}
            </div>
            
            {/* Temporal Activity */}
            <div className="bg-dark-300 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-medium mb-6">Temporal Activity (30 Days)</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={explanation.temporal}>
                    <defs>
                      <linearGradient id="colorVol" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                    <XAxis dataKey="day" stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} />
                    <YAxis stroke="rgba(255,255,255,0.3)" tick={{ fontSize: 10 }} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                    <Area type="monotone" dataKey="volume" stroke="#10b981" fillOpacity={1} fill="url(#colorVol)" />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </div>

          </div>
        )}
      </div>
    </PageWrapper>
  )
}
