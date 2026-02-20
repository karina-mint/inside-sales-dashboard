export function metricColor(label: string): string {
  if (label.includes('アポ')) return '#facc15'
  if (label.includes('通電')) return '#ffffff'
  if (label.includes('案件')) return '#f87171'
  if (label.includes('リード')) return '#4ade80'
  return '#ffffff'
}
