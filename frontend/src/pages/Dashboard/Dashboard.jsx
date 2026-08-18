import React, { useEffect, useState } from 'react';
import PageWrapper from '../../components/Layout/PageWrapper';
import StatCard from '../../components/UI/StatCard';
import { adminAPI } from '../../services/api';
import { Shield, AlertTriangle, ArrowLeftRight, FileSearch, Network, Activity } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, BarChart, Bar, CartesianGrid } from 'recharts';

const MOCK_STATS = {
  totalWallets: 125430,
  fraudulentWallets: 1876,
  totalTransactions: 721046,
  networks: 5,
  activeInvestigations: 31,
  avgFraudScore: 0.237,
  fraud_trend: Array.from({ length: 14 }, (_, i) => ({
    date: `Day ${i + 1}`,
    flagged: Math.floor(Math.random() * 50 + 10),
    total: Math.floor(Math.random() * 500 + 200),
  })),
  volume_trend: Array.from({ length: 7 }, (_, i) => ({
    date: `Day ${i + 1}`,
    volume: Math.floor(Math.random() * 50000 + 10000),
  }))
};

const normalizeStats = (data = {}) => {
  const rawVolumeTrend = (data.volume_trend && data.volume_trend.length > 0) ? data.volume_trend : MOCK_STATS.volume_trend;
  return {
    totalWallets: data.totalWallets ?? data.total_wallets ?? MOCK_STATS.totalWallets,
    fraudulentWallets: data.fraudulentWallets ?? data.fraudulent_wallets ?? MOCK_STATS.fraudulentWallets,
    totalTransactions: data.totalTransactions ?? data.total_transactions ?? MOCK_STATS.totalTransactions,
    networks: data.networks ?? data.blockchain_networks ?? MOCK_STATS.networks,
    activeInvestigations: data.activeInvestigations ?? data.active_investigations ?? MOCK_STATS.activeInvestigations,
    avgFraudScore: data.avgFraudScore ?? data.avg_fraud_score ?? MOCK_STATS.avgFraudScore,
    fraud_trend: (data.fraud_trend && data.fraud_trend.length > 0) ? data.fraud_trend : MOCK_STATS.fraud_trend,
    volume_trend: rawVolumeTrend.map(item => ({
      ...item,
      volume: item.volume ?? ((item.bitcoin || 0) + (item.ethereum || 0) + (item.bnb || 0) + (item.polygon || 0) + (item.tron || 0))
    })),
  };
};

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const res = await adminAPI.getStats();
        setStats(normalizeStats(res.data));
      } catch (err) {
        setStats(MOCK_STATS);
      }
    };
    fetchStats();
  }, []);

  if (!stats) {
    return (
      <PageWrapper title="Dashboard" subtitle="Overview of platform metrics">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        </div>
      </PageWrapper>
    );
  }

  return (
    <PageWrapper title="Dashboard" subtitle="Overview of platform metrics">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <StatCard title="Total Wallets Monitored" value={stats.totalWallets.toLocaleString()} icon={Shield} color="primary" />
        <StatCard title="Fraudulent Wallets Detected" value={stats.fraudulentWallets.toLocaleString()} icon={AlertTriangle} color="red" />
        <StatCard title="Transactions Analyzed" value={stats.totalTransactions.toLocaleString()} icon={ArrowLeftRight} color="green" />
        <StatCard title="Active Investigations" value={stats.activeInvestigations} icon={FileSearch} color="yellow" />
        <StatCard title="Supported Networks" value={stats.networks} icon={Network} color="cyan" />
        <StatCard title="Avg System Fraud Score" value={`${(stats.avgFraudScore * 100).toFixed(1)}%`} icon={Activity} color="orange" />
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="card p-5">
          <h3 className="text-lg font-semibold text-white mb-4">Fraud Activity Trend</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={stats.fraud_trend}>
                <defs>
                  <linearGradient id="colorFlagged" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#ef4444" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#ef4444" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff' }} />
                <Area type="monotone" dataKey="flagged" stroke="#ef4444" fillOpacity={1} fill="url(#colorFlagged)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card p-5">
          <h3 className="text-lg font-semibold text-white mb-4">Transaction Volume</h3>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.volume_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="date" stroke="#64748b" fontSize={12} />
                <YAxis stroke="#64748b" fontSize={12} />
                <Tooltip contentStyle={{ background: '#0f172a', border: '1px solid #1e293b', borderRadius: '8px', color: '#fff' }} />
                <Bar dataKey="volume" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </PageWrapper>
  );
}
