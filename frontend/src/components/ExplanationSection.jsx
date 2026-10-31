import ResultCard from './ResultCard'

export default function ExplanationSection({ status, error, data }) {
  const evidence = data?.evidence ?? []
  const numberFor = (id) => evidence.findIndex((e) => e.article_id === id) + 1
  const jump = (id) =>
    document.getElementById(`ev-${id}`)?.scrollIntoView({ behavior: 'smooth', block: 'center' })

  return (
    <ResultCard step="2" title="What the articles say" status={status} error={error}>
      {data && data.status === 'grounded' && (
        <>
          <p className="mb-4">
            <span className="bg-teal text-cream px-3 py-1 text-sm font-semibold">
              Based on {evidence.length} source{evidence.length === 1 ? '' : 's'}
            </span>
          </p>
          {data.statements.map((s, i) => (
            <p key={i} className="text-2xl leading-snug mb-3">
              {s.text}{' '}
              {s.evidence_ids.map((id) => (
                <button
                  key={id}
                  type="button"
                  onClick={() => jump(id)}
                  aria-label={`Show source ${numberFor(id)}`}
                  className="align-middle border-2 border-teal px-2 text-sm font-semibold hover:bg-teal hover:text-cream"
                >
                  {numberFor(id)}
                </button>
              ))}
            </p>
          ))}
          <p className="mt-4 text-sm text-teal-soft">{data.uncertainty}</p>
        </>
      )}
      {data && data.status !== 'grounded' && (
        <>
          <p className="mb-3">
            <span className="border-2 border-teal px-3 py-1 text-sm font-semibold">Not enough evidence</span>
          </p>
          <p className="text-lg">{data.uncertainty}</p>
        </>
      )}
      {data && <p className="mt-4 text-sm text-teal-soft">{data.disclaimer}</p>}
    </ResultCard>
  )
}