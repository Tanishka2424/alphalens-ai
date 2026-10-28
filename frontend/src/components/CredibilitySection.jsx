import ResultCard from './ResultCard'

function Signal({ title, value, reasons, emptyText }) {
  return (
    <div>
      <dt className="text-xs uppercase tracking-wide text-[var(--color-card-ink-soft)]">{title}</dt>
      <dd className="font-mono-data mt-0.5 text-[var(--color-card-ink)]">{value}</dd>
      <div className="mt-1.5 flex flex-wrap gap-1.5">
        {reasons.length > 0 ? (
          reasons.map((r) => (
            <span key={r} className="text-xs px-2 py-0.5 rounded border border-[var(--color-card-ink-soft)] text-[var(--color-card-ink)]">
              {r}
            </span>
          ))
        ) : (
          <span className="text-xs text-[var(--color-card-ink-soft)]">{emptyText}</span>
        )}
      </div>
    </div>
  )
}

export default function CredibilitySection({ status, error, data }) {
  const clickbait = data?.clickbait
  const emotional = data?.emotional_language
  const source = data?.source_context
  const clickbaitReasons = [
  ...(clickbait?.matched_phrases ?? []),
  ...(clickbait?.excessive_caps ? ['Excessive capital letters'] : []),
  ...(clickbait?.excessive_punctuation ? ['Excessive punctuation'] : []),
]

  return (
    <ResultCard eyebrow="Writing & Source Signals" status={status} error={error}>
      {data && (
        <div>
          <dl className="grid grid-cols-1 sm:grid-cols-3 gap-5 text-sm">
            <Signal
              title="Clickbait wording"
              value={clickbait.score.toFixed(2)}
              reasons={clickbaitReasons}
              emptyText="No clickbait phrases found"
            />
            <Signal
              title="Emotional language"
              value={emotional.score.toFixed(2)}
              reasons={emotional.matched_words ?? []}
              emptyText="No emotional words found"
            />
            <Signal
              title="Source context"
              value={source.tier}
              reasons={source.resolved_domain
              ? [source.resolved_domain]
              : source.matched_via
              ? [`Matched by ${source.matched_via.replace('_', ' ')}`]
             : []
}
            />
          </dl>

          <p className="mt-5 text-xs text-[var(--color-card-ink-soft)] italic font-display">
            {data.disclaimer} A source that is not in our list is not necessarily unreliable.
          </p>
        </div>
      )}
    </ResultCard>
  )
}