import React, { useState } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { attributionAPI } from '../../services/api'
import { WALLET_CATEGORIES } from '../../utils/constants'
import { Search, Building2, Cpu, AlertTriangle, EyeOff, Shuffle, ArrowLeftRight, Code2, Image as ImageIcon, User, HelpCircle } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { formatAddress } from '../../utils/formatters'

const CATEGORY_ICONS = {
  exchange: Building2,
  miner: Cpu,
  scam: AlertTriangle,
  mixer: Shuffle,
  dex: ArrowLeftRight,
  smart_contract: Code2,
  nft: ImageIcon,
  individual: User,
  darknet: EyeOff,
  unknown: HelpCircle
}

const MOCK_RESULT = {
  address: '0x1234567890abcdef1234567890abcdef12345678',
  primary_category: 'exchange',
  confidence: 0.92,
  secondary_categories: [
    { category: 'dex', confidence: 0.05 },
    { category: 'individual', confidence: 0.02 }
  ]
}

const MOCK_DISTRIBUTION = [
  { name: 'Exchange', value: 45, color: '#3b82f6' },
  { name: 'Individual', value: 30, color: '#10b981' },
  { name: 'Smart Contract', value: 15, color: '#8b5cf6' },
  { name: 'Mixer', value: 5, color: '#f59e0b' },
  { name: 'Scam', value: 5, color: '#ef4444' }
]

export default function WalletAttribution() {
  const [address, setAddress] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!address) return
    
    setLoading(true)
    try {
      if (attributionAPI && attributionAPI.predictCategory) {
        const res = await attributionAPI.predictCategory(address)
        setResult(res.data)
      } else {
        throw new Error('API not available')
      }
    } catch {
      setResult({ ...MOCK_RESULT, address })
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageWrapper title="Wallet Attribution">
      <div className="flex flex-col lg:flex-row gap-6">
        
        {/* Left: Search & Result */}
        <div className="w-full lg:w-2/3 space-y-6">
          <div className="bg-dark-300 border border-white/10 rounded-xl p-6">
            <h2 className="text-xl font-semibold text-white mb-4">Attribution Analysis</h2>
            <form onSubmit={handleSearch} className="flex gap-3">
              <input 
                type="text" 
                placeholder="Enter wallet address" 
                value={address}
                onChange={e => setAddress(e.target.value)}
                className="flex-1 bg-dark-400 border border-white/20 rounded-lg px-4 py-2 text-white focus:border-primary-500 outline-none"
              />
              <button type="submit" disabled={loading || !address} className="bg-primary-600 hover:bg-primary-700 disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors">
                {loading ? <Spinner size="sm" /> : 'Analyze'}
              </button>
            </form>
          </div>

          {result && (
            <div className="bg-dark-300 border border-white/10 rounded-xl p-6 animate-fade-in">
              <div className="flex items-start justify-between mb-8">
                <div>
                  <p className="text-sm text-white/50 mb-1">Target Address</p>
                  <p className="font-mono text-xl text-primary-400">{formatAddress(result.address)}</p>
                </div>
              </div>

              <div className="bg-dark-400 border border-white/5 rounded-xl p-6 mb-8 flex items-center gap-6">
                <div className="w-20 h-20 rounded-2xl bg-primary-500/10 flex items-center justify-center text-primary-400">
                  {React.createElement(CATEGORY_ICONS[result.primary_category] || HelpCircle, { size: 40 })}
                </div>
                <div className="flex-1">
                  <p className="text-sm text-white/50 mb-1 uppercase tracking-wider">Primary Category</p>
                  <h3 className="text-3xl font-bold text-white capitalize mb-3">{result.primary_category.replace('_', ' ')}</h3>
                  
                  <div className="space-y-1.5">
                    <div className="flex justify-between text-sm">
                      <span className="text-white/60">Confidence Score</span>
                      <span className="text-white font-medium">{(result.confidence * 100).toFixed(1)}%</span>
                    </div>
                    <div className="h-2 w-full bg-dark-200 rounded-full overflow-hidden">
                      <div className="h-full bg-primary-500 rounded-full" style={{ width: `${result.confidence * 100}%` }} />
                    </div>
                  </div>
                </div>
              </div>

              {result.secondary_categories?.length > 0 && (
                <div>
                  <h4 className="text-sm font-medium text-white/80 mb-4">Secondary Possibilities</h4>
                  <div className="space-y-4">
                    {result.secondary_categories.map((cat, i) => (
                      <div key={i} className="flex items-center gap-4">
                        <div className="w-10 h-10 rounded-lg bg-dark-400 flex items-center justify-center text-white/50">
                          {React.createElement(CATEGORY_ICONS[cat.category] || HelpCircle, { size: 20 })}
                        </div>
                        <div className="flex-1">
                          <div className="flex justify-between text-sm mb-1.5">
                            <span className="text-white capitalize">{cat.category.replace('_', ' ')}</span>
                            <span className="text-white/60 font-mono">{(cat.confidence * 100).toFixed(1)}%</span>
                          </div>
                          <div className="h-1.5 w-full bg-dark-200 rounded-full overflow-hidden">
                            <div className="h-full bg-white/20 rounded-full" style={{ width: `${cat.confidence * 100}%` }} />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Right: Distribution */}
        <div className="w-full lg:w-1/3 bg-dark-300 border border-white/10 rounded-xl p-6 flex flex-col">
          <h3 className="text-lg font-semibold text-white mb-6">Global Distribution</h3>
          <div className="flex-1 min-h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={MOCK_DISTRIBUTION}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {MOCK_DISTRIBUTION.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }}
                  itemStyle={{ color: '#fff' }}
                />
                <Legend verticalAlign="bottom" height={36} wrapperStyle={{ color: '#fff', fontSize: '12px' }} />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>
    </PageWrapper>
  )
}
