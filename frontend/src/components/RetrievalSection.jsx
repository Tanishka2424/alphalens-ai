import ResultCard from './ResultCard'

export default function RetrievalSection({ status, error, data }) {
  return (
    <ResultCard eyebrow="Related Wire Copy" status={status} error={error}>
      {data && (
        data.results.length === 0 ? (
          <p className="text-sm text-[var(--color-card-ink-soft)] italic font-display">
            No related coverage found in the indexed corpus.
          </p>
        ) : (
          <ul className="space-y-3">
            {data.results.map((r, i) => (
              <li key={i} className="flex items-baseline justify-between gap-4 border-b border-[var(--color-card-line)] last:border-0 pb-3 last:pb-0">
                <span className="text-sm text-[var(--color-card-ink)]">{r.title}</span>
                <span className="font-mono-data text-xs text-[var(--color-card-ink-soft)] whitespace-nowrap">
                  {(r.similarity_score * 100).toFixed(0)}% match
                </span>
              </li>
            ))}
          </ul>
        )
      )}
    </ResultCard>
  )
}
