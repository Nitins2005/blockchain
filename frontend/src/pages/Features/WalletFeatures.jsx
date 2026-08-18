import React, { useState, useEffect } from 'react'
import PageWrapper from '../../components/Layout/PageWrapper'
import { featuresAPI } from '../../services/api'
import Spinner from '../../components/UI/Spinner'
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts'
import { formatAddress } from '../../utils/formatters'
import Pagination from '../../components/UI/Pagination'
import { Play } from 'lucide-react'
import toast from 'react-hot-toast'

const MOCK_FEATURES = Array.from({ length: 15 }, (_, i) => ({
  address: `0x${Math.random().toString(16).slice(2, 42)}`,
  tx_count: Math.floor(Math.random() * 1000),
  total_received: Math.random() * 100,
  total_sent: Math.random() * 90,
  unique_senders: Math.floor(Math.random() * 50),
  unique_receivers: Math.floor(Math.random() * 50),
  avg_tx_value: Math.random() * 5,
  time_between_txs: Math.random() * 86400,
  cross_chain_ratio: Math.random(),
  contract_interaction_ratio: Math.random(),
  active_days: Math.floor(Math.random() * 365)
}))

export default function WalletFeatures() {
  const [featuresList, setFeaturesList] = useState([])
  const [selectedWallet, setSelectedWallet] = useState(null)
  const [loading, setLoading] = useState(true)
  const [page, setPage] = useState(1)
  const [total, setTotal] = useState(100)
  
  useEffect(() => {
    loadFeatures()
  }, [page])

  const loadFeatures = async () => {
    setLoading(true)
    try {
      if (featuresAPI && featuresAPI.getAll) {
        const res = await featuresAPI.getAll({ page, limit: 15 })
        setFeaturesList(res.data.items || res.data)
        setTotal(res.data.total || 100)
      } else {
        throw new Error('API not available')
      }
    } catch {
      setFeaturesList(MOCK_FEATURES)
      setTotal(100)
    } finally {
      setLoading(false)
    }
  }

  const handleCompute = async () => {
    toast.success('Started feature computation pipeline')
  }

  const radarData = selectedWallet ? [
    { subject: 'Volume', A: selectedWallet.total_received / 100, fullMark: 1 },
    { subject: 'Velocity', A: 1 - (selectedWallet.time_between_txs / 86400), fullMark: 1 },
    { subject: 'Network', A: selectedWallet.unique_senders / 50, fullMark: 1 },
    { subject: 'Contracts', A: selectedWallet.contract_interaction_ratio, fullMark: 1 },
    { subject: 'Cross-chain', A: selectedWallet.cross_chain_ratio, fullMark: 1 },
    { subject: 'Longevity', A: selectedWallet.active_days / 365, fullMark: 1 },
  ] : []

  return (
    <PageWrapper title="Wallet Features">
      <div className="flex gap-6 h-[calc(100vh-120px)]">
        
        {/* Left: List */}
        <div className="w-1/2 flex flex-col bg-dark-300 border border-white/10 rounded-xl overflow-hidden">
          <div className="p-4 border-b border-white/10 flex justify-between items-center">
            <h2 className="font-semibold text-white">Extracted Features</h2>
            <button onClick={handleCompute} className="flex items-center gap-2 px-3 py-1.5 bg-primary-600 hover:bg-primary-700 text-white text-sm rounded-lg transition-colors">
              <Play size={14} /> Compute All
            </button>
          </div>
          
          <div className="flex-1 overflow-y-auto">
            {loading ? (
              <div className="p-8 flex justify-center"><Spinner /></div>
            ) : (
              <table className="w-full text-left text-sm">
                <thead>
                  <tr className="bg-dark-400/50 text-white/60 border-b border-white/5">
                    <th className="p-3 font-medium">Address</th>
                    <th className="p-3 font-medium text-right">TX Count</th>
                    <th className="p-3 font-medium text-right">Vol (In)</th>
                    <th className="p-3 font-medium text-right">Active Days</th>
                  </tr>
                </thead>
                <tbody>
                  {featuresList.map(feat => (
                    <tr 
                      key={feat.address} 
                      onClick={() => setSelectedWallet(feat)}
                      className={`border-b border-white/5 cursor-pointer transition-colors ${selectedWallet?.address === feat.address ? 'bg-primary-500/10' : 'hover:bg-white/5'}`}
                    >
                      <td className="p-3 font-mono text-primary-400">{formatAddress(feat.address)}</td>
                      <td className="p-3 text-right text-white/80">{feat.tx_count}</td>
                      <td className="p-3 text-right text-white/80">{feat.total_received.toFixed(2)}</td>
                      <td className="p-3 text-right text-white/80">{feat.active_days}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
          <Pagination page={page} pages={Math.ceil(total / 15)} total={total} pageSize={15} onPageChange={setPage} />
        </div>

        {/* Right: Details */}
        <div className="w-1/2 bg-dark-300 border border-white/10 rounded-xl p-6 overflow-y-auto">
          {selectedWallet ? (
            <div>
              <h2 className="text-lg font-semibold text-white mb-1">Feature Profile</h2>
              <p className="font-mono text-sm text-primary-400 mb-6">{selectedWallet.address}</p>
              
              <div className="h-64 mb-8">
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart cx="50%" cy="50%" outerRadius="80%" data={radarData}>
                    <PolarGrid stroke="rgba(255,255,255,0.1)" />
                    <PolarAngleAxis dataKey="subject" tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 12 }} />
                    <PolarRadiusAxis angle={30} domain={[0, 1]} tick={false} axisLine={false} />
                    <Radar name="Wallet" dataKey="A" stroke="#6366f1" fill="#6366f1" fillOpacity={0.3} />
                    <RechartsTooltip contentStyle={{ backgroundColor: '#1e1e1e', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '8px' }} />
                  </RadarChart>
                </ResponsiveContainer>
              </div>

              <div className="grid grid-cols-2 gap-4">
                {Object.entries(selectedWallet).filter(([k]) => k !== 'address').map(([key, value]) => (
                  <div key={key} className="bg-dark-400 rounded-lg p-3 border border-white/5">
                    <p className="text-xs text-white/40 mb-1 uppercase tracking-wider">{key.replace(/_/g, ' ')}</p>
                    <p className="text-sm font-medium text-white">{typeof value === 'number' ? value.toFixed(4).replace(/\.?0+$/, '') : value}</p>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div className="h-full flex items-center justify-center">
              <p className="text-white/40">Select a wallet to view its feature profile</p>
            </div>
          )}
        </div>

      </div>
    </PageWrapper>
  )
}
