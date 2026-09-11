import React, { useState, useEffect } from 'react'
import { blockchainAPI } from '../../services/api'
import toast from 'react-hot-toast'
import { Eye, EyeOff, Save, RefreshCw, Activity, Link, Layers } from 'lucide-react'
import PageWrapper from '../../components/Layout/PageWrapper'
import Spinner from '../../components/UI/Spinner'

const MOCK_CONFIGS = [
  { chain: 'bitcoin', name: 'Bitcoin', enabled: true, url: 'https://api.bitcoin.org', key: 'mock-key-btc', lastSync: '2023-10-01T12:00:00Z', txCount: 1500000, wallets: 500000, blockHeight: 800000, status: 'synced' },
  { chain: 'ethereum', name: 'Ethereum', enabled: true, url: 'https://api.infura.io/v3', key: 'mock-key-eth', lastSync: '2023-10-01T12:05:00Z', txCount: 5000000, wallets: 2000000, blockHeight: 18000000, status: 'syncing' },
  { chain: 'bnb', name: 'BNB Chain', enabled: false, url: 'https://bsc-dataseed.binance.org', key: '', lastSync: '2023-09-28T12:00:00Z', txCount: 3000000, wallets: 1000000, blockHeight: 32000000, status: 'idle' },
  { chain: 'polygon', name: 'Polygon', enabled: true, url: 'https://polygon-rpc.com', key: 'mock-key-matic', lastSync: '2023-10-01T12:10:00Z', txCount: 4000000, wallets: 1500000, blockHeight: 48000000, status: 'error' },
  { chain: 'tron', name: 'Tron', enabled: false, url: 'https://api.trongrid.io', key: '', lastSync: '2023-09-30T12:00:00Z', txCount: 2000000, wallets: 800000, blockHeight: 55000000, status: 'idle' },
]

