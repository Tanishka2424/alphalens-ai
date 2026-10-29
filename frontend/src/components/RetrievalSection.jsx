import ResultCard from './ResultCard'

export default function RetrievalSection({ status, error, data }) {
  return (
    <ResultCard eyebrow="Related Coverage (context only)" status={status} error={error}>
      {data && (
        data.results.length === 0 ? (
          <p className="text-sm text-[var(--color-card-ink-soft)] italic font-display">
            No related coverage found in the indexed corpus.
          </p>
        ) : (
          <>
            <ul className="space-y-3">
              {data.results.map((r) => (
                <li key={r.article_id} className="border-b border-[var(--color-card-line)] last:border-0 pb-3 last:pb-0">
                  <div className="flex items-baseline justify-between gap-4">
                    {r.url ? (
                      <a href={r.url} target="_blank" rel="noreferrer" className="text-sm text-[var(--color-card-ink)] underline">
                        {r.title}
                      </a>
                    ) : (
                      <span className="text-sm text-[var(--color-card-ink)]">{r.title}</span>
                    )}
                    <span className="font-mono-data text-xs text-[var(--color-card-ink-soft)] whitespace-nowrap">
                      similarity {r.similarity_score.toFixed(2)}
                    </span>
                  </div>
                  <div className="mt-1 text-xs text-[var(--color-card-ink-soft)]">
                    {[r.source, r.published_at].filter(Boolean).join(' · ') || 'Source and date not available'}
                  </div>
                </li>
              ))}
            </ul>
            <p className="mt-4 text-xs text-[var(--color-card-ink-soft)] italic font-display">
              These articles are similar in topic. They do not confirm or disprove the claim.
            </p>
          </>
        )
      )}
    </ResultCard>
  )
}