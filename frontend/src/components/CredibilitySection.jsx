import ResultCard from './ResultCard'

function level(score) {
  if (!score) return 'None found'
  if (score < 0.34) return 'Low'
  if (score < 0.67) return 'Medium'
  return 'High'
}

function Meter({ label, score, reasons }) {
  return (
    <div className="mb-4">
      <p className="flex justify-between font-semibold">
        <span>{label}</span>
        <span>{level(score)}</span>
      </p>
      <div className="h-3 bg-line my-1" role="img" aria-label={`${label}: ${level(score)}`}>
        <div className="h-3 bg-teal" style={{ width: `${Math.max(Math.round(score * 100), score ? 4 : 0)}%` }} />
      </div>
      <div className="flex flex-wrap gap-1.5">
        {reasons.map((r) => (
          <span key={r} className="border-2 border-teal px-2 text-xs font-semibold">{r}</span>
        ))}
      </div>
    </div>
  )
}

export default function CredibilitySection({ status, error, data }) {
  const cb = data?.clickbait
  const em = data?.emotional_language
  const src = data?.source_context
  const cbReasons = cb
    ? [
        ...(cb.matched_phrases ?? []),
        ...(cb.excessive_caps ? ['Excessive capital letters'] : []),
        ...(cb.excessive_punctuation ? ['Excessive punctuation'] : []),
      ]
    : []

  return (
    <ResultCard title="How it is written" status={status} error={error}>
      {data && (
        <>
          <Meter label="Clickbait wording" score={cb.score} reasons={cbReasons} />
          <Meter label="Emotional language" score={em.score} reasons={em.matched_words ?? []} />
          <p className="font-semibold">Source: {src.tier}</p>
          {src.resolved_domain && <p className="text-sm text-teal-soft">{src.resolved_domain}</p>}
          <p className="mt-3 text-sm text-teal-soft">
            Writing-style hints only. They say nothing about whether a claim is true, and a source that is not in our list is not necessarily unreliable.
          </p>
        </>
      )}
    </ResultCard>
  )
}