import KpiCard from './KpiCard'
import type { KpiCard as KpiCardType } from '../types'

interface Props {
  cards: KpiCardType[]
}

export default function KpiCardGrid({ cards }: Props) {
  return (
    <div style={{
      display: 'flex',
      gap: '16px',
      flexWrap: 'wrap',
      marginBottom: '32px',
    }}>
      {cards.map((card) => (
        <KpiCard key={card.label} card={card} />
      ))}
    </div>
  )
}
