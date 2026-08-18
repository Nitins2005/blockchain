export const BLOCKCHAINS = [
  { id: 'bitcoin', name: 'Bitcoin', symbol: 'BTC', color: '#f7931a' },
  { id: 'ethereum', name: 'Ethereum', symbol: 'ETH', color: '#627eea' },
  { id: 'bnb', name: 'BNB Chain', symbol: 'BNB', color: '#f3ba2f' },
  { id: 'polygon', name: 'Polygon', symbol: 'MATIC', color: '#8247e5' },
  { id: 'tron', name: 'Tron', symbol: 'TRX', color: '#ef0027' },
]

export const WALLET_CATEGORIES = [
  'Exchange', 'Mining Pool', 'Scam Wallet', 'Darknet Wallet',
  'Mixer', 'Bridge', 'DeFi Protocol', 'NFT Marketplace',
  'Personal Wallet', 'Unknown'
]

export const RISK_COLORS = {
  low: { text: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', dot: '#10b981' },
  medium: { text: 'text-yellow-400', bg: 'bg-yellow-500/10', border: 'border-yellow-500/30', dot: '#f59e0b' },
  high: { text: 'text-orange-400', bg: 'bg-orange-500/10', border: 'border-orange-500/30', dot: '#f97316' },
  critical: { text: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30', dot: '#ef4444' },
}

export const CHART_COLORS = ['#6366f1', '#06b6d4', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#14b8a6']

export const BLOCKCHAIN_COLORS = {
  bitcoin: '#f7931a',
  ethereum: '#627eea',
  bnb: '#f3ba2f',
  polygon: '#8247e5',
  tron: '#ef0027',
}
