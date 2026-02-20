import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend,
  ResponsiveContainer, Cell, ReferenceLine,
} from 'recharts'
import type { FunnelStage } from '../types'
import { metricColor } from '../utils/metricColors'

interface Props {
  stages: FunnelStage[]
}

export default function FunnelChart({ stages }: Props) {
  const data = stages.map((s) => ({
    name: s.label,
    実績: s.actual !== null ? +(s.actual * 100).toFixed(2) : 0,
    ベンチマーク: +(s.benchmark * 100).toFixed(2),
    color: metricColor(s.label),
  }))

  return (
    <div style={{
      background: '#1a1d2e',
      border: '1px solid #2a2d3e',
      borderRadius: '12px',
      padding: '20px',
      marginBottom: '32px',
    }}>
      <p style={{ color: '#9ca3af', fontSize: '0.8rem', marginBottom: '16px' }}>
        ▪ 実績 vs ベンチマーク（%）
      </p>
      <ResponsiveContainer width="100%" height={240}>
        <BarChart data={data} barCategoryGap="35%">
          <XAxis
            dataKey="name"
            tick={{ fill: '#9ca3af', fontSize: 12 }}
            axisLine={{ stroke: '#2a2d3e' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#9ca3af', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            unit="%"
          />
          <Tooltip
            contentStyle={{ background: '#1a1d2e', border: '1px solid #2a2d3e', borderRadius: '8px' }}
            labelStyle={{ color: '#fff', fontWeight: 600 }}
            itemStyle={{ color: '#9ca3af' }}
            formatter={(value) => [`${value}%`]}
          />
          <Legend wrapperStyle={{ color: '#9ca3af', fontSize: '0.8rem' }} />
          <Bar dataKey="実績" radius={[4, 4, 0, 0]}>
            {data.map((entry, i) => (
              <Cell key={i} fill={entry.color} />
            ))}
          </Bar>
          <Bar dataKey="ベンチマーク" fill="#374151" radius={[4, 4, 0, 0]} />
          <ReferenceLine y={0} stroke="#2a2d3e" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
