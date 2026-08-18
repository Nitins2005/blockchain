import { useState } from 'react'

export default function usePagination(initialPage = 1, initialPageSize = 20) {
  const [page, setPage] = useState(initialPage)
  const [pageSize] = useState(initialPageSize)
  const goToPage = (p) => setPage(p)
  const reset = () => setPage(1)
  return { page, pageSize, goToPage, reset }
}
