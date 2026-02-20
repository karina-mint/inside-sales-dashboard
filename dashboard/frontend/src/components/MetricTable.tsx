import type { MonthlyRow } from '../types'

interface Props {
  rows: MonthlyRow[]
  months: string[]
  selected: string
}

function isRateMetric(metric: string): boolean {
  return metric.includes('率')
}

function fmtCell(val: number | null, isRate: boolean): string {
  if (val === null) return '---'
  if (isRate) return `${(val * 100).toFixed(1)}%`
  return val.toLocaleString()
}

function getAchievementRate(rows: MonthlyRow[], month: string): number | null {
  const targetRow = rows.find(
    (r) => r.metric.startsWith('目標：') && !r.metric.includes('率')
  )
  const actualRow = rows.find(
    (r) => r.metric.startsWith('実績：') && !r.metric.includes('率')
  )
  if (!targetRow || !actualRow) return null
  const t = targetRow.columns[month]
  const a = actualRow.columns[month]
  if (t === null || t === 0 || a === null) return null
  return a / t
}

export default function MetricTable({ rows, months, selected }: Props) {
  return (
    <div style={{
      background: '#1a1d2e',
      border: '1px solid #2a2d3e',
      borderRadius: '12px',
      marginBottom: '24px',
      overflowX: 'auto',
    }}>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.85rem' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #2a2d3e' }}>
            <th style={{
              textAlign: 'left',
              padding: '12px 16px',
              color: '#6b7280',
              fontWeight: 500,
              minWidth: '220px',
            }}>
              指標
            </th>
            {months.map((m) => (
              <th
                key={m}
                style={{
                  padding: '12px 12px',
                  textAlign: 'right',
                  color: m === selected ? '#fff' : '#6b7280',
                  fontWeight: m === selected ? 600 : 400,
                  background: m === selected ? 'rgba(99,102,241,0.08)' : 'transparent',
                  whiteSpace: 'nowrap',
                }}
              >
                {m}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => {
            const isRate = isRateMetric(row.metric)
            return (
              <tr
                key={row.metric}
                style={{ borderBottom: '1px solid rgba(42,45,62,0.5)' }}
              >
                <td style={{
                  padding: '10px 16px',
                  color: '#d1d5db',
                  whiteSpace: 'nowrap',
                }}>
                  {row.metric}
                </td>
                {months.map((m) => {
                  const val = row.columns[m] ?? null
                  const isSelected = m === selected
                  return (
                    <td
                      key={m}
                      style={{
                        padding: '10px 12px',
                        textAlign: 'right',
                        color: '#e5e7eb',
                        background: isSelected ? 'rgba(99,102,241,0.05)' : 'transparent',
                        fontWeight: isSelected ? 600 : 400,
                      }}
                    >
                      {fmtCell(val, isRate)}
                    </td>
                  )
                })}
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}

export { getAchievementRate }
