export const formatAddress = (address, chars = 8) => {
  if (!address) return 'N/A'
  return `${address.slice(0, chars)}...${address.slice(-6)}`
}

export const formatAmount = (amount, decimals = 6) => {
  if (amount === null || amount === undefined) return '0'
  return Number(amount).toLocaleString('en-US', { maximumFractionDigits: decimals })
}

export const formatUSD = (amount) => {
  if (!amount) return '$0.00'
  return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(amount)
}

export const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })
}

export const formatDateTime = (dateStr) => {
  if (!dateStr) return 'N/A'
  return new Date(dateStr).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })
}

export const formatPercent = (value) => {
  if (value === null || value === undefined) return '0%'
  return `${(value * 100).toFixed(1)}%`
}

export const formatNumber = (n) => {
  if (!n) return '0'
  if (n >= 1000000) return `${(n / 1000000).toFixed(1)}M`
  if (n >= 1000) return `${(n / 1000).toFixed(1)}K`
  return n.toString()
}
