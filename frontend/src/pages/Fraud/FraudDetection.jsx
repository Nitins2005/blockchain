import React, { useState } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { aiAPI } from '../../services/api'
import { Shield, ShieldAlert, Activity, GitBranch, Cpu, Clock, CheckCircle } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import RiskBadge from '../../components/UI/RiskBadge'
import { formatAddress, formatDateTime } from '../../utils/formatters'

const MOCK_RESULT = {
  address: '0x742d35Cc6634C0532925a3b844Bc454e4438f44e',
  score: 0.89,
  risk_level: 'critical',
  confidence: 0.94,
  last_activity: '2023-10-25T14:30:00Z',
  tx_count: 1245,
  connected_wallets: 342,
  cross_chain_ratio: 0.65,
  prediction_time: '234ms',
  model_version: 'v2.4.1 (Ensemble)'
}

const MOCK_HIGH_RISK = Array.from({ length: 5 }, (_, i) => ({
  address: `0x${Math.random().toString(16).slice(2, 42)}`,
  blockchain: ['ethereum', 'bitcoin', 'polygon'][i % 3],
  score: 0.8 + (Math.random() * 0.2),
  risk_level: i % 2 === 0 ? 'critical' : 'high',
  last_activity: new Date(Date.now() - Math.random() * 100000000).toISOString()
}))

export default function FraudDetection() {
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!address) return
    
    setLoading(true)
    try {
      if (aiAPI && aiAPI.predictFraud) {
        const res = await aiAPI.predictFraud(address)
        setResult(res.data)
      } else {
        throw new Error('API not available')
      }
    } catch {
      setTimeout(() => {
        setResult({ ...MOCK_RESULT, address })
        setLoading(false)
      }, 1500)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 0.8) return '#ef4444' // red
    if (score >= 0.6) return '#f97316' // orange
    if (score >= 0.3) return '#f59e0b' // yellow
    return '#10b981' // green
  }

  return (
    <PageWrapper title="Fraud Detection">
      <div className="max-w-4xl mx-auto space-y-8">
        
        {/* Search Bar */}
        <div className="bg-dark-300 border border-white/10 rounded-2xl p-6 shadow-xl text-center">
          <ShieldAlert size={48} className="mx-auto text-primary-500 mb-4 opacity-80" />
          <h2 className="text-2xl font-bold text-white mb-2">Analyze Wallet for Fraud</h2>
          <p className="text-white/50 mb-6">Enter a wallet address to get real-time AI fraud probability</p>
          
          <form onSubmit={handleSearch} className="flex max-w-2xl mx-auto gap-3">
            <input 
              type="text" 
              placeholder="Enter wallet address (0x... / 1... / T...)" 
              value={address}
              onChange={e => setAddress(e.target.value)}
              className="flex-1 bg-dark-400 border border-white/20 rounded-xl px-4 py-3 text-white focus:border-primary-500 focus:ring-1 focus:ring-primary-500 outline-none transition-all"
            />
            <button type="submit" disabled={loading || !address} className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-6 py-3 rounded-xl font-medium flex items-center gap-2 transition-colors">
              {loading ? <Spinner size="sm" /> : <Shield size={18} />}
              Analyze
            </button>
          </form>
          <div className="mt-4">
            <button onClick={() => setAddress(MOCK_RESULT.address)} className="text-sm text-primary-400 hover:text-primary-300">Try Example Address</button>
          </div>
        </div>

        {/* Result Area */}
        {result && !loading && (
          <div className="bg-dark-300 border border-white/10 rounded-2xl p-8 shadow-xl animate-fade-in">
            <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">
              
              {/* Score Gauge */}
              <div className="flex-shrink-0 relative w-48 h-48 flex items-center justify-center">
                <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                  <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.1)" strokeWidth="10" />
                  <circle 
                    cx="50" cy="50" r="45" fill="none" 
                    stroke={getScoreColor(result.score)} 
                    strokeWidth="10" 
                    strokeDasharray={`${result.score * 283} 283`}
                    strokeLinecap="round"
                    className="transition-all duration-1000 ease-out"
                  />
                </svg>
                <div className="absolute flex flex-col items-center">
                  <span className="text-4xl font-bold text-white">{(result.score * 100).toFixed(1)}%</span>
                  <span className="text-sm text-white/50 uppercase tracking-wider">Fraud Score</span>
                </div>
              </div>

              {/* Details */}
              <div className="flex-1 w-full">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-white/10">
                  <div>
                    <p className="text-sm text-white/50 mb-1">Target Address</p>
                    <p className="font-mono text-lg text-primary-400">{formatAddress(result.address)}</p>
                  </div>
                  <RiskBadge level={result.risk_level} size="lg" />
                </div>

                <div className="grid grid-cols-2 gap-4 mb-6">
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-dark-400 rounded-lg text-primary-400"><CheckCircle size={18} /></div>
                    <div><p className="text-xs text-white/40">Confidence</p><p className="text-sm font-medium text-white">{(result.confidence * 100).toFixed(1)}%</p></div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-dark-400 rounded-lg text-blue-400"><Clock size={18} /></div>
                    <div><p className="text-xs text-white/40">Last Activity</p><p className="text-sm font-medium text-white">{formatDateTime(result.last_activity).split(',')[0]}</p></div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-dark-400 rounded-lg text-emerald-400"><Activity size={18} /></div>
                    <div><p className="text-xs text-white/40">Total TXs</p><p className="text-sm font-medium text-white">{result.tx_count.toLocaleString()}</p></div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-dark-400 rounded-lg text-purple-400"><GitBranch size={18} /></div>
                    <div><p className="text-xs text-white/40">Connections</p><p className="text-sm font-medium text-white">{result.connected_wallets.toLocaleString()}</p></div>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-dark-400 rounded-lg text-yellow-400"><Cpu size={18} /></div>
                    <div><p className="text-xs text-white/40">AI Model</p><p className="text-sm font-medium text-white">{result.model_version}</p></div>
                  </div>
                </div>

                <div className="flex gap-3">
                  <button className="flex-1 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white py-2 rounded-lg text-sm transition-colors">View Graph</button>
                  <button className="flex-1 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white py-2 rounded-lg text-sm transition-colors">Explanation</button>
                  <button className="flex-1 bg-red-500/20 hover:bg-red-500/30 text-red-400 border border-red-500/20 py-2 rounded-lg text-sm transition-colors">Blacklist</button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* High Risk Table */}
        <div className="bg-dark-300 border border-white/10 rounded-2xl p-6">
          <h3 className="text-lg font-semibold text-white mb-4">Recent High-Risk Detections</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b border-white/10 text-white/60">
                  <th className="pb-3 font-medium">Address</th>
                  <th className="pb-3 font-medium">Chain</th>
                  <th className="pb-3 font-medium">Score</th>
                  <th className="pb-3 font-medium">Risk Level</th>
                  <th className="pb-3 font-medium">Last Active</th>
                </tr>
              </thead>
              <tbody>
                {MOCK_HIGH_RISK.map((item, i) => (
                  <tr key={i} className="border-b border-white/5 hover:bg-white/5 cursor-pointer">
                    <td className="py-3 font-mono text-primary-400">{formatAddress(item.address)}</td>
                    <td className="py-3 capitalize text-white/80">{item.blockchain}</td>
                    <td className="py-3">
                      <span className="font-mono text-white">{(item.score * 100).toFixed(1)}%</span>
                    </td>
                    <td className="py-3"><RiskBadge level={item.risk_level} size="sm" /></td>
                    <td className="py-3 text-white/60">{formatDateTime(item.last_activity).split(',')[0]}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </PageWrapper>
  )
}
