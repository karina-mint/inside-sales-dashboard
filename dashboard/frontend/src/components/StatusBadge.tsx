interface Props {
  rate: number
}

export default function StatusBadge({ rate }: Props) {
  const pct = Math.round(rate * 100)
  const style: React.CSSProperties =
    rate >= 1.0
      ? { background: 'rgba(34,197,94,0.15)', color: '#4ade80' }
      : rate >= 0.7
      ? { background: 'rgba(234,179,8,0.15)', color: '#facc15' }
      : { background: 'rgba(239,68,68,0.15)', color: '#f87171' }

  return (
    <span
      style={{
        ...style,
        fontSize: '0.75rem',
        padding: '2px 8px',
        borderRadius: '999px',
        fontWeight: 600,
      }}
    >
      {pct}%
    </span>
  )
}
