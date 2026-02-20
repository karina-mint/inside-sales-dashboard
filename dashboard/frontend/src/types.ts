export interface KpiCard {
  label: string
  target: number | null
  actual: number | null
  achievement_rate: number | null
  unit: string
}

export interface FunnelStage {
  label: string
  actual: number | null
  benchmark: number
  achievement_rate: number | null
}

export interface MonthlyRow {
  metric: string
  columns: Record<string, number | null>
}

export interface DashboardResponse {
  available_months: string[]
  selected_month: string
  kpi_cards: KpiCard[]
  funnel_stages: FunnelStage[]
  section_ankenjika: MonthlyRow[]
  section_apo_kakutoku: MonthlyRow[]
  section_lead_kakutoku: MonthlyRow[]
  last_updated: string
}
