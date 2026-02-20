interface Props {
  months: string[]
  selected: string
  onSelect: (m: string) => void
}

export default function MonthTabs({ months, selected, onSelect }: Props) {
  return (
    <div style={{ display: 'flex', gap: '8px', marginBottom: '24px', flexWrap: 'wrap' }}>
      {months.map((m) => (
        <button
          key={m}
          onClick={() => onSelect(m)}
          style={{
            padding: '6px 14px',
            borderRadius: '8px',
            fontSize: '0.85rem',
            fontWeight: 500,
            cursor: 'pointer',
            transition: 'all 0.15s',
            border: m === selected ? 'none' : '1px solid #2a2d3e',
            background: m === selected ? '#6366f1' : '#1a1d2e',
            color: m === selected ? '#ffffff' : '#9ca3af',
          }}
        >
          {m}
        </button>
      ))}
    </div>
  )
}
