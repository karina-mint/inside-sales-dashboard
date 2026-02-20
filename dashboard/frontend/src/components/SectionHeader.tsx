interface Props {
  label: string
}

export default function SectionHeader({ label }: Props) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      gap: '10px',
      marginBottom: '12px',
      marginTop: '8px',
    }}>
      <div style={{ width: '4px', height: '20px', background: '#6366f1', borderRadius: '2px' }} />
      <h2 style={{ fontSize: '1rem', fontWeight: 600, color: '#e5e7eb', margin: 0 }}>{label}</h2>
    </div>
  )
}
