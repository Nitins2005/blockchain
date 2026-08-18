import { SearchX } from 'lucide-react'

export default function EmptyState({ icon: Icon = SearchX, title = 'No data found', message = 'Try adjusting your search or filters.' }) {
  return (
    <div className="flex flex-col items-center justify-center py-16 text-center">
      <div className="p-4 rounded-2xl bg-white/5 mb-4">
        <Icon size={32} className="text-white/20" />
      </div>
      <p className="text-white/50 font-medium">{title}</p>
      <p className="text-white/30 text-sm mt-1">{message}</p>
    </div>
  )
}
