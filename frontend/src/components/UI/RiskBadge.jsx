import { RISK_COLORS } from '../../utils/constants'

export default function RiskBadge({ level, score, showScore = false, size = 'md' }) {
  const colors = RISK_COLORS[level?.toLowerCase()] || RISK_COLORS.medium
  const sizeClass = size === 'sm' ? 'text-xs px-2 py-0.5' : size === 'lg' ? 'text-sm px-3 py-1' : 'text-xs px-2.5 py-0.5'
  return (
    <span className={`inline-flex items-center rounded-full font-medium border ${sizeClass} ${colors.text} ${colors.bg} ${colors.border}`}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 flex-shrink-0" style={{ backgroundColor: colors.dot }}></span>
      {level?.toUpperCase() || 'UNKNOWN'}
      {showScore && score !== undefined && <span className="ml-1 font-mono opacity-80">({(score * 100).toFixed(0)}%)</span>}
    </span>
  )
}
