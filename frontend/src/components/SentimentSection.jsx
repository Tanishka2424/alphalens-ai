import ResultCard from './ResultCard'

const STYLE = {
  Bullish: { sign: '▲', cls: 'bg-up text-up-ink' },
  Bearish: { sign: '▼', cls: 'bg-down text-down-ink' },
  Neutral: { sign: '●', cls: 'bg-line text-teal' },
}

export default function SentimentSection({ status, error, data }) {
  const s = data ? STYLE[data.label] : null
  return (
    <ResultCard title="Market tone" status={status} error={error}>
      {data && s && (
        <>
          <p className={`inline-flex items-center gap-3 px-5 py-2 font-display text-4xl uppercase tracking-wide ${s.cls}`}>
            <span aria-hidden="true">{s.sign}</span>
            {data.label}
          </p>
          <p className="mt-3 text-sm text-teal-soft">
            Bullish {data.scores.Bullish?.toFixed(2)} · Bearish {data.scores.Bearish?.toFixed(2)} · Neutral {data.scores.Neutral?.toFixed(2)}
          </p>
          <p className="mt-1 text-sm text-teal-soft">
            Read by FinBERT. These are model scores, not probabilities.
          </p>
        </>
      )}
    </ResultCard>
  )
}