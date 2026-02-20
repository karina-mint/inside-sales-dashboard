import StatusBadge from './StatusBadge'
import type { KpiCard as KpiCardType } from '../types'
import { metricColor } from '../utils/metricColors'

function fmt(v: number | null, unit: string): string {
  if (v === null) return '---'
  if (unit === '%') return `${(v * 100).toFixed(1)}%`
  return `${v}${unit}`
}

interface Props {
  card: KpiCardType
}

export default function KpiCard({ card }: Props) {
  return (
    <div style={{
      background: '#1a1d2e',
      border: '1px solid #2a2d3e',
      borderRadius: '12px',
      padding: '20px',
      minWidth: '160px',
      flex: '1',
    }}>
      <p style={{ color: '#9ca3af', fontSize: '0.8rem', marginBottom: '4px' }}>{card.label}</p>
      <p style={{
        fontSize: '2rem',
        fontWeight: 700,
        color: metricColor(card.label),
        marginBottom: '8px',
      }}>
        {fmt(card.actual, card.unit)}
      </p>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
        <span style={{ fontSize: '0.75rem', color: '#6b7280' }}>
          目標: {fmt(card.target, card.unit)}
        </span>
        {card.achievement_rate !== null && (
          <StatusBadge rate={card.achievement_rate} />
        )}
      </div>
    </div>
  )
}
