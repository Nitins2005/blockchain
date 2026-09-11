import React, { useState, useEffect } from 'react'
import { graphAPI } from '../../services/api'
import CytoscapeGraph from '../../components/Graph/CytoscapeGraph'
import PageWrapper from '../../components/Layout/PageWrapper'
import { Search, Layers, Activity, Share2, Hexagon } from 'lucide-react'
import Spinner from '../../components/UI/Spinner'

const MOCK_GRAPH = {
  nodes: Array.from({ length: 15 }, (_, i) => ({
    data: {
      id: `n${i}`,
      label: i === 0 ? 'Target Wallet' : `Wallet ${i}`,
      address: `0x${Math.random().toString(16).slice(2, 42)}`,
      is_center: i === 0,
      blockchain: 'ethereum',
      fraud_score: Math.random(),
      tx_count: Math.floor(Math.random() * 500),
      risk_level: i === 0 ? 'critical' : ['low', 'medium', 'high'][Math.floor(Math.random() * 3)],
      color: i === 0 ? '#ef4444' : ['#10b981', '#f59e0b', '#f97316'][Math.floor(Math.random() * 3)]
    }
  })),
  edges: Array.from({ length: 20 }, (_, i) => ({
    data: {
      id: `e${i}`,
      source: `n${Math.floor(Math.random() * 15)}`,
      target: `n${Math.floor(Math.random() * 15)}`,
      amount: Math.random() * 10
    }
  }))
}

const MOCK_STATS = { nodes: 47823, edges: 189234, components: 12, density: 0.000082 }

export default function GraphVisualization() {
  const [graphData, setGraphData] = useState(null)
  const [stats, setStats] = useState(MOCK_STATS)
  const [searchAddress, setSearchAddress] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setGraphData(MOCK_GRAPH)
    const fetchStats = async () => {
      try {
        const res = await graphAPI.getStats()
        if (res.data) {
          setStats({
            nodes: res.data.node_count ?? res.data.nodes ?? MOCK_STATS.nodes,
            edges: res.data.edge_count ?? res.data.edges ?? MOCK_STATS.edges,
            components: res.data.components ?? MOCK_STATS.components,
            density: res.data.graph_density ?? res.data.density ?? MOCK_STATS.density,
          })
        }
      } catch {
        // keep MOCK_STATS
      }
    }
    fetchStats()
  }, [])

  const handleSearch = async (e) => {
    e?.preventDefault()
    if (!searchAddress) return
    
    setLoading(true)
    try {
      const res = await graphAPI.getWalletGraph(searchAddress)
      if (res.data && res.data.nodes && res.data.nodes.length > 0) {
        setGraphData(res.data)
      } else {
        setGraphData(MOCK_GRAPH)
      }
    } catch {
      setTimeout(() => {
        setGraphData(MOCK_GRAPH)
        setLoading(false)
      }, 1000)
      return
    }
    setLoading(false)
  }

  return (
    <PageWrapper title="Graph Visualization">
      <div className="flex flex-col lg:flex-row gap-6 h-[calc(100vh-120px)]">
        
        {/* Sidebar */}
        <div className="w-full lg:w-80 flex flex-col gap-4">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input 
              type="text" 
              placeholder="Enter wallet address" 
              value={searchAddress}
              onChange={e => setSearchAddress(e.target.value)}
              className="flex-1 bg-dark-300 border border-white/10 rounded-lg px-3 py-2 text-sm text-white focus:border-primary-500 outline-none"
            />
            <button type="submit" className="bg-primary-600 hover:bg-primary-700 text-white p-2 rounded-lg transition-colors">
              <Search size={18} />
            </button>
          </form>

          <div className="grid grid-cols-2 gap-3">
            {[
              { label: 'Nodes', value: stats.nodes.toLocaleString(), icon: Hexagon },
              { label: 'Edges', value: stats.edges.toLocaleString(), icon: Share2 },
              { label: 'Components', value: stats.components, icon: Layers },
              { label: 'Density', value: stats.density.toFixed(6), icon: Activity }
            ].map((stat, i) => (
              <div key={i} className="bg-dark-300 border border-white/10 rounded-lg p-3">
                <div className="flex items-center gap-2 text-white/40 mb-1">
                  <stat.icon size={14} />
                  <span className="text-xs uppercase font-medium tracking-wider">{stat.label}</span>
                </div>
                <p className="text-lg font-semibold text-white">{stat.value}</p>
              </div>
            ))}
          </div>

          <div className="bg-dark-300 border border-white/10 rounded-lg p-4 flex-1">
            <h3 className="text-sm font-medium text-white mb-3">Filters & Layout</h3>
            <div className="space-y-4">
              <div>
                <p className="text-xs text-white/60 mb-2">Blockchains</p>
                {['Ethereum', 'Bitcoin', 'Polygon'].map(chain => (
                  <label key={chain} className="flex items-center gap-2 text-sm text-white/80 mb-1 cursor-pointer">
                    <input type="checkbox" defaultChecked className="rounded border-white/20 bg-dark-400 text-primary-500 focus:ring-primary-500" />
                    {chain}
                  </label>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Main Graph Area */}
        <div className="flex-1 relative bg-dark-300 border border-white/10 rounded-xl overflow-hidden flex flex-col">
          {loading ? (
            <div className="absolute inset-0 flex items-center justify-center bg-dark-300/50 backdrop-blur-sm z-10">
              <div className="flex flex-col items-center gap-4">
                <Spinner size="lg" />
                <p className="text-white/60 text-sm">Building transaction graph...</p>
              </div>
            </div>
          ) : null}
          
          <div className="flex-1 min-h-[500px]">
            {graphData ? (
              <CytoscapeGraph nodes={graphData.nodes} edges={graphData.edges} height="100%" />
            ) : (
              <div className="absolute inset-0 flex items-center justify-center">
                <p className="text-white/30">Enter a wallet address to visualize</p>
              </div>
            )}
          </div>
        </div>

      </div>
    </PageWrapper>
  )
}
