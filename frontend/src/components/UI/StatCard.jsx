import { TrendingUp, TrendingDown } from 'lucide-react'

export default function StatCard({ title, value, subtitle, icon: Icon, trend, trendValue, color = 'primary', gradient }) {
  const colorMap = {
    primary: 'from-primary-500/20 to-primary-600/5 border-primary-500/20',
    cyan: 'from-cyan-500/20 to-cyan-600/5 border-cyan-500/20',
    green: 'from-emerald-500/20 to-emerald-600/5 border-emerald-500/20',
    red: 'from-red-500/20 to-red-600/5 border-red-500/20',
    yellow: 'from-yellow-500/20 to-yellow-600/5 border-yellow-500/20',
    orange: 'from-orange-500/20 to-orange-600/5 border-orange-500/20',
  }
  const iconColorMap = {
    primary: 'text-primary-400 bg-primary-500/10',
    cyan: 'text-cyan-400 bg-cyan-500/10',
    green: 'text-emerald-400 bg-emerald-500/10',
    red: 'text-red-400 bg-red-500/10',
    yellow: 'text-yellow-400 bg-yellow-500/10',
    orange: 'text-orange-400 bg-orange-500/10',
  }
  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} backdrop-blur-md border rounded-xl p-5 hover:scale-[1.02] transition-all duration-300`}>
      <div className="flex items-start justify-between mb-3">
        <div>
          <p className="text-white/50 text-xs font-medium uppercase tracking-wider mb-1">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
          {subtitle && <p className="text-white/40 text-xs mt-1">{subtitle}</p>}
        </div>
        {Icon && (
          <div className={`p-2.5 rounded-lg ${iconColorMap[color]}`}>
            <Icon size={20} />
          </div>
        )}
      </div>
      {trend !== undefined && (
        <div className={`flex items-center gap-1 text-xs font-medium ${trend >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
          {trend >= 0 ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
          {Math.abs(trendValue || trend)}% vs last period
        </div>
      )}
    </div>
  )
}
