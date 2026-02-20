import { useState, useEffect } from 'react'
import { useDashboard } from './hooks/useDashboard'
import MonthTabs from './components/MonthTabs'
import KpiCardGrid from './components/KpiCardGrid'
import FunnelChart from './components/FunnelChart'
import MetricTable from './components/MetricTable'
import SectionHeader from './components/SectionHeader'
import './App.css'

export default function App() {
  const [selectedMonth, setSelectedMonth] = useState('')
  const { data, loading, error, refresh } = useDashboard(selectedMonth)

  // 初回ロード時、APIが返した selected_month に同期
  useEffect(() => {
    if (data && !selectedMonth) {
      setSelectedMonth(data.selected_month)
    }
  }, [data, selectedMonth])

  const handleMonthSelect = (m: string) => {
    setSelectedMonth(m)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div>
          <h1>インサイドセールス ダッシュボード</h1>
          <p className="subtitle">リアルタイム KPI モニタリング</p>
        </div>
        <button className="refresh-btn" onClick={refresh} title="手動更新">
          ↻ 更新
        </button>
      </header>

      {error && (
        <div className="error-banner">
          エラー: {error}
        </div>
      )}

      {data && (
        <MonthTabs
          months={data.available_months}
          selected={data.selected_month}
          onSelect={handleMonthSelect}
        />
      )}

      {loading && !data && (
        <div className="loading">データを読み込み中...</div>
      )}

      {data && (
        <>
          <KpiCardGrid cards={data.kpi_cards} />

          <SectionHeader label="セールスファネル（実績 vs ベンチマーク）" />
          <FunnelChart stages={data.funnel_stages} />

          <SectionHeader label="案件化" />
          <MetricTable
            rows={data.section_ankenjika}
            months={data.available_months}
            selected={data.selected_month}
          />

          <SectionHeader label="アポ獲得" />
          <MetricTable
            rows={data.section_apo_kakutoku}
            months={data.available_months}
            selected={data.selected_month}
          />

          <SectionHeader label="リード獲得" />
          <MetricTable
            rows={data.section_lead_kakutoku}
            months={data.available_months}
            selected={data.selected_month}
          />

          <footer className="app-footer">
            最終更新: {new Date(data.last_updated).toLocaleString('ja-JP')}
            &nbsp;（60秒ごとに自動更新）
          </footer>
        </>
      )}
    </div>
  )
}
