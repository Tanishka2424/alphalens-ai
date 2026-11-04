import { fmtDate, isLink } from '../format'
import ResultCard from './ResultCard'

export default function EvidenceSection({ status, error, data }) {
  if (status === 'done' && (!data || data.evidence.length === 0)) return null

  return (
    <ResultCard step="3" title="Where it came from" status={status} error={error}>
      <ol>
        {data?.evidence.map((e, i) => (
          <li key={e.article_id} id={`ev-${e.article_id}`} className="flex gap-4 py-4 border-t-2 border-teal first:border-t-0">
            <span className="font-display text-5xl leading-none">{i + 1}</span>
            <div>
              <p className="font-semibold">{e.title}</p>
              <p className="text-sm text-teal-soft">
                {e.source || 'Unknown source'} · {fmtDate(e.published_at)} · similarity {e.similarity_score.toFixed(2)}
              </p>
              {isLink(e.url) ? (
                <a href={e.url} target="_blank" rel="noreferrer" className="inline-block mt-2 bg-teal text-cream px-4 py-2 text-sm font-semibold">
                  Read the original
                </a>
              ) : (
                <p className="mt-2 text-sm">No link available for this item.</p>
              )}
            </div>
          </li>
        ))}
      </ol>
    </ResultCard>
  )
}