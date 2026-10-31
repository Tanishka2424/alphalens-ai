import { fmtDate } from '../format'
import ResultCard from './ResultCard'

export default function RetrievalSection({ status, error, data, excludeIds = [] }) {
  const items = (data?.results ?? []).filter((r) => !excludeIds.includes(r.article_id))
  return (
    <ResultCard title="Other related coverage (context, not confirmation)" status={status} error={error}>
      {data && items.length === 0 && <p>No other related articles found.</p>}
      {items.length > 0 && (
        <details>
          <summary className="cursor-pointer font-semibold">Show {items.length} related articles</summary>
          <ul className="mt-3 space-y-3">
            {items.map((r) => (
              <li key={r.article_id} className="border-t-2 border-teal pt-3">
                <p className="font-semibold">{r.title}</p>
                <p className="text-sm text-teal-soft">
                  {r.source || 'Unknown source'} · {fmtDate(r.published_at)} · similarity {r.similarity_score.toFixed(2)}
                </p>
              </li>
            ))}
          </ul>
          <p className="mt-3 text-sm text-teal-soft">
            These articles are on a similar topic. They do not confirm or disprove the claim.
          </p>
        </details>
      )}
    </ResultCard>
  )
}