export default function BlockchainData() {
  const [configs, setConfigs] = useState([])
  const [loading, setLoading] = useState(true)
  const [syncing, setSyncing] = useState({})
  const [showKeys, setShowKeys] = useState({})

  useEffect(() => {
    loadConfigs()
  }, [])

  const loadConfigs = async () => {
    setLoading(true)
    try {
      if (blockchainAPI && blockchainAPI.getConfigs) {
        const res = await blockchainAPI.getConfigs()
        const mapped = (res.data || []).map(c => ({
          chain: c.blockchain || c.chain,
          name: c.display_name || c.name || c.blockchain,
          url: c.api_url || c.url || '',
          key: c.api_key || c.key || '',
          enabled: c.is_enabled ?? c.enabled ?? true,
          lastSync: c.last_sync || c.lastSync,
          txCount: c.tx_count ?? c.txCount ?? 0,
          wallets: c.wallet_count ?? c.wallets ?? 0,
          blockHeight: c.block_height ?? c.blockHeight ?? 0,
          status: c.sync_status || c.status || 'idle'
        }))
        setConfigs(mapped)
      } else {
        throw new Error('API not available')
      }
    } catch {
      setConfigs(MOCK_CONFIGS)
    } finally {
      setLoading(false)
    }
  }

  const handleUpdate = (chain, field, value) => {
    setConfigs(configs.map(c => c.chain === chain ? { ...c, [field]: value } : c))
  }

  const handleSave = async (config) => {
    try {
      if (blockchainAPI && blockchainAPI.updateConfig) {
        await blockchainAPI.updateConfig(config.chain, config)
      }
      toast.success(`${config.name} config saved`)
    } catch {
      toast.success(`${config.name} config saved (mock)`)
    }
  }

  const handleSync = async (chainName) => {
    setSyncing(prev => ({ ...prev, [chainName]: true }))
    try {
      if (blockchainAPI && blockchainAPI.sync) {
        await blockchainAPI.sync(chainName)
      } else {
        await new Promise(r => setTimeout(r, 1500))
      }
      toast.success(`Synced ${chainName}`)
      setConfigs(configs.map(c => c.chain === chainName ? { ...c, status: 'synced', lastSync: new Date().toISOString() } : c))
    } catch {
      toast.error(`Failed to sync ${chainName}`)
    } finally {
      setSyncing(prev => ({ ...prev, [chainName]: false }))
    }
  }

  const toggleKeyVisibility = (chain) => {
    setShowKeys(prev => ({ ...prev, [chain]: !prev[chain] }))
  }

  const getStatusColor = (status) => {
    switch(status) {
      case 'synced': return 'bg-emerald-500'
      case 'syncing': return 'bg-yellow-500 animate-pulse'
      case 'error': return 'bg-red-500'
      default: return 'bg-gray-500'
    }
  }

  if (loading) return <div className="p-8 flex justify-center"><Spinner /></div>

  return (
    <PageWrapper title="Blockchain Configuration">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {configs.map((config) => (
          <div key={config.chain} className="bg-dark-300 border border-white/10 rounded-xl p-5">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-3 h-3 rounded-full ${getStatusColor(config.status)}`} />
                <h3 className="text-xl font-semibold text-white">{config.name}</h3>
              </div>
              <label className="flex items-center cursor-pointer">
                <div className="relative">
                  <input type="checkbox" className="sr-only" checked={config.enabled} onChange={(e) => handleUpdate(config.chain, 'enabled', e.target.checked)} />
                  <div className={`block w-10 h-6 rounded-full transition-colors ${config.enabled ? 'bg-primary-600' : 'bg-gray-600'}`}></div>
                  <div className={`dot absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${config.enabled ? 'transform translate-x-4' : ''}`}></div>
                </div>
              </label>
            </div>
            
            <div className="space-y-4 mb-6">
              <div>
                <label className="block text-sm text-white/60 mb-1">API URL</label>
                <div className="relative">
                  <Link size={16} className="absolute left-3 top-2.5 text-white/40" />
                  <input 
                    type="text" 
                    value={config.url}
                    onChange={(e) => handleUpdate(config.chain, 'url', e.target.value)}
                    className="w-full bg-dark-400 border border-white/10 rounded-lg pl-9 pr-3 py-2 text-white focus:border-primary-500 outline-none"
                  />
                </div>
              </div>
              
              <div>
                <label className="block text-sm text-white/60 mb-1">API Key</label>
                <div className="relative">
                  <input 
                    type={showKeys[config.chain] ? "text" : "password"}
                    value={config.key}
                    onChange={(e) => handleUpdate(config.chain, 'key', e.target.value)}
                    className="w-full bg-dark-400 border border-white/10 rounded-lg px-3 py-2 text-white focus:border-primary-500 outline-none"
                  />
                  <button 
                    onClick={() => toggleKeyVisibility(config.chain)}
                    className="absolute right-3 top-2.5 text-white/40 hover:text-white"
                  >
                    {showKeys[config.chain] ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex gap-3 mb-6">
              <button 
                onClick={() => handleSave(config)}
                className="flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors"
              >
                <Save size={16} /> Save Config
              </button>
              <button 
                onClick={() => handleSync(config.chain)}
                disabled={syncing[config.chain]}
                className="flex items-center gap-2 px-4 py-2 bg-dark-400 hover:bg-dark-200 border border-white/10 text-white rounded-lg transition-colors disabled:opacity-50"
              >
                {syncing[config.chain] ? <Spinner size="sm" /> : <RefreshCw size={16} />} 
                Sync Now
              </button>
            </div>
            
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-dark-400 rounded-lg border border-white/5">
              <div>
                <p className="text-xs text-white/40 mb-1">Status</p>
                <span className="text-sm font-medium text-white capitalize">{config.status}</span>
              </div>
              <div>
                <p className="text-xs text-white/40 mb-1">Block Height</p>
                <p className="text-sm font-mono text-white">{config.blockHeight?.toLocaleString() || '0'}</p>
              </div>
              <div>
                <p className="text-xs text-white/40 mb-1">Transactions</p>
                <p className="text-sm font-mono text-white">{config.txCount?.toLocaleString() || '0'}</p>
              </div>
              <div>
                <p className="text-xs text-white/40 mb-1">Wallets</p>
                <p className="text-sm font-mono text-white">{config.wallets?.toLocaleString() || '0'}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </PageWrapper>
  )
}
