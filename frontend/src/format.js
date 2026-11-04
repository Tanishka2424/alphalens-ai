export const isLink = (u) => typeof u === 'string' && /^https?:\/\//i.test(u)

export function fmtDate(iso) {
  if (!iso) return 'Undated archive headline'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return 'Undated archive headline'
  return d.toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
}