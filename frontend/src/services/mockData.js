// Mock data for UI demonstration before AI integration

export const mockStats = {
  totalWallets: 284751,
  fraudulentWallets: 12847,
  totalTransactions: 4829304,
  blockchainNetworks: 5,
  activeInvestigations: 47,
  avgFraudScore: 23.7,
  fraudRate: 4.51,
  newToday: 1284,
}

export const mockFraudTrend = [
  { date: '2024-01', fraud: 245, normal: 8450 },
  { date: '2024-02', fraud: 312, normal: 9120 },
  { date: '2024-03', fraud: 289, normal: 8780 },
  { date: '2024-04', fraud: 456, normal: 10230 },
  { date: '2024-05', fraud: 523, normal: 11450 },
  { date: '2024-06', fraud: 612, normal: 12340 },
  { date: '2024-07', fraud: 489, normal: 13200 },
  { date: '2024-08', fraud: 734, normal: 14500 },
  { date: '2024-09', fraud: 891, normal: 15200 },
  { date: '2024-10', fraud: 1023, normal: 16700 },
  { date: '2024-11', fraud: 967, normal: 17800 },
  { date: '2024-12', fraud: 1156, normal: 18900 },
]

export const mockBlockchainDistribution = [
  { name: 'Bitcoin', value: 28.4, color: '#f59e0b' },
  { name: 'Ethereum', value: 35.2, color: '#6366f1' },
  { name: 'BNB Chain', value: 18.7, color: '#eab308' },
  { name: 'Polygon', value: 11.3, color: '#8b5cf6' },
  { name: 'Tron', value: 6.4, color: '#ef4444' },
]

export const mockWalletCategories = [
  { name: 'Personal Wallet', value: 42.1, color: '#10b981' },
  { name: 'Exchange', value: 18.3, color: '#6366f1' },
  { name: 'DeFi Protocol', value: 12.7, color: '#0ea5e9' },
  { name: 'Mining Pool', value: 8.4, color: '#f59e0b' },
  { name: 'Scam Wallet', value: 6.8, color: '#ef4444' },
  { name: 'Mixer', value: 4.2, color: '#f97316' },
  { name: 'NFT Marketplace', value: 3.9, color: '#8b5cf6' },
  { name: 'Others', value: 3.6, color: '#64748b' },
]

export const mockTopSuspicious = [
  { address: '0x742d35Cc6634C0532925a3b8D4d9B3F267c3B3f2', score: 97, blockchain: 'ETH', risk: 'CRITICAL', txCount: 4521 },
  { address: 'bc1qxy2kgdygjrsqtzq2n0yrf249dmlmqs5q2tgr', score: 93, blockchain: 'BTC', risk: 'CRITICAL', txCount: 1872 },
  { address: 'TKFLnxkzqmRN2mkfGpQiTQnbdBM4PvCEMx', score: 89, blockchain: 'TRX', risk: 'HIGH', txCount: 8934 },
  { address: '0x55d398326f99059ff775485246999027b3197955', score: 84, blockchain: 'BNB', risk: 'HIGH', txCount: 2341 },
  { address: '0x3c499c542cef5e3811e1192ce70d8cc03d5c3359', score: 78, blockchain: 'MATIC', risk: 'HIGH', txCount: 1567 },
]

export const mockTransactions = Array.from({ length: 50 }, (_, i) => ({
  id: `tx-${i + 1}`,
  hash: `0x${Math.random().toString(16).slice(2, 66)}`,
  sender: `0x${Math.random().toString(16).slice(2, 42)}`,
  receiver: `0x${Math.random().toString(16).slice(2, 42)}`,
  blockchain: ['ETH', 'BTC', 'BNB', 'MATIC', 'TRX'][Math.floor(Math.random() * 5)],
  amount: (Math.random() * 10000).toFixed(4),
  gasFee: (Math.random() * 0.1).toFixed(6),
  timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
  blockNumber: Math.floor(Math.random() * 10000000) + 15000000,
  token: ['ETH', 'BTC', 'BNB', 'USDT', 'USDC', 'MATIC'][Math.floor(Math.random() * 6)],
  status: ['confirmed', 'confirmed', 'confirmed', 'pending', 'failed'][Math.floor(Math.random() * 5)],
  fraudScore: Math.floor(Math.random() * 100),
}))

