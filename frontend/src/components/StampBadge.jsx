const COLOR_MAP = {
  ledger: 'var(--color-ledger)',
  brass: 'var(--color-risk-amber)',
  red: 'var(--color-risk-red)',
  amber: 'var(--color-risk-amber)',
}

export default function StampBadge({ label, color = 'ledger' }) {
  return (
    <span className="stamp" style={{ color: COLOR_MAP[color] || COLOR_MAP.ledger }}>
      {label}
    </span>
  )
}
