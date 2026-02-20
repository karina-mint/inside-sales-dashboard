import { useState, useEffect, useCallback } from 'react'
import { fetchDashboard } from '../api'
import type { DashboardResponse } from '../types'

export function useDashboard(selectedMonth: string) {
  const [data, setData] = useState<DashboardResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const load = useCallback(async () => {
    try {
      const result = await fetchDashboard(selectedMonth)
      setData(result)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [selectedMonth])

  useEffect(() => {
    setLoading(true)
    load()
    const interval = setInterval(load, 60_000)
    return () => clearInterval(interval)
  }, [load])

  return { data, loading, error, refresh: load }
}