export const mockWalletPrediction = (address) => ({
  address,
  fraudScore: Math.floor(Math.random() * 100),
  riskLevel: ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'][Math.floor(Math.random() * 4)],
  confidence: (0.7 + Math.random() * 0.3).toFixed(3),
  lastActivity: new Date(Date.now() - Math.random() * 7 * 24 * 60 * 60 * 1000).toISOString(),
  transactionCount: Math.floor(Math.random() * 5000) + 1,
  connectedWallets: Math.floor(Math.random() * 200) + 1,
  crossChainActivity: Math.floor(Math.random() * 5),
  predictionTime: new Date().toISOString(),
  features: {
    incomingTxCount: Math.floor(Math.random() * 3000),
    outgoingTxCount: Math.floor(Math.random() * 3000),
    avgAmount: (Math.random() * 10000).toFixed(2),
    maxAmount: (Math.random() * 100000).toFixed(2),
    balance: (Math.random() * 50000).toFixed(4),
    activeDays: Math.floor(Math.random() * 500),
    gasUsage: (Math.random() * 10).toFixed(4),
    tokenDiversity: Math.floor(Math.random() * 20),
    neighborCount: Math.floor(Math.random() * 500),
    degreeCentrality: (Math.random() * 0.01).toFixed(5),
    betweennessCentrality: (Math.random() * 0.005).toFixed(5),
    pageRank: (Math.random() * 0.001).toFixed(6),
    clusteringCoeff: (Math.random()).toFixed(3),
    crossChainTxCount: Math.floor(Math.random() * 100),
  },
  blacklistedNeighbors: Math.floor(Math.random() * 10),
  riskFactors: [
    'Connected to 7 known blacklisted wallets',
    'Unusual transaction frequency spike detected',
    'Cross-chain asset movement pattern',
    'Interaction with known mixer contracts',
    'Abnormally large transfer amounts',
  ].slice(0, Math.floor(Math.random() * 4) + 1),
})

export const mockAttribution = (address) => ({
  address,
  category: ['Exchange', 'Mining Pool', 'Scam Wallet', 'Darknet Wallet', 'Mixer', 'Bridge', 'DeFi Protocol', 'NFT Marketplace', 'Personal Wallet', 'Unknown'][Math.floor(Math.random() * 10)],
  confidence: (0.6 + Math.random() * 0.4).toFixed(3),
  alternativeCategories: [
    { category: 'Exchange', confidence: 0.12 },
    { category: 'Personal Wallet', confidence: 0.08 },
  ],
  signals: [
    'High transaction volume consistency',
    'Multiple token types handled',
    'Regular batch processing patterns',
    'Network centrality score above threshold',
  ],
})

