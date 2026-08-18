import { ChevronLeft, ChevronRight } from 'lucide-react'

export default function Pagination({ page, pages, total, pageSize, onPageChange }) {
  return (
    <div className="flex items-center justify-between px-4 py-3 border-t border-white/10">
      <p className="text-sm text-white/40">
        Showing {Math.min((page - 1) * pageSize + 1, total)}–{Math.min(page * pageSize, total)} of {total}
      </p>
      <div className="flex items-center gap-1">
        <button onClick={() => onPageChange(page - 1)} disabled={page <= 1}
          className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
          <ChevronLeft size={16} />
        </button>
        {Array.from({ length: Math.min(pages, 7) }, (_, i) => {
          const p = i + Math.max(1, page - 3)
          if (p > pages) return null
          return (
            <button key={p} onClick={() => onPageChange(p)}
              className={`w-8 h-8 rounded-lg text-sm font-medium transition-colors ${
                p === page ? 'bg-primary-600 text-white' : 'text-white/50 hover:text-white hover:bg-white/10'
              }`}>{p}</button>
          )
        })}
        <button onClick={() => onPageChange(page + 1)} disabled={page >= pages}
          className="p-1.5 rounded-lg text-white/40 hover:text-white hover:bg-white/10 disabled:opacity-30 disabled:cursor-not-allowed transition-colors">
          <ChevronRight size={16} />
        </button>
      </div>
    </div>
  )
}
