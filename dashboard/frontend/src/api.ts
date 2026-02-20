import type { DashboardResponse } from './types'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

export async function fetchDashboard(month: string = ''): Promise<DashboardResponse> {
  const params = month ? `?month=${encodeURIComponent(month)}` : ''
  const res = await fetch(`${API_BASE}/api/dashboard${params}`)
  if (!res.ok) throw new Error(`API error: ${res.status}`)
  return res.json()
}