export const mockExplanation = (address) => ({
  address,
  topFeatures: [
    { feature: 'Blacklisted Neighbor Count', importance: 0.342, value: 7, direction: 'positive' },
    { feature: 'Transaction Frequency', importance: 0.287, value: 45.2, direction: 'positive' },
    { feature: 'Cross-Chain Activity', importance: 0.198, value: 4, direction: 'positive' },
    { feature: 'Average Transaction Amount', importance: 0.156, value: 45230.5, direction: 'positive' },
    { feature: 'Clustering Coefficient', importance: 0.142, value: 0.023, direction: 'negative' },
    { feature: 'Active Days', importance: 0.098, value: 12, direction: 'negative' },
    { feature: 'PageRank Score', importance: 0.087, value: 0.00234, direction: 'positive' },
    { feature: 'Token Diversity', importance: 0.065, value: 8, direction: 'positive' },
  ],
  riskFactors: [
    { factor: 'Connected to multiple blacklisted wallets', severity: 'CRITICAL', weight: 0.342 },
    { factor: 'High transaction frequency anomaly', severity: 'HIGH', weight: 0.287 },
    { factor: 'Cross-chain movement detected', severity: 'HIGH', weight: 0.198 },
    { factor: 'Abnormal transfer amount pattern', severity: 'MEDIUM', weight: 0.156 },
    { factor: 'Interaction with malicious smart contracts', severity: 'HIGH', weight: 0.142 },
  ],
  neighborInfluence: [
    { address: '0xDead...B33f', influence: 0.28, fraudScore: 98, category: 'Mixer' },
    { address: '0xScam...4E21', influence: 0.19, fraudScore: 94, category: 'Scam Wallet' },
    { address: '0xDark...9A12', influence: 0.15, fraudScore: 87, category: 'Darknet Wallet' },
  ],
  temporalPattern: Array.from({ length: 30 }, (_, i) => ({
    date: new Date(Date.now() - (29 - i) * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
    txCount: Math.floor(Math.random() * 50),
    fraudSignal: Math.random() > 0.7 ? Math.random() * 100 : 0,
  })),
  reasoning: `This wallet exhibits multiple high-risk behavioral patterns consistent with fraudulent activity. The primary risk indicator is its connection to 7 known blacklisted wallets including confirmed mixers and scam addresses. Analysis of temporal transaction patterns reveals unusual frequency spikes that coincide with known fraud campaigns. The cross-chain movement of assets through ${Math.floor(Math.random() * 4) + 2} different blockchain networks suggests deliberate obfuscation attempts. The Temporal GNN model assigned a fraud score of ${Math.floor(Math.random() * 30) + 70}/100 based on both structural graph features and temporal behavioral patterns.`,
})

export const mockGraphData = (address) => ({
  nodes: [
    { id: address, label: address.slice(0, 10) + '...', fraudScore: 87, type: 'target', blockchain: 'ETH' },
    ...Array.from({ length: 12 }, (_, i) => ({
      id: `wallet-${i}`,
      label: `0x${Math.random().toString(16).slice(2, 10)}...`,
      fraudScore: Math.floor(Math.random() * 100),
      type: ['normal', 'suspicious', 'blacklisted'][Math.floor(Math.random() * 3)],
      blockchain: ['ETH', 'BTC', 'BNB', 'MATIC', 'TRX'][Math.floor(Math.random() * 5)],
    })),
  ],
  edges: Array.from({ length: 18 }, (_, i) => ({
    id: `edge-${i}`,
    source: i < 12 ? address : `wallet-${Math.floor(Math.random() * 12)}`,
    target: `wallet-${i % 12}`,
    amount: (Math.random() * 10000).toFixed(4),
    timestamp: new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000).toISOString(),
    blockchain: ['ETH', 'BTC', 'BNB'][Math.floor(Math.random() * 3)],
  })),
})

export const mockBlacklist = Array.from({ length: 30 }, (_, i) => ({
  id: `bl-${i + 1}`,
  address: `0x${Math.random().toString(16).slice(2, 42)}`,
  type: ['Scam Wallet', 'Mixer', 'Known Exchange', 'Darknet'][Math.floor(Math.random() * 4)],
  blockchain: ['ETH', 'BTC', 'BNB', 'MATIC', 'TRX'][Math.floor(Math.random() * 5)],
  addedBy: ['admin', 'investigator'][Math.floor(Math.random() * 2)],
  addedAt: new Date(Date.now() - Math.random() * 90 * 24 * 60 * 60 * 1000).toISOString(),
  reason: ['Confirmed fraud', 'Money laundering', 'Phishing', 'Ransomware'][Math.floor(Math.random() * 4)],
  reportCount: Math.floor(Math.random() * 50) + 1,
}))

export const mockInvestigations = Array.from({ length: 20 }, (_, i) => ({
  id: `INV-2024-${String(i + 1).padStart(3, '0')}`,
  title: [
    'Suspected Ponzi Scheme Network',
    'DeFi Protocol Exploit Analysis',
    'NFT Wash Trading Investigation',
    'Cross-Chain Money Laundering',
    'Phishing Campaign Wallet Cluster',
  ][Math.floor(Math.random() * 5)],
  status: ['open', 'in-progress', 'closed', 'pending'][Math.floor(Math.random() * 4)],
  priority: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)],
  assignee: ['Investigator A', 'Investigator B', 'Admin'][Math.floor(Math.random() * 3)],
  walletCount: Math.floor(Math.random() * 50) + 1,
  createdAt: new Date(Date.now() - Math.random() * 60 * 24 * 60 * 60 * 1000).toISOString(),
  updatedAt: new Date(Date.now() - Math.random() * 5 * 24 * 60 * 60 * 1000).toISOString(),
  notes: Math.floor(Math.random() * 10),
}))

export const mockModelStatus = {
  status: 'ready',
  version: '2.1.4',
  accuracy: 97.3,
  precision: 96.8,
  recall: 94.2,
  f1Score: 95.5,
  lastTrained: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
  trainingSamples: 2847302,
  modelType: 'Temporal GNN (PyTorch Geometric)',
  graphLayers: 4,
  hiddenDim: 256,
  temporalWindow: '30 days',
}